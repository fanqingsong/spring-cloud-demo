# 第 23 课 · 网关路由与 OpenFeign 熔断

## 一句话先懂

这是 Netflix 老栈（Zuul + Ribbon + Hystrix + Turbine）在本仓库里的**完整现代化对照**：Gateway 转发、LoadBalancer 选实例、Resilience4j 熔断、Turbine 模块仅作 Actuator 占位。

本课第一次让你只记一个地址 **9876**，就能调到 Provider 和 Consumer。

## 学习目标

- 读懂 `spring.cloud.gateway.routes`：谓词（谁匹配）+ `uri`（转到哪）
- 理解 `lb://服务名`：网关自己也做客户端发现，不写死下游 IP
- 会走两条教学链路：大门 → Provider；大门 → Consumer → Feign → Provider
- 打开 `spring.cloud.openfeign.circuitbreaker.enabled=true`，并会用停进程验证 RestTemplate / Feign 两种兜底

## 本课在整条链路里的位置

02～22 的能力在这里收口。24 课换「官方云原生加餐」（配置中心、JWT、Zipkin、Kafka）。25 课起用 Nacos 再走一遍注册与网关。

---

## 知识点讲解

### 1. 路由：大门上的路牌

**是什么**

```properties
spring.cloud.gateway.routes[0].id=provider1
spring.cloud.gateway.routes[0].uri=lb://spring-cloud-provider
spring.cloud.gateway.routes[0].predicates[0]=Path=/api/**

spring.cloud.gateway.routes[1].id=consumer1
spring.cloud.gateway.routes[1].uri=lb://spring-cloud-consumer
spring.cloud.gateway.routes[1].predicates[0]=Path=/feign/**
```

| 字段 | 含义 |
|------|------|
| `id` | 这条规则的名字，仅便于日志 |
| `predicates` | 什么请求命中这条规则。`Path=/api/**` 表示路径以此开头 |
| `uri=lb://...` | 命中后转给 Eureka 里该**服务名**下的某实例 |

**有什么用**

调用方不再记住 7778 / 8888。网关根据路径把「资源型 API」和「经过 Consumer 的 Feign 演示」分开。下游扩容只改注册表，路牌不用改。

**生活类比**

前台墙上两行字：「找档案室 → 走 /api；找已经封装好的客服台 → 走 /feign」。`lb://` 表示「档案室今天在几号工位，查内部通讯录」。

本课 Consumer **改回** 应用名 `spring-cloud-consumer`、端口 **8888**（20/22 课曾用 consumer2 / 8886）。路牌上的名字必须和它一致。

### 2. 两条调用链（务必分清）

```text
浏览器  GET :9876/api/user/1
    → Gateway 匹配 /api/**
    → 直接转发到 Provider 的 /api/user/1

浏览器  GET :9876/feign/user/1
    → Gateway 匹配 /feign/**
    → 转发到 Consumer 的 /feign/user/1
    → Consumer 再用 Feign 调 Provider /api/user/{id}
```

第二条链路上有**两次**跳转。停 Provider 时：

- 第一条：网关会报下游错误（网关本身本课没配 fallback）
- 第二条：Consumer 的 Feign fallback 可以返回 `"system error"`

### 3. OpenFeign circuitbreaker 开关

```properties
spring.cloud.openfeign.circuitbreaker.enabled=true
```

**是什么**

让 Feign 调用包进 CircuitBreaker。配合已有的 `RcFeignFallback`，失败和熔断打开时走降级类。

RestTemplate 仍用 `@CircuitBreaker` + `"自定义信息"`。两种保护可以同时开，互不影响。

Token 过滤器本课写了 `gateway.token-filter.enabled=false`。想复现 22 课门卫，改成 true 后带 Header `token: roncoo`。

网关还配了较长的 `httpclient` 超时，避免教学时一点抖动就断。`logging.level.org.springframework.cloud.loadbalancer=debug` 可在日志里看见选了哪台实例。

Turbine 仍是 9999 的 Actuator 占位，没有聚合大盘。

---

## 模块结构

| 模块 | 端口 | 应用名 |
|------|------|--------|
| service-23 | 8761 | `spring-cloud-server` |
| provider-23 | 7778 | `spring-cloud-provider` |
| consumer-23 | 8888 | `spring-cloud-consumer` |
| gateway-23 | 9876 | `spring-cloud-gateway` |
| turbine-23 | 9999 | 占位 |
| bean / api | — | 契约与 Feign |

## 建议启动与验证

```bash
# 经网关
curl http://localhost:9876/api/user/1
curl http://localhost:9876/feign/user/1

# 直连对照
curl http://localhost:8888/user/1
curl http://localhost:8888/feign/user/1

# 停 Provider 后
curl http://localhost:8888/user/1          # 自定义信息
curl http://localhost:8888/feign/user/1    # system error
```

编译：`mvn -pl spring-cloud-23 -am compile`

## 与后续课程

- **第 24 课**：Config、Authorization Server / JWT、Zipkin、Stream / Kafka
- **第 26 课**：同一套「网关 + Feign」换 Nacos 当注册中心

## Docker 一键启动

```bash
cd spring-cloud-23
docker compose up --build -d
```

- 日志：`docker compose logs -f`
- 停止：`docker compose down -v`
- 验证：`curl http://localhost:9876/api/user/1`
- Eureka：[http://localhost:8761](http://localhost:8761)，`roncoo` / `123456`
