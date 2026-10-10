# 第 20 课 · Spring Cloud Gateway 入门

## 一句话先懂

到现在为止，调用方必须知道 Consumer 是 8886、Provider 是 7778。**网关的作用是对外只暴露一个门口**（本课是 9876），外面的人只认识大门，由大门再转到后面的微服务。

本课只把大门**盖起来并在 Eureka 登记**，还没有写「哪条路通向哪个服务」。直接访问 9876 出现 404 是预期，完整路牌在第 23 课。

## 学习目标

- 能讲清 API 网关解决什么问题（统一入口、少暴露端口、后续加鉴权 / 限流）
- 知道本仓库用 **Spring Cloud Gateway** 替代已停更的 **Zuul 1**
- 理解 Gateway 基于 **WebFlux**，不要和 Servlet 型 Provider 揉进同一个 Spring Boot 进程
- 能在 Eureka 里看到 `spring-cloud-gateway`

## 本课在整条链路里的位置

| 课 | 网关 |
|----|------|
| **本课** | 空壳进程 + 注册 |
| 22 | 加全局过滤器（验 token），仍几乎无路由表 |
| 23 | 真正配置 `lb://服务名` 路由，可经网关调业务 |

---

## 知识点讲解

### 1. 为什么要有网关

**是什么**

网关是集群对外的**单一 HTTP 入口**。浏览器 / App / 合作方只访问 `http://网关/xxx`，由网关按路径转发到 Provider 或 Consumer。

**有什么用**

- 安全：内网服务端口不必全部对公网开放
- 横切：登录校验、限流、日志可以写一次，所有下游共享（22 课的 Token 过滤器）
- 演进：后面加服务、改端口，调用方仍只认大门

**生活类比**

公司只设一个前台。访客不直接冲进各个办公室；前台看访客要找谁，再带路。本课是「前台桌子摆好了，路线图还没贴」。

### 2. Spring Cloud Gateway vs Zuul 1

原视频是 Netflix Zuul 1（Servlet 阻塞模型）。Zuul 1 停更后，Spring 官方推荐 **Spring Cloud Gateway**：

- 建立在 WebFlux（响应式）上
- 用 `spring.cloud.gateway.routes` 声明路由（23 课）
- 用 `lb://spring-cloud-provider` 结合注册中心做转发

依赖是 `spring-cloud-starter-gateway`。不要在同一个应用里再引 `spring-boot-starter-web`（Servlet），两者抢 HTTP 服务器，启动容易冲突。

### 3. 本课为什么没有 routes

`GatewayApplication` 几乎是空的启动类 + Eureka Client + LoadBalancer。properties **没有** `spring.cloud.gateway.routes`。

**有什么用（作为一课）**

先确认：网关也是一个普通微服务，要注册、要有应用名 `spring-cloud-gateway`、端口 9876。路由规则是下一步的配置，不是「有了依赖就自动转发给所有服务」。

访问 `http://localhost:9876/` 得到 404 / 空响应，说明进程活着但「没匹配到任何路由」，这是成功，不是失败。

业务验证请继续走 Consumer：`http://localhost:8886/user/1`（本课 Consumer 仍是 consumer2 / 8886）。Turbine 模块继续当 Actuator 占位（9999）。

---

## 模块结构

| 模块 | 端口 | 应用名 |
|------|------|--------|
| service | 8761 | `spring-cloud-server` |
| provider | 7778 | `spring-cloud-provider` |
| consumer | 8886 | `spring-cloud-consumer2` |
| **gateway** | **9876** | **`spring-cloud-gateway`** |
| turbine | 9999 | `spring-cloud-turbine`（占位） |
| bean / api | — | 同前 |

## 建议启动与验证

1. 启动 Eureka、Provider、Consumer、Gateway
2. 控制台出现 `SPRING-CLOUD-GATEWAY`
3. `curl -I http://localhost:9876/` —— 无路由，404 属预期
4. 业务仍：`curl http://localhost:8886/user/1`

## 与后续课程

- **第 22 课**：`TokenGlobalFilter` + Feign fallback（过滤器要显式打开才生效）
- **第 23 课**：`/api/**`、`/feign/**` 两条完整路由

## Docker 一键启动

```bash
cd spring-cloud-20
docker compose up --build -d
```

- 日志：`docker compose logs -f`
- 停止：`docker compose down -v`
- 验证：Gateway [http://localhost:9876](http://localhost:9876)；Eureka [http://localhost:8761](http://localhost:8761)
- 账号：`roncoo` / `123456`
