# 第 24 课 · Spring 官方云原生栈

## 一句话先懂

02～23 课把「注册、调用、熔断、大门」走通了。企业里通常还缺四块：**配置不要散落在每个 jar 里、访问要带身份、调用要能画出链路、有些事适合异步发消息**。本课用 Spring **官方**组件一次补齐，作为「第二季」综合实战。

## 学习目标

- 能讲清 Config Server、JWT、链路追踪、消息驱动**各自解决什么痛**
- 会从 Config 拉配置，并用 `@RefreshScope` 理解「改配置不必重启」（本课刷新接口本身可能仍要带 JWT）
- 会用客户端凭证拿 Token，再访问网关
- 能在 Zipkin 里看到一次请求的 trace，能往 Kafka 发一条演示消息

## 本课在整条链路里的位置

建立在 23 课（Eureka + Gateway + Feign）之上。25 课开始用 Nacos 同时扮演「注册中心 + 配置中心」，和本课的 Config Server 是两条产品线，可以对照着学。

---

## 知识点讲解

### 1. 配置中心：把 properties 从 jar 里搬出去

**是什么**

每个服务自己带着一份 `application.properties` 时，改一句欢迎语也要重新打包。**Spring Cloud Config** 起一个 Server，配置文件放在它的 `config-repo`（本课是 classpath 本地文件，生产常接 Git）。客户端启动时用：

```properties
spring.config.import=optional:configserver:http://config:config-secret@localhost:8888
```

按**自己的应用名**去拉 `{application}.properties`，以及所有人共享的 `application.properties`。

**有什么用**

环境差异（dev / 试运行 / 生产）只改仓库，不改代码。运维和开发对同一份配置有据可查。

**动态刷新**

`@RefreshScope` + `@ConfigurationProperties(prefix = "demo")` 表示：这些字段允许在运行中换成新值。改完 Server 里的文件后，再 `POST /actuator/refresh`，Bean 会重建。

注意：本课 Provider 的 Security **只放行了** health / info / Swagger，`/actuator/refresh` 和 `/api/**` 一样需要 **JWT**。README 里若只写一行 curl 而不带 Token，会被 401，这不是刷新坏了。

本课文件与键：

| 文件 | 作用 |
|------|------|
| `application.properties` | 共享：`demo.shared-message` |
| `spring-cloud-provider.properties` | `demo.welcome`（可用来做刷新实验） |
| `spring-cloud-consumer.properties` | Consumer 自己的 welcome |
| `spring-cloud-gateway.properties` | 说明性备注 |

### 2. 认证授权：先证明「你是谁」，再访问 API

**是什么**

**Spring Authorization Server**（9000）发 **JWT**（一段带签名的令牌）。Gateway 和 Provider 配成 **Resource Server**：没带合法 Bearer Token 的请求直接拒绝。

本课演示最简单的机器对机器方式——**客户端凭证**（client_credentials）：

```bash
curl -s -u 'demo-client:demo-secret' \
  -d 'grant_type=client_credentials&scope=api.read' \
  http://localhost:9000/oauth2/token
```

把返回的 `access_token` 放到：

```bash
curl -H "Authorization: Bearer <token>" http://localhost:9876/api/user/1
```

Consumer 调 Provider 时打开了 `spring.cloud.openfeign.oauth2.enabled=true`，Feign 会自动要 Token 再出站，避免你在业务代码里手写 Header。

**有什么用**

网关统一验票，后面的服务可以信「到我这的请求已经过安检」。比 22 课那个写死的 `token=roncoo` 更接近真实 OAuth2。

授权码登录页另有演示用户 `user` / `password`，本课验证以客户端凭证为主即可。

### 3. 链路追踪：一次请求在哪些服务里待过

**是什么**

一次 `9876/api/user/1` 会经过 Gateway → Provider；走 `9876/feign/user/1` 还会再经过 Consumer 的 Feign。出了问题你要在三份日志里用肉眼对时间戳。**链路追踪**给这次调用发一个全局 **traceId**，每个服务再打自己的 **span**（这一跳花了多久、调了谁），最后报到 **Zipkin**（9411），网页上画成一条时间轴。

本课采样率 `1.0`（每条都报），方便学习。生产常降到 `0.1` 以下以免打爆收集器。

**有什么用**

慢在网关还是慢在 Provider、Feign 有没有丢掉某一跳，看图比看日志快。同一 `traceId` 也能把各服务日志对上。

**本课怎么实现（没有手写 Tracing 代码）**

业务类里找不到 `@NewSpan`、`Tracer` 或 Filter。Spring Boot 3 用 **Micrometer Observation** 做统一埋点，再用 **Brave** 当 Tracer、**Zipkin Reporter** 把 span 推出去。旧课里的 **Spring Cloud Sleuth** 已从 Spring Cloud 2022+ 移除，本仓库用这套官方替代。

分五层看：**谁接入、依赖各干什么、如何自动埋点、跨服务如何串同一条 trace、如何报到 Zipkin**。

#### 3.1 谁接入了

| 模块 | 是否接入 | 原因 |
|------|----------|------|
| `gateway-24` / `provider-24` / `consumer-24` | 是 | POM 有 Brave + Zipkin Reporter，properties 指向 Zipkin |
| `stream-24` | 否 | 只演示 Kafka，没有 tracing 依赖 |
| Config / Eureka / Auth | 否 | 不在本次 HTTP 调用链的「画图」范围里 |

Compose 里只给上面三个 Java 服务注入了 `MANAGEMENT_ZIPKIN_TRACING_ENDPOINT`。

#### 3.2 依赖：两块 jar 各干什么

三个接入模块的 POM 都有 Actuator，再加上：

```xml
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-tracing-bridge-brave</artifactId>
</dependency>
<dependency>
    <groupId>io.zipkin.reporter2</groupId>
    <artifactId>zipkin-reporter-brave</artifactId>
</dependency>
```

| 依赖 | 作用 |
|------|------|
| `spring-boot-starter-actuator` | 打开 Observation / Tracing 自动装配（`ZipkinAutoConfiguration` 等在 Actuator 自动配置里） |
| `micrometer-tracing-bridge-brave` | 把 Observation 桥到 **Brave**：生成 `traceId` / `spanId`、读写传播头 |
| `zipkin-reporter-brave` | 把结束的 span **HTTP POST** 到 Zipkin 的 `/api/v2/spans` |

只加第一块：进程内会有 Observation，但没有 Tracer，Zipkin 里什么都没有。只加 Brave、不加 Reporter：本地有 ID、日志能对上，但 UI 收不到。版本由 Spring Boot BOM 管理，不必手写。

#### 3.3 自动埋点：Observation 何时开 span

classpath 满足后，Boot / Cloud 自动挂过滤器，业务代码不用改：

| 场景 | 谁开 span | 本课对应 |
|------|-----------|----------|
| 入站 HTTP | MVC 的 `ServerHttpObservationFilter`，Gateway（WebFlux）的 Observation WebFilter | Provider、Consumer 收请求；Gateway 收浏览器/curl |
| 出站 HTTP | Gateway 转发、OpenFeign 拦截器 | Gateway → 下游；Consumer Feign → Provider |

一次入站是一个 **server span**，再往下调用是 **client span**。Zipkin 里同一 `traceId` 下会看到父子关系。Provider 的 `log.info("provider find id=...")` 本身不是埋点，只是业务日志；有了 tracing 后，默认控制台格式会带上 `[应用名,traceId,spanId]`，便于和 Zipkin 对号。

#### 3.4 跨服务如何串成同一条 trace

关键不是「每个服务自己造一个 ID」，而是**下游必须读到上游传来的 ID**。

Brave 在出站请求上注入传播头，入站再解析。Spring Boot 3 默认 **W3C Trace Context**（头名 `traceparent`），也可改 B3：

```properties
# 默认就是 w3c；要看旧式头可改成 b3
management.tracing.propagation.type=w3c
```

`traceparent` 形态类似 `00-{32位traceId}-{16位spanId}-{flag}`。Gateway 把当前 span 写成这个头再转给 Provider / Consumer；下游抽出同一个 `traceId`，再开自己的子 span。用 `curl -v` 打到网关时，请求里还没有这个头——**根 span 由 Gateway 创建**；你看到的传播发生在**服务之间**。

两条演示路径：

```mermaid
sequenceDiagram
    participant Client as curl
    participant GW as Gateway 9876
    participant C as Consumer 7779
    participant P as Provider 7778
    participant Z as Zipkin 9411

    Client->>GW: GET /api/user/1 + JWT
    Note over GW: 生成 traceId，开根 span
    GW->>P: 注入 traceparent
    P-->>GW: User
    GW-->>Client: User
    GW-->>Z: 上报 span
    P-->>Z: 上报 span

    Client->>GW: GET /feign/user/1 + JWT
    GW->>C: 同一套传播头
    C->>P: Feign 继续带同一 traceId
    P-->>C: User
    C-->>GW: User
    GW-->>Z: 上报
    C-->>Z: 上报
    P-->>Z: 上报
```

- `GET /api/user/1`：Zipkin 上常见 **Gateway + Provider**（两跳）
- `GET /feign/user/1`：常见 **Gateway + Consumer + Provider**（三跳）

Auth 校验 JWT 在网关本地完成，**不会**在 Zipkin 里多出 `auth-server` 这一跳（Auth 模块也没接 tracing）。

#### 3.5 配置：采样与上报地址

三个接入模块的 `application.properties` 相同：

```properties
management.tracing.sampling.probability=1.0
management.zipkin.tracing.endpoint=http://localhost:9411/api/v2/spans
```

| 配置 | 含义 |
|------|------|
| `management.tracing.sampling.probability` | `1.0` = 100% 采样，学习时每条请求都进 Zipkin；生产常 `0.1` 或更低 |
| `management.zipkin.tracing.endpoint` | Brave Reporter 的 POST 地址；服务名用 `spring.application.name`，所以 UI 里是 `spring-cloud-gateway` 等 |

IDE 本地启动：Zipkin 在本机 `9411`，用上面的 `localhost` 即可。Compose 里容器不能写 `localhost`（那是容器自己），所以覆盖为：

```yaml
MANAGEMENT_ZIPKIN_TRACING_ENDPOINT: "http://zipkin:9411/api/v2/spans"
```

Zipkin 本身在 `docker-compose.yml` 的 `zipkin` 服务，镜像 `openzipkin/zipkin:3.4`，端口 **9411**。应用是 **推送（push）** span，和 19 课 Prometheus **拉取**指标方向相反。

#### 3.6 最小清单（对照检查）

| 步骤 | 本课是否具备 | 作用 |
|------|----------------|------|
| `spring-boot-starter-actuator` | 是（三模块） | Observation / Tracing 自动装配入口 |
| `micrometer-tracing-bridge-brave` | 是（三模块） | 真正的 Tracer 与传播头 |
| `zipkin-reporter-brave` | 是（三模块） | 把 span 推到 Zipkin |
| 采样率 + endpoint | 是（properties；Compose 改 host） | 决定报不报、报到哪 |
| Zipkin 进程 | Compose 的 `zipkin` 服务 | 收集并画时间轴 |
| 业务代码埋点 | 否 | HTTP / Feign / Gateway 已自动埋；自定义 span 需再写 `Observation` / `Tracer` |

### 4. Spring Cloud Stream + Kafka：能异步就别卡着 HTTP

**是什么**

不是所有事都要同步等返回。「发一张优惠券、记一条审计」更适合丢进消息队列。本课 `spring-cloud-stream-24` **不连 Eureka**：

- `POST /messages?body=hello-kafka` 用 `StreamBridge` 发到主题 `demo-topic`
- `demoConsumer` 函数式 Bean 从同一主题消费并打日志

**有什么用**

发送方不用管接收方是否在线（在 Kafka 还活着的前提下）。这和 RestTemplate「对方必须立刻 200」是两种编程模型。

### 5. SpringDoc：给 Provider 自动出说明书

访问 [http://localhost:7778/swagger-ui.html](http://localhost:7778/swagger-ui.html) 可试 REST。文档来自代码注解，减少「接口文档和实现各写各的」。Swagger 在本课安全配置里通常免登录，便于点一点；业务 `/api/**` 仍要 JWT。

OpenFeign 打开了 circuitbreaker 开关，但**没有**像 26 课那样的 fallback 类，停 Provider 时不要期待友好 JSON。

---

## 模块说明

| 模块 | 端口 | 说明 |
|------|------|------|
| Zipkin（Compose） | 9411 | 链路 UI |
| Kafka（Compose） | 9092 | 消息 |
| `config-server-24` | 8888 | Native 配置仓库 |
| `service-24` | 8761 | Eureka |
| `auth-server-24` | 9000 | 发 JWT |
| `provider-24` | 7778 | 资源服务器 + 配置客户端 + OpenAPI |
| `consumer-24` | 7779 | Feign + OAuth2 Client |
| `gateway-24` | 9876 | ` /api/**`、`/feign/**` + JWT |
| `stream-24` | 7780 | Kafka 演示 |
| api / bean | — | Feign 与模型 |

路由与 23 课相同：`/api/**` → Provider，`/feign/**` → Consumer，但大门本身要验 JWT。

## 启动顺序

1. **推荐**：本课目录 `docker compose up --build -d`（含 Zipkin、Kafka 和全部 Java 模块）
2. 本地 IDE：先 `docker compose up -d zipkin kafka`，再 Config → Eureka → Auth → Provider → Consumer → Gateway → Stream  
   `mvn -pl spring-cloud-24 -am compile`

## 快速验证

### 1. 拿 Token 再走网关

```bash
curl -s -u 'demo-client:demo-secret' \
  -d 'grant_type=client_credentials&scope=api.read' \
  http://localhost:9000/oauth2/token
```

把返回的 `access_token` 填到下面两条请求里：

```bash
curl -s -H "Authorization: Bearer <token>" http://localhost:9876/api/user/1
curl -s -H "Authorization: Bearer <token>" http://localhost:9876/feign/user/1
```

直连 Consumer（7779）通常**没有** Resource Server，可作对照：

```bash
curl -s http://localhost:7779/feign/user/1
```

Provider 的 `/api/user/config/demo` 能看到来自 Config 的 welcome / sharedMessage，**需要 JWT**：

```bash
curl -s -H "Authorization: Bearer <token>" http://localhost:7778/api/user/config/demo
```

### 2. 刷新配置

先拿 Token，并记下当前配置：

```bash
curl -s -u 'demo-client:demo-secret' \
  -d 'grant_type=client_credentials&scope=api.read' \
  http://localhost:9000/oauth2/token

curl -s -H "Authorization: Bearer <token>" http://localhost:7778/api/user/config/demo
```

改 `spring-cloud-config-server-24/src/main/resources/config-repo/spring-cloud-provider.properties` 里的 `demo.welcome`，例如改成：

```properties
demo.welcome=Provider 配置已热更新
```

Compose 下配置打在镜像里，改完要重建 Config Server 后，再带 Token 刷新并回读：

```bash
docker compose up --build -d config-server

curl -s -X POST -H "Authorization: Bearer <token>" http://localhost:7778/actuator/refresh

curl -s -H "Authorization: Bearer <token>" http://localhost:7778/api/user/config/demo
```

本地 IDE 启动时，改完文件后重启 Config Server，再执行上面两条 curl（不必 `docker compose up`）。`welcome` 应变为新文案。`/actuator/refresh` 不带 Token 会 401。

### 3. Zipkin

```bash
curl -s -u 'demo-client:demo-secret' \
  -d 'grant_type=client_credentials&scope=api.read' \
  http://localhost:9000/oauth2/token
```

把返回的 `access_token` 填到下面两条请求里（都会进同一套追踪）：

```bash
curl -s -H "Authorization: Bearer <token>" http://localhost:9876/api/user/1
curl -s -H "Authorization: Bearer <token>" http://localhost:9876/feign/user/1
```

对照 Provider 日志里的 `[spring-cloud-provider,<traceId>,<spanId>]`：

```bash
docker compose logs provider | grep "provider find"
```

打开 [http://localhost:9411](http://localhost:9411)：

1. 左上 **Run Query**（可先在 Service Name 选 `spring-cloud-gateway`）
2. 点开一条 trace：`/api/user/1` 应能看到 Gateway → Provider；`/feign/user/1` 还应多一跳 Consumer
3. Zipkin 顶部的 Trace ID 应与上面日志里的 `traceId` 一致

若 UI 为空：先确认这次调用是 **200**（401 往往在网关就被拒，下游没有 span）；再确认 Zipkin 已起、Compose 里三个服务的 endpoint 指向 `http://zipkin:9411/api/v2/spans`：

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:9411
docker compose ps zipkin gateway provider consumer
```

### 4. Stream

```bash
curl -s -X POST 'http://localhost:7780/messages?body=hello-kafka'
```

看 `stream` 容器日志是否打印 `Spring Cloud Stream 收到消息: hello-kafka`：

```bash
docker compose logs -f --tail=50 stream
```

## 默认账号

| 组件 | 用户名 | 密码 |
|------|--------|------|
| Eureka | `roncoo` | `123456` |
| Config Server | `config` | `config-secret` |
| OAuth 客户端 | `demo-client` | `demo-secret` |
| 授权码登录页 | `user` | `password` |

## Docker 一键启动

```bash
cd spring-cloud-24
docker compose up --build -d
```

- 日志：`docker compose logs -f`
- 停止：`docker compose down -v`
- 验证：Zipkin 9411；先取 Token 再访问 9876；Stream POST 7780
