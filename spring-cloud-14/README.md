# 第 14 课 · 服务熔断（Resilience4j）

## 学习目标

- 理解 **熔断 / 降级**：下游失败时返回 fallback，避免雪崩
- 使用 **`@CircuitBreaker`**（Resilience4j）保护 **RestTemplate** 调用
- 区分配置文件中 **Hystrix 遗留项**（本仓库已不使用 Hystrix 依赖）

## 本课讲什么

原视频使用 Hystrix；升级后使用 **Spring Cloud Circuit Breaker + Resilience4j**。本课在 Consumer 的 `UserController` 上对远程 GET 增加熔断与 `getFallback` 方法。

## 模块结构

五模块 `*-14`，布局同 13。

## 核心功能

1. **POM**：`spring-cloud-starter-circuitbreaker-resilience4j`
2. **UserController**：`@CircuitBreaker(name = "getUser", fallbackMethod = "getFallback")`
3. **Feign**：仍可用；本课重点在 RestTemplate 路径
4. properties 中可能保留 `feign.hystrix.enabled=false` 等**说明性**配置

## 如何实现

- 启动类无需 `@EnableCircuitBreaker`（Hystrix 时代注解已移除）
- fallback 方法签名需与受保护方法兼容（参数 + 返回类型）

## 建议启动与验证

1. 正常启动全套服务，确认调用成功
2. 停掉 Provider 或制造超时，再次调用 Consumer，应触发 **fallback** 返回自定义字符串

## 与后续课程

- **第 16 课**：熔断 + **RandomRule** 负载策略并存练习。

        ## Docker 一键启动

        本课已提供 **Docker Compose**，无需本地安装 JDK/Maven 即可启动演示（首次会镜像内 Maven 编译，耗时较长）。

        ```bash
        cd spring-cloud-14
        docker compose up --build -d
        ```

        - 查看日志：`docker compose logs -f`
        - 停止：`docker compose down -v`
        - 验证：Eureka：http://localhost:8761（`roncoo` / `123456`）；Consumer：http://localhost:8888
- Eureka 控制台默认账号：`roncoo` / `123456`

        > 容器内已通过环境变量将 Eureka 地址改为 `eureka`（或第 05 课集群 hostname），并开启 `prefer-ip-address` 以便服务间调用。
