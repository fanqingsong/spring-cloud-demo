# 第 20 课 · Spring Cloud Gateway 入门

## 一句话先懂

到现在为止，调用方必须知道 Consumer 是 8886、Provider 是 7778。**网关的作用是对外只暴露一个门口**（本课是 9876），外面的人只认识大门，由大门再转到后面的微服务。

本课在 Eureka 登记网关，并在 `application.properties` 里配置了 **`spring.cloud.gateway.routes`**，经 9876 即可转发到 Provider / Consumer。未匹配任何路由的路径（例如根路径 `/`）仍会 404，这是正常现象。

## 学习目标

- 能讲清 API 网关解决什么问题（统一入口、少暴露端口、后续加鉴权 / 限流）
- 知道本仓库用 **Spring Cloud Gateway** 替代已停更的 **Zuul 1**
- 理解 Gateway 基于 **WebFlux**，不要和 Servlet 型 Provider 揉进同一个 Spring Boot 进程
- 理解 **`pom.xml` 引入 Gateway 依赖后，启动类不必 import Gateway 包**（自动配置生效）
- 能说明 Gateway **如何**注册到 Eureka（依赖 + 配置 + 自动配置，启动类无注册代码）
- 能分清 Gateway 对 Eureka 的两种关系：**拉注册表做 `lb://`**（路由必需）与 **把自己也注册**（本课开启，运维/教学用途）
- 能在 Eureka 里看到 `spring-cloud-gateway`，并用 `lb://服务名` 经网关访问业务

## 本课在整条链路里的位置

| 课 | 网关 |
|----|------|
| **本课** | 启动类 + 注册 + **基础路由表**（`/api/**`、`/feign/**`、`/user/**`） |
| 22 | 加全局过滤器（验 token），路由表与 23 课类似 |
| 23 | 深化路由与熔断等（Consumer 注册名在部分课次为 `spring-cloud-consumer`） |

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

公司只设一个前台。访客不直接冲进各个办公室；前台看访客要找谁，再带路。本课是「前台摆好 + 路线图贴好」，未登记的路径仍会被告知「找不到」。

### 2. Spring Cloud Gateway vs Zuul 1

原视频是 Netflix Zuul 1（Servlet 阻塞模型）。Zuul 1 停更后，Spring 官方推荐 **Spring Cloud Gateway**：

- 建立在 WebFlux（响应式）上
- 用 `spring.cloud.gateway.routes` 声明路由
- 用 `lb://spring-cloud-provider` 结合注册中心做转发

依赖是 `spring-cloud-starter-gateway`。不要在同一个应用里再引 `spring-boot-starter-web`（Servlet），两者抢 HTTP 服务器，启动容易冲突。

### 3. 为什么 `GatewayApplication` 里没有 Gateway 的 import？

`spring-cloud-gateway-20/pom.xml` 里已有 `spring-cloud-starter-gateway`，但 `GatewayApplication` 通常只有 `@SpringBootApplication` 和 `main`，**看不到** `import org.springframework.cloud.gateway...`，这是 **正确且常见** 的写法。

**原理**

- `@SpringBootApplication` 会开启组件扫描和 **自动配置（Auto-configuration）**。
- `spring-cloud-starter-gateway` 在 classpath 上时，会通过 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`（旧版为 `spring.factories`）注册 Gateway 相关配置类（如 `GatewayAutoConfiguration`），从而启动 Netty、路由引擎、过滤器链等。
- 因此：**依赖 + 自动配置** 即可，不必在启动类里手动组装 Gateway。

**什么时候才要在 Java 里引用 Gateway 包？**

仅当你自己写代码时，例如：`@Bean RouteLocator` 编程式路由、自定义 `GlobalFilter` / `GatewayFilterFactory` 等。本课路由写在 **`application.properties`** 里即可。

**注意**

有了 Gateway 依赖 **不会** 自动把「所有已注册服务」都转发出去，仍须在配置或 Java 中 **显式声明路由**；否则进程能起来，但没有可用的转发规则。

### 4. 本课路由配置（`spring.cloud.gateway.routes`）

配置在 `spring-cloud-gateway-20/src/main/resources/application.properties`。`lb://` 后的 **服务名必须与 Eureka 注册名一致**；本课 Consumer 为 **`spring-cloud-consumer2`**（不是其它课次里的 `spring-cloud-consumer`）。

| 路由 id | 匹配路径 | 转发目标 | 对应原直连示例 |
|---------|----------|----------|----------------|
| `provider-api` | `/api/**` | `lb://spring-cloud-provider` | `http://localhost:7778/api/user/1` |
| `consumer-feign` | `/feign/**` | `lb://spring-cloud-consumer2` | `http://localhost:8886/feign/user/...` |
| `consumer-user` | `/user/**` | `lb://spring-cloud-consumer2` | `http://localhost:8886/user/1` |

网关模块还依赖 **Eureka Client** 与 **Spring Cloud LoadBalancer**，`lb://` 才会从注册中心解析实例。

访问 `http://localhost:9876/` 无匹配路由，得到 **404** 说明进程在跑、只是根路径未配置路由，**不是** 启动失败。业务请走上表中的路径。

### 5. Gateway 如何注册到 Eureka？为什么要注册？

与 Provider、Consumer 相同：**`GatewayApplication` 里没有写任何注册代码**，靠 Eureka Client 的自动配置完成。

**怎么注册**

1. **依赖**：`spring-cloud-starter-netflix-eureka-client`（见 `spring-cloud-gateway-20/pom.xml`）。
2. **配置**（`application.properties`）：
   - `spring.application.name=spring-cloud-gateway` → Eureka 控制台显示为 **`SPRING-CLOUD-GATEWAY`**
   - `eureka.client.serviceUrl.defaultZone=...` → 注册中心地址
   - 实例相关：`eureka.instance.instanceId`、`prefer-ip-address`、续约/拉取间隔等
3. **启动后自动行为**：
   - 向 Eureka **注册**本实例（如端口 9876）
   - 定时 **心跳续约**（本课 `lease-renewal-interval-in-seconds=15`）
   - 定时 **拉取注册表**（本课 `registry-fetch-interval-seconds=30`）

日志中可见类似：`Registering application SPRING-CLOUD-GATEWAY`、`registration status: 204`、`Netty started on port 9876`。

**为什么要和 Eureka 打交道（两件事别混为一谈）**

| 角色 | 是否本课必需 | 说明 |
|------|--------------|------|
| **作为 Eureka 客户端，发现下游** | **是**（用了 `lb://` 就必须） | 路由指向 `lb://spring-cloud-provider` 时，Gateway 要从注册表拿到 Provider/Consumer 实例，再经 **LoadBalancer** 选一个转发。拉不到注册表易出现 **503**。 |
| **把自己也注册到 Eureka** | **否**（本课仍开启） | 外部访问网关通常是固定 `http://host:9876`，不一定要在 Eureka 里查网关名。注册主要是为了：**控制台可见**、与其它微服务一致的运维习惯、多实例网关时的实例列表等。 |

关系示意：

```
调用方 → :9876 Gateway ──lb://──► Provider / Consumer
              │    ▲
              │    └── 拉注册表（解析 lb://，必需）
              └── 注册 + 心跳（本课开启，可选架构）
                    Eureka
         Provider / Consumer 也注册 ──► Eureka
```

若只想「发现别人、不在 Eureka 里挂自己」，可单独配置（本课未采用）：

```properties
eureka.client.register-with-eureka=false
eureka.client.fetch-registry=true
```

仍可使用 `lb://` 转发，但 Eureka 列表里不会出现 Gateway。

**和 §3 的对比**

- Gateway **路由能力**：`spring-cloud-starter-gateway` 自动配置。
- **注册 / 发现**：`spring-cloud-starter-netflix-eureka-client` + 上述 properties 自动配置。
- 启动类仍只需 `@SpringBootApplication`，两类能力都靠 classpath 上的 starter 分别生效。

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
2. Eureka 控制台出现 `SPRING-CLOUD-GATEWAY`，且 Provider / Consumer 已注册
3. 经网关访问（下游就绪后再测，避免 503）：
   - `curl http://localhost:9876/api/user/1`
   - `curl http://localhost:9876/user/1`
   - `curl http://localhost:9876/feign/user/1`（若 Consumer 已启用对应接口）
4. `curl -I http://localhost:9876/` —— 未配置根路径路由，**404 属预期**
5. 对照直连：`curl http://localhost:8886/user/1`（应与经网关的 `/user/1` 行为一致）

## 与后续课程

- **第 22 课**：`TokenGlobalFilter` + Feign fallback（过滤器要显式打开才生效）
- **第 23 课**：同样用 `spring.cloud.gateway.routes` 与 `lb://`，可对照本课路由；注意不同模块里 Consumer 的 **Eureka 应用名** 可能不同

## Docker 一键启动

```bash
cd spring-cloud-20
docker compose up --build -d
```

- 日志：`docker compose logs -f`
- 停止：`docker compose down -v`
- 验证：Gateway [http://localhost:9876](http://localhost:9876)；Eureka [http://localhost:8761](http://localhost:8761)
- 账号：`roncoo` / `123456`

**Docker 排错**：若 `docker compose logs gateway` 出现 `no main manifest attribute, in /app/app.jar`，说明 JAR 未经过 `spring-boot-maven-plugin` 的 `repackage`。本仓库已在 `spring-cloud-gateway-20`、`spring-cloud-turbine-20` 的 `pom.xml` 中配置；修改后请 `docker compose build --no-cache gateway` 再 `up -d`。
