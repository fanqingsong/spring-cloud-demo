# 第 24 课 · Spring 官方云原生栈

## 学习目标

- 使用 **Spring Cloud Config** 集中管理配置，并 **`@RefreshScope` 热更新**
- 搭建 **Spring Authorization Server**，用 **JWT** 保护 Gateway 与 Provider
- 集成 **Micrometer Tracing + Zipkin** 做分布式链路追踪
- 用 **Spring Cloud Stream + Kafka** 实现异步消息
- 使用 **SpringDoc** 生成 OpenAPI 文档

## 本课讲什么

在 `spring-cloud-23`（Eureka + Gateway + Feign + 熔断）之上，本课补齐企业里常见的 **Spring 官方** 能力：配置中心、统一认证、可观测性、消息驱动。这是「第二季」综合实战，适合在掌握 02–23 课后学习。

## 如何实现（要点）

| 能力 | 实现方式 |
|------|----------|
| 配置中心 | `spring-cloud-config-server-24` + Native `config-repo`；客户端 `spring.config.import=configserver:...` |
| 动态刷新 | `@RefreshScope` + `DemoConfigProperties`；`POST /actuator/refresh` |
| 认证授权 | `spring-cloud-auth-server-24` 签发 JWT；Gateway/Provider `oauth2ResourceServer().jwt()` |
| 服务间调用 | Consumer `oauth2-client` + `spring.cloud.openfeign.oauth2.enabled=true` |
| 网关 | `spring.cloud.gateway.routes` + JWT 校验（WebFlux Security） |
| 追踪 | `micrometer-tracing-bridge-brave` + `management.zipkin.tracing.endpoint` |
| 消息 | `StreamBridge` 发送、`Consumer<String>` 函数式消费；Kafka `localhost:9092` |
| API 文档 | `springdoc-openapi-starter-webmvc-ui` on Provider |

---

## 模块说明

| 模块 | 端口 | 说明 |
| --- | --- | --- |
| `spring-cloud-config-server-24` | 8888 | **Spring Cloud Config**（Native 配置仓库） |
| `spring-cloud-service-24` | 8761 | Eureka 注册中心 |
| `spring-cloud-auth-server-24` | 9000 | **Spring Authorization Server**（JWT） |
| `spring-cloud-provider-24` | 7778 | 配置客户端 + OAuth2 Resource Server + 链路追踪 + OpenAPI |
| `spring-cloud-consumer-24` | 7779 | OpenFeign + OAuth2 Client + 熔断 |
| `spring-cloud-gateway-24` | 9876 | Gateway + JWT 校验 + 路由 |
| `spring-cloud-stream-24` | 7780 | **Spring Cloud Stream** + Kafka |

## 启动顺序

1. **Docker 一键启动（推荐）**：在本课目录执行 `docker compose up --build -d`，会同时启动 Zipkin、Kafka 与全部 Java 模块（详见下文「Docker 一键启动」）。

2. **本地 IDE / Maven 启动**：先 `docker compose up -d zipkin kafka`，再按 Config Server → Eureka → Auth Server → Provider → Consumer → Gateway → Stream 顺序启动；编译：`mvn -pl spring-cloud-24 -am compile`

## 快速验证

### 1. 配置中心

Provider 启动后访问（需 JWT，见下）或查看日志中的 `demo.welcome` 是否来自 Config Server。

动态刷新：修改 `config-server` 内 `config-repo/spring-cloud-provider.properties` 后：

```bash
curl -X POST http://localhost:7778/actuator/refresh
```

### 2. OAuth2 Token（客户端凭证）

```bash
curl -s -u 'demo-client:demo-secret' \
  -d 'grant_type=client_credentials&scope=api.read' \
  http://localhost:9000/oauth2/token
```

将返回的 `access_token` 用于：

```bash
curl -H "Authorization: Bearer <token>" http://localhost:9876/api/user/1
```

### 3. 链路追踪

浏览器打开 [http://localhost:9411](http://localhost:9411)，调用网关接口后查看 Trace。

### 4. Spring Cloud Stream

```bash
curl -X POST 'http://localhost:7780/messages?body=hello-kafka'
```

查看 `spring-cloud-stream-24` 日志中的消费记录。

### 5. OpenAPI

[http://localhost:7778/swagger-ui.html](http://localhost:7778/swagger-ui.html)

## 默认账号

- Eureka：`roncoo` / `123456`
- Config Server：`config` / `config-secret`
- OAuth Client：`demo-client` / `demo-secret`

        ## Docker 一键启动

        本课已提供 **Docker Compose**，无需本地安装 JDK/Maven 即可启动演示（首次会镜像内 Maven 编译，耗时较长）。

        ```bash
        cd spring-cloud-24
        docker compose up --build -d
        ```

        - 查看日志：`docker compose logs -f`
        - 停止：`docker compose down -v`
        - 验证：Zipkin http://localhost:9411；先取 Token（见 README）再访问 Gateway http://localhost:9876；Stream POST http://localhost:7780/messages?body=hi
- Eureka 控制台默认账号：`roncoo` / `123456`

        > 容器内已通过环境变量将 Eureka 地址改为 `eureka`（或第 05 课集群 hostname），并开启 `prefer-ip-address` 以便服务间调用。
