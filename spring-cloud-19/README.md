# 第 19 课 · 监控聚合与多 Consumer

## 一句话先懂

原视频用 **Netflix Turbine** 把多个服务的 Hystrix 流汇到一块大屏。Hystrix 停更后，那种「一条管道看全站熔断」的组件不再作为本仓库的运行时依赖。本课保留 **turbine 这个模块名和端口**，让你对照视频目录，但跑起来它只是一个挂了 Actuator、并注册到 Eureka 的普通进程。

同时，Consumer 换成了另一个身份：`spring-cloud-consumer2`（端口 8886），用来演示「注册中心上可以同时有多个消费者应用」。

## 学习目标

- 理解「监控聚合」想解决什么：熔断指标散落在每个实例上，运维想看一张总图
- 知道今天业界常用替代是 **Micrometer + Prometheus + Grafana**，而不是 Turbine
- 能在 Eureka 里认出 `spring-cloud-consumer2` 和 `spring-cloud-turbine`
- 注意本课 **properties 端口是 8886**，部分 Compose 文件曾映射成 8888——以进程真实监听端口为准

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

每个应用的 Actuator 暴露 Prometheus 格式指标，由 Prometheus 按时来拉，Grafana 做图。这是官方和社区都还在演进的路。模块 `spring-cloud-turbine-19` 只提供 `/actuator/health`，端口 **9999**。

### 2. 多个 Consumer 应用名

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

### 3. 端口 8886 vs 8888

`application.properties` 写的是 **8886**。若 Docker Compose 只映射了 `8888:8888` 又没改 `SERVER_PORT`，容器内仍听 8886，宿主机 8888 会连不上。遇到这种情况：

- 看启动日志里的 `Tomcat started on port`
- 或直接 `curl http://localhost:8886/user/1`

20 课 Compose 已按 8886 对齐，本课若发现不一致，以日志为准。

业务代码与 18 课同类：RestTemplate 熔断、Feign fallback。Turbine 模块**没有**业务接口。

---

## 模块结构

| 模块 | 端口 | 应用名 |
|------|------|--------|
| service-19 | 8761 | `spring-cloud-server` |
| provider-19 | 7778 | `spring-cloud-provider` |
| consumer-19 | **8886** | **`spring-cloud-consumer2`** |
| turbine-19 | 9999 | `spring-cloud-turbine` |
| bean / api | — | 同前 |

## 建议启动与验证

1. service → provider → consumer → turbine
2. Eureka 应出现 `SPRING-CLOUD-CONSUMER2`、`SPRING-CLOUD-TURBINE`
3. `curl http://localhost:8886/user/1`、`/feign/user/1`
4. `curl http://localhost:9999/actuator/health`
5. 不要期待视频里的 Turbine 聚合大盘

## 与后续课程

- **第 20 课**：新增 Gateway 进程（9876），本课的 Consumer2 / Turbine 仍会跟着走一会儿

## Docker 一键启动

```bash
cd spring-cloud-19
docker compose up --build -d
```

- 日志：`docker compose logs -f`
- 停止：`docker compose down -v`
- 验证：先看 Consumer 实际端口再 curl；Turbine health 在 9999
- Eureka：[http://localhost:8761](http://localhost:8761)，`roncoo` / `123456`
