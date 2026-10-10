# 第 22 课 · 网关过滤器与 Feign 降级

## 一句话先懂

大门（20 课）已经在了。本课给大门加一个**门卫**：请求头里必须带 `token=roncoo`，否则 401。门卫默认关着，和原视频里自定义 Zuul Filter 默认禁用一致。

另一条线在 Consumer：Feign 接口指定 **fallback 实现类**，Provider 挂了返回兜底，而不是把异常甩给用户。

路由表仍然几乎是空的——「门卫会检查证件」和「路线图」是两件事，路线图在 23 课。

## 学习目标

- 理解 Gateway **GlobalFilter**：所有进入网关的请求都会经过，类似 Zuul 的 PreFilter
- 会用配置开关 `gateway.token-filter.enabled` 控制过滤器是否生效
- 理解 Feign `fallback`：接口的「备用实现」，必须是 Spring Bean
- 能停 Provider 后从 `/feign/user/{id}` 看到 `"system error"` 一类兜底（直连 Consumer，不经空路由网关）

## 本课在整条链路里的位置

20 课空壳 → 本课横切逻辑 → 23 课才把 `/api/**` 接到 Provider。

---

## 知识点讲解

### 1. GlobalFilter：网关的统一前置逻辑

**是什么**

`TokenGlobalFilter` 实现 `GlobalFilter` + `Ordered`。请求进入 Gateway 后、转发到下游前，先看 Header `token` 是否等于 `roncoo`。不对就返回 **401**，body 为 `token is error`。

```java
@ConditionalOnProperty(name = "gateway.token-filter.enabled", havingValue = "true")
```

只有显式写成 `true` 时，这个 Bean 才存在。本课 properties **没写或为 false**，所以默认你带不带 token 都能打到网关（然后因为没路由，多半还是 404）。

**有什么用**

登录校验、租户识别、打印 traceId，都适合放在网关做一次，避免每个微服务复制一份。它不管「转发到哪」，只管家规。

**生活类比**

前台先查工牌，再决定带不带你进楼。查工牌的人（Filter）和墙上的办公室地图（routes）不是同一张纸。

开启实验（改网关配置后重启）：

```properties
gateway.token-filter.enabled=true
```

```bash
curl -H "token: roncoo" http://localhost:9876/任意路径
```

没有正确 token 应 401。**即使 token 对了，本课仍没有业务路由**，不要用 9876 测 User JSON。

### 2. Feign fallback 类

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

Consumer 应用名仍是 `spring-cloud-consumer2`，properties 端口 **8886**。Compose 若映射 8888 但未改 `SERVER_PORT`，请看启动日志里的真实端口（与 19 课同一类问题）。

本课 **没有** `spring.cloud.openfeign.circuitbreaker.enabled=true`（23 课才打开）。有 fallback 类时，部分失败路径仍可能进入降级；不要和 23 课的开关混为一谈。

### 3. 为什么业务验证要直连 Consumer

网关没有 `Path=/feign/** → lb://...`。经 9876 访问业务路径不会转到 8886。本课验证降级：

```bash
curl http://localhost:8886/feign/user/1   # 先确认正常
# 停 Provider
curl http://localhost:8886/feign/user/1   # system error
```

---

## 模块结构

七模块：五模块 + `gateway-22`（9876）+ `turbine-22`（9999，Actuator 占位）。

## 建议启动与验证

1. 启动全套
2. 直连 Consumer 测正常调用与停 Provider 后的两种兜底
3. 可选：打开 token 开关，看 9876 对错误 token 返回 401
4. Eureka 账号 `roncoo` / `123456`

## 与后续课程

- **第 23 课**：补上路由表，并打开 OpenFeign circuitbreaker；可以从 `http://localhost:9876/api/user/1` 一路打到 Provider

## Docker 一键启动

```bash
cd spring-cloud-22
docker compose up --build -d
```

- 日志：`docker compose logs -f`
- 停止：`docker compose down -v`
- 验证：以 Consumer 实际端口访问 `/feign/user/1`；网关 9876 无路由
- Eureka：[http://localhost:8761](http://localhost:8761)
