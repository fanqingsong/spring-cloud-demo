# 第 19 课 · 监控聚合与多 Consumer

## 一句话先懂

原视频用 **Netflix Turbine** 把多个服务的 Hystrix 流汇到一块大屏。Hystrix 停更后，那种「一条管道看全站熔断」的组件不再作为本仓库的运行时依赖。本课保留 **turbine 这个模块名和端口**，让你对照视频目录；实际监控走 **Micrometer + Prometheus + Grafana**（`docker compose` 会一并拉起），turbine 进程只是带 Actuator、注册 Eureka 的对照占位。

同时，Consumer 换成了另一个身份：`spring-cloud-consumer2`（端口 8886），用来演示「注册中心上可以同时有多个消费者应用」。

## 学习目标

- 理解「监控聚合」想解决什么：熔断指标散落在每个实例上，运维想看一张总图
- 知道今天业界常用替代是 **Micrometer + Prometheus + Grafana**，而不是 Turbine
- 能在 Eureka 里认出 `spring-cloud-consumer2` 和 `spring-cloud-turbine`
- 会用本课 Docker Compose 里的 **Prometheus / Grafana** 查看各服务的 `/actuator/prometheus` 指标
- 分清 **Actuator / Micrometer / prometheus 依赖 / 暴露端点 / Prometheus 拉取** 各自负责什么，而不是以为「只改 POM 就全自动」

## 本课在整条链路里的位置

18 课是单 Consumer 的 health。本课多一个「监控入口进程」和第二个 Consumer 名字。20 课开始加网关空壳。

---

## 知识点讲解

### 1. 原 Turbine 在干什么（概念仍然有用）

**是什么**

每个开了 Hystrix 的应用会吐一条实时流（谁熔断了、成功率多少）。Turbine 订阅**多个应用名**的流，合并后给 Dashboard 画图。

本课 properties 还留着：

```properties
turbine.app-config=spring-cloud-consumer,spring-cloud-consumer2
```

意思是「请聚合这两个 Consumer」。**当前 POM 没有 Netflix Turbine 依赖**，这行配置不会真的去拉流。读它是为了看懂视频里的字段含义。

**有什么用（概念）**

微服务数量上去之后，你不可能开 20 个 Hystrix Dashboard 来回切。聚合层把「多实例指标」收拢到一个入口。

**现在用什么**

| 层 | 作用 |
|----|------|
| **Actuator** | 健康检查、info、以及（配置后）对外 HTTP 端点；并驱动 Spring Boot 与 Micrometer 的自动装配 |
| **Micrometer** | 应用内统一指标 API；配合 `spring-boot-starter-web` 等会自动采集 JVM、Tomcat、`http.server.requests` 等 |
| **micrometer-registry-prometheus** | 增加 Prometheus 格式 registry，并启用 Actuator 的 `prometheus` 端点（见下节） |
| **Prometheus** | 按配置定时 **拉取（pull）** 各实例的 `/actuator/prometheus` 并存储 |
| **Grafana** | 连 Prometheus 做大盘与告警（本课 Compose 已预置数据源） |

模块 `spring-cloud-turbine-19` 仍保留名称与端口 **9999**，与视频目录对照；**不再**承担 Netflix Turbine 聚合，指标与其它 Spring 服务一样交给 Prometheus 收拢。

本地 Compose 抓取目标见 `docker/prometheus/prometheus.yml`（`provider:7778`、`consumer:8886`、`turbine:9999`）。

### 2. Micrometer 在本课里怎么生效？（不只改 POM）

很多人问：**只依赖 `micrometer-registry-prometheus`，Micrometer 就会自动生效吗？** 要分三层看：**采数**、**注册与格式**、**对外暴露与集群拉取**。

#### 2.1 采数：Actuator 已经在用 Micrometer

本课 provider / consumer / turbine 的 POM 里已有 **`spring-boot-starter-actuator`**。Spring Boot 会自动：

- 装配 **`MeterRegistry`**（指标注册表）
- 绑定多种 **MeterBinder**（JVM 内存/GC、Tomcat、Spring MVC 的 HTTP 请求指标等，有 Web  starter 时 HTTP 指标更明显）

因此：**即使不加** `micrometer-registry-prometheus`，进程内部也已经在用 Micrometer 收集**默认**指标；只是默认未必以 Prometheus 文本格式通过一个 HTTP 地址对外提供。

#### 2.2 注册与格式：`micrometer-registry-prometheus` 多做了什么

该依赖会：

- 注册 **`PrometheusMeterRegistry`**，把 Micrometer 里的指标转成 **Prometheus  exposition 格式**
- 在 classpath 满足条件时，由 Spring Boot 自动配置接上 Actuator 的 **`prometheus` endpoint**（对应路径 **`/actuator/prometheus`**）

它解决的是「**给 Prometheus 拉取用的格式和端点能力**」，不是「从零开启 Micrometer」。

#### 2.3 对外暴露：只加依赖仍可能访问不到

Spring Boot 3 默认**不会**把所有 Actuator 端点都开在 HTTP 上。必须显式暴露 **`prometheus`**，例如本课 **`docker-compose.yml`** 里：

```yaml
MANAGEMENT_ENDPOINTS_WEB_EXPOSURE_INCLUDE: health,info,prometheus
```

等价 properties：

```properties
management.endpoints.web.exposure.include=health,info,prometheus
```

**IDE 或 jar 本地启动、不用 Compose 时**，若没在 properties 里写上述配置，访问 `/actuator/prometheus` 可能 404 或未暴露。Docker 一键启动则已由 Compose 注入环境变量。

#### 2.4 集群侧：Prometheus / Grafana

应用暴露 `/actuator/prometheus` 之后，还需要 **`docker/prometheus/prometheus.yml`**（或自建 Prometheus）配置 **scrape**，Grafana 再连 Prometheus 看图。这是**进程外**的步骤，与 JVM 内 Micrometer 无关。

#### 2.5 本课最小清单（对照检查）

| 步骤 | 本课是否具备 | 作用 |
|------|----------------|------|
| `spring-boot-starter-actuator` | 是（三模块 POM） | Micrometer + 默认 JVM/HTTP 等指标 |
| `micrometer-registry-prometheus` | 是（三模块 POM） | Prometheus 格式 + `prometheus` endpoint |
| 暴露 `prometheus` 端点 | Compose 有；本地需自行写 properties | HTTP 可访问 `/actuator/prometheus` |
| Prometheus scrape | Compose + `docker/prometheus/prometheus.yml` | 定时拉取、存储 |
| 自定义业务指标 | 否（本课未写） | 需 `@Timed`、`MeterRegistry.counter(...)` 等 |

验证整条链：先 `curl http://localhost:8886/user/1` 打几次业务请求，再在 `/actuator/prometheus` 或 Grafana Explore 里查 `http_server_requests_seconds_count` 等是否有变化。

### 3. 多个 Consumer 应用名

**是什么**

到目前为止，调用方一直叫 `spring-cloud-consumer`。本课改成 **`spring-cloud-consumer2`**，并在实例元数据里标 `cluster=RONCOO`：

```properties
eureka.instance.metadata-map.cluster=RONCOO
```

**有什么用**

- 同一套业务可以有「网关后面的 BFF」「给内部用的 Consumer」等多个入口应用
- 旧 Turbine 按应用名和 cluster 过滤要聚合谁
- 元数据本身不改变负载均衡，只是挂在实例上的标签（类似 04 课的 datacenter）

控制台里你**不会**自动看到 `spring-cloud-consumer`，除非再启动一份旧名字的进程。本课演示的是「换一个身份注册」，不是「同时起两个 Consumer 进程」。

### 4. Consumer 端口 8886

`application.properties` 与 **本课 `docker-compose.yml`** 均为 **8886**。业务入口：

- `curl http://localhost:8886/user/1`
- `curl http://localhost:8886/feign/user/1`

业务代码与 18 课同类：RestTemplate 熔断、Feign fallback。Turbine 模块**没有**业务接口。

### 5. Docker 里的 Prometheus + Grafana（动手验证）

Compose 会一并启动 **prometheus**（9090）与 **grafana**（3000，默认 `admin` / `admin`）。

1. 确认指标端点（任选其一）：
   - `curl -s http://localhost:7778/actuator/prometheus | head`
   - `curl -s http://localhost:8886/actuator/prometheus | head`
2. 打开 [Prometheus Targets](http://localhost:9090/targets)，`spring-cloud-19` 下三个 target 应为 **UP**。
3. 打开 [Grafana](http://localhost:3000)，数据源 **Prometheus** 已自动指向 Compose 内的 Prometheus。
4. 在 **Explore** 里试查例如 `jvm_memory_used_bytes`、`http_server_requests_seconds_count`；先打几次 `curl` 业务接口再查 HTTP 指标更明显。

> 端点暴露说明见上文 **§2.3**；Compose 用环境变量，本地启动请在 `application.properties` 写 `management.endpoints.web.exposure.include=health,info,prometheus`。

---

## 模块结构

| 模块 / 组件 | 端口 | 说明 |
|-------------|------|------|
| service-19 | 8761 | Eureka，`spring-cloud-server` |
| provider-19 | 7778 | `spring-cloud-provider`，含 Prometheus 指标 |
| consumer-19 | **8886** | **`spring-cloud-consumer2`**，含 Prometheus 指标 |
| turbine-19 | 9999 | `spring-cloud-turbine`，Actuator 占位，含 Prometheus 指标 |
| prometheus（Compose） | 9090 | 拉取上述三服务的 `/actuator/prometheus` |
| grafana（Compose） | 3000 | 可视化，默认账号 `admin` / `admin` |
| bean / api | — | 同前 |

## 建议启动与验证

**IDE 或 jar 逐个启动**

1. service → provider → consumer → turbine
2. Eureka 应出现 `SPRING-CLOUD-CONSUMER2`、`SPRING-CLOUD-TURBINE`
3. `curl http://localhost:8886/user/1`、`/feign/user/1`
4. `curl http://localhost:9999/actuator/health`
5. 若已自行安装 Prometheus/Grafana：POM 与 **§2.3 暴露端点** 配齐后，再配置 scrape 指向 `/actuator/prometheus`
6. 不要期待视频里的 Turbine 聚合大盘

**推荐：Docker Compose 一键（含 Prometheus + Grafana）** — 见下文。

## 与后续课程

- **第 20 课**：新增 Gateway 进程（9876），本课的 Consumer2 / Turbine 仍会跟着走一会儿

## Docker 一键启动

```bash
cd spring-cloud-19
docker compose up --build -d
```

- 日志：`docker compose logs -f`
- 停止：`docker compose down -v`

| 地址 | 用途 |
|------|------|
| [http://localhost:8761](http://localhost:8761) | Eureka，`roncoo` / `123456` |
| [http://localhost:8886/user/1](http://localhost:8886/user/1) | Consumer 业务 |
| [http://localhost:9999/actuator/health](http://localhost:9999/actuator/health) | Turbine 模块 health |
| [http://localhost:9090/targets](http://localhost:9090/targets) | Prometheus 抓取状态 |
| [http://localhost:3000](http://localhost:3000) | Grafana（`admin` / `admin`） |

监控相关文件：

- `docker/prometheus/prometheus.yml` — scrape 配置
- `docker/grafana/provisioning/datasources/prometheus.yml` — Grafana 默认数据源
