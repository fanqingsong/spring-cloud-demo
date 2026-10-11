# 第 22 课 · 网关过滤器与 Feign 降级

## 一句话先懂

大门（20 课）已经在了。本课给大门加一个**门卫**：请求头里必须带 `token=roncoo`，否则 401。门卫已打开（`gateway.token-filter.enabled=true`）。

另一条线在 Consumer：Feign 接口指定 **fallback 实现类**，Provider 挂了返回兜底，而不是把异常甩给用户。

路由表也已补上：`/feign/**`、`/user/**` 转到 Consumer，`/api/**` 转到 Provider。先过门卫，再按路牌转发。

## 学习目标

- 理解 Gateway **GlobalFilter**：命中路由的请求会经过，类似 Zuul 的 PreFilter
- 会用配置开关 `gateway.token-filter.enabled` 控制过滤器是否生效
- 读懂 `Path=/feign/** → lb://spring-cloud-consumer2`：路牌和门卫是两件事
- 理解 Feign `fallback`：接口的「备用实现」，必须是 Spring Bean
- 能停 Provider 后从 `/feign/user/{id}` 看到 `"system error"` 一类兜底

## 本课在整条链路里的位置

20 课空壳大门 → 本课门卫 + 路牌 + Feign fallback（已开 circuitbreaker）→ 23 课把 Consumer 应用名改回 `spring-cloud-consumer`，并走完整熔断演示。

---

## 知识点讲解

### 1. GlobalFilter：网关的统一前置逻辑

**是什么**

`TokenGlobalFilter` 实现 `GlobalFilter` + `Ordered`。请求**命中某条路由后**、转发到下游前，先看 Header `token` 是否等于 `roncoo`。不对就返回 **401**，body 为 `token is error`。

```java
@ConditionalOnProperty(name = "gateway.token-filter.enabled", havingValue = "true")
```

只有显式写成 `true` 时，这个 Bean 才存在。本课已打开：

```properties
gateway.token-filter.enabled=true
```

**GlobalFilter 只对匹配到路由的请求生效。** 没有路牌时，带不带 token 都是 404，门卫根本轮不到上场。这就是之前 `curl :9876/feign/user/1` 一直 404 的原因。

**有什么用**

登录校验、租户识别、打印 traceId，都适合放在网关做一次，避免每个微服务复制一份。它不管「转发到哪」，只管家规。

**生活类比**

前台先查工牌，再按墙上的办公室地图带你进楼。查工牌的人（Filter）和地图（routes）不是同一张纸，但**没有地图时前台不会放人进去**，你只会听到「这个房间不存在」。

```bash
# 没 token / token 错 → 401 token is error
curl -i http://localhost:9876/feign/user/1

# token 正确 → User JSON
curl -H "token: roncoo" http://localhost:9876/feign/user/1
```

`token: roncoo` 和 `token:roncoo` 都可以。

### 2. 路由：大门上的路牌

```properties
spring.cloud.gateway.routes[0].uri=lb://spring-cloud-provider
spring.cloud.gateway.routes[0].predicates[0]=Path=/api/**

spring.cloud.gateway.routes[1].uri=lb://spring-cloud-consumer2
spring.cloud.gateway.routes[1].predicates[0]=Path=/feign/**

spring.cloud.gateway.routes[2].uri=lb://spring-cloud-consumer2
spring.cloud.gateway.routes[2].predicates[0]=Path=/user/**
```

Consumer 应用名仍是 `spring-cloud-consumer2`，端口 **8886**。`lb://` 后面必须和 Eureka 里的名字一致。

```text
浏览器  GET :9876/feign/user/1   Header token: roncoo
    → Gateway 门卫校验 token
    → 匹配 /feign/** → Consumer :8886/feign/user/1
    → Consumer 再用 Feign 调 Provider /api/user/{id}

浏览器  GET :9876/api/user/1     Header token: roncoo
    → Gateway 门卫校验 token
    → 匹配 /api/** → Provider :7778/api/user/1
```

经 9876 调业务接口**必须带 token**。直连 8886 / 7778 不经过门卫。

### 3. Feign fallback 类

**是什么**

```java
@FeignClient(value = "spring-cloud-provider", fallback = RcFeignFallback.class)
```

`RcFeignFallback` 实现同一个 `IUserBiz`，在真实 HTTP 失败或熔断打开时被调用。`view1` 一类方法会返回 `"system error"`。类上要有 `@Component`（或等价注册），否则 Feign 找不到备用实现。

**有什么用**

和 14 课 RestTemplate 的 `fallbackMethod` 是同一目的、两种写法：

| 调用方式 | 兜底怎么写 | 本课对外入口 | 停 Provider 后 |
|----------|------------|--------------|----------------|
| RestTemplate | 同类里的方法 | `GET /user/{id}` | `"自定义信息"` |
| Feign | 独立实现类 | `GET /feign/user/{id}` | `"system error"` |

本课已打开 `spring.cloud.openfeign.circuitbreaker.enabled=true`。只写 `fallback=` 不够，必须把 Feign 包进 CircuitBreaker，失败和「Eureka 里没有 Provider 实例」才会走 `RcFeignFallback`。没开这个开关时，Consumer 会直接 500（`Load balancer does not contain an instance`）。

验证降级建议直连 Consumer（少一层网关干扰）：

```bash
curl http://localhost:8886/feign/user/1   # 先确认正常
# 停 Provider
curl http://localhost:8886/feign/user/1   # system error
```

---

## 模块结构

七模块：五模块 + `gateway-22`（9876）+ `turbine-22`（9999，Actuator 占位）。`gateway-22` 需要 `spring-boot-maven-plugin` 打可执行 jar，否则 Docker 里会 `no main manifest attribute` 起不来。

## 建议启动与验证

1. `docker compose up --build -d`，等 Eureka 里出现 Provider / Consumer（大约十几秒）
2. 经网关测门卫 + 转发
3. 直连 Consumer 对照；可选：停 Provider 看兜底
4. Eureka 账号 `roncoo` / `123456`

```bash
# 经网关（必须带 token）
curl -i http://localhost:9876/feign/user/1
curl -H "token: roncoo" http://localhost:9876/feign/user/1
curl -H "token: roncoo" http://localhost:9876/api/user/1

# 直连对照（不经过门卫）
curl http://localhost:8886/feign/user/1
curl http://localhost:7778/api/user/1
```

## 与后续课程

- **第 23 课**：Consumer 应用名改回 `spring-cloud-consumer`、端口 8888；门卫默认关；继续用 `9876` 走完整熔断演示

## Docker 一键启动

```bash
cd spring-cloud-22
docker compose up --build -d
```

只重建网关、不要把 Eureka 一起重建时：

```bash
docker compose build gateway && docker compose up -d --no-deps gateway
```

- 日志：`docker compose logs -f`
- 停止：`docker compose down -v`
- 验证：`curl -H "token: roncoo" http://localhost:9876/feign/user/1`
- Eureka：[http://localhost:8761](http://localhost:8761)
