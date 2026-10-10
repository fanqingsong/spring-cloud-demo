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

一次 `9876/api/user/1` 会经过 Gateway → Provider。出了问题你要在三份日志里用肉眼对时间戳。**Micrometer Tracing + Zipkin** 给这次调用发一个 **traceId**，每个服务打点后报到 Zipkin（9411），网页上画成一条时间轴。

本课采样率 `1.0`（每条都报），方便学习。生产常降到 0.1 以下以免打爆收集器。

**有什么用**

慢在网关还是慢在 Provider、有没有丢掉某一跳，看图比看日志快。

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

见上文 curl。再试 `GET http://localhost:9876/feign/user/1`。

直连 Consumer（7779）通常**没有** Resource Server，可作对照。Provider 的 `GET /api/user/config/demo` 能看到来自 Config 的 welcome / sharedMessage，**需要 JWT**。

### 2. 刷新配置

改 `config-repo/spring-cloud-provider.properties` 后，带 Token 调用 `POST http://localhost:7778/actuator/refresh`，再读 `/api/user/config/demo`。

### 3. Zipkin

打开 [http://localhost:9411](http://localhost:9411)，先成功调一次网关，再搜 trace。

### 4. Stream

```bash
curl -X POST 'http://localhost:7780/messages?body=hello-kafka'
```

看 `stream-24` 容器日志是否打印消费内容。

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
