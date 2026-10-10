# 第 22 课 · 网关过滤器与 Feign 降级

## 学习目标

- 使用 **Gateway `GlobalFilter`** 实现全局前置逻辑（对应原 Zuul PreFilter）
- 为 Feign 配置 **`fallback` 实现类**（`RcFeignFallback`）
- 理解 **`gateway.token-filter.enabled`** 开关控制过滤器是否生效

## 本课讲什么

在 20 课 Gateway 模块基础上，增加 **TokenGlobalFilter**：校验 Header `token=roncoo`（默认 **关闭**，与原 Zuul 禁用 CustomPreFilter 一致）。Feign 接口 **`IUserBiz`** 指定 `fallback=RcFeignFallback.class`，下游异常时返回兜底数据。

## 模块结构

七模块：五模块 + gateway-22 + turbine-22。

## 核心功能

1. **TokenGlobalFilter**：`@ConditionalOnProperty(name = "gateway.token-filter.enabled", havingValue = "true")`
2. **RcFeignFallback**：实现 `IUserBiz`，在 `view1` 等方法的降级逻辑
3. Gateway properties **仍无** 完整 `spring.cloud.gateway.routes`（对比 23 课）

## 如何实现

- Filter 实现 `GlobalFilter` + `Ordered`，在 WebFlux 链路上修改请求/响应
- Feign Fallback 类需注册为 Spring Bean（`@Component`）

## 建议启动与验证

1. 启动全套 + Gateway
2. 开启 `gateway.token-filter.enabled=true` 后，经网关访问需带 Header `token: roncoo`
3. 停 Provider，通过 Feign 调用应走 **fallback**

## 与后续课程

- **第 23 课**：配置 **Gateway 路由** 与 **OpenFeign circuitbreaker**。

        ## Docker 一键启动

        本课已提供 **Docker Compose**，无需本地安装 JDK/Maven 即可启动演示（首次会镜像内 Maven 编译，耗时较长）。

        ```bash
        cd spring-cloud-22
        docker compose up --build -d
        ```

        - 查看日志：`docker compose logs -f`
        - 停止：`docker compose down -v`
        - 验证：Eureka：http://localhost:8761（`roncoo` / `123456`）；Consumer：http://localhost:8888
- Eureka 控制台默认账号：`roncoo` / `123456`

        > 容器内已通过环境变量将 Eureka 地址改为 `eureka`（或第 05 课集群 hostname），并开启 `prefer-ip-address` 以便服务间调用。
