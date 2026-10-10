# 第 23 课 · 网关路由与 OpenFeign 熔断

## 学习目标

- 配置 **`spring.cloud.gateway.routes`**，用 **`lb://服务名`** 转发到 Provider / Consumer
- 开启 **`spring.cloud.openfeign.circuitbreaker.enabled`**
- 综合运用 Eureka、Feign、Gateway、Resilience4j（升级后的 Netflix 栈替代方案）

## 本课讲什么

这是原课程 **Zuul + Hystrix + Turbine** 阶段的**现代化版本**：Gateway 替代 Zuul，Resilience4j 替代 Hystrix，LoadBalancer 替代 Ribbon。23 课提供**完整可演示**的网关路由与微服务调用链。

## 模块结构

- `spring-cloud-bean-23` / `api-23` / `service-23` / `provider-23` / `consumer-23`
- `spring-cloud-gateway-23`（9876）
- `spring-cloud-turbine-23`（Actuator 占位，9999）

## 核心功能

1. **Gateway 路由**（示例）：
   - `/api/**` → `lb://spring-cloud-provider`
   - `/feign/**` → `lb://spring-cloud-consumer`
2. **TokenGlobalFilter**（可选，默认 `gateway.token-filter.enabled=false`）
3. **Consumer**：`@CircuitBreaker` on RestTemplate；Feign + fallback + circuitbreaker
4. **超时**：Gateway `httpclient.connect-timeout` / `response-timeout`

## 如何实现

- Gateway 依赖：`spring-cloud-starter-gateway` + eureka-client + loadbalancer
- 路由使用服务 ID，与 `spring.application.name` 一致
- Consumer 端口 **8888**，应用名 **`spring-cloud-consumer`**

## 建议启动与验证

1. 启动：service(8761) → provider(7778) → consumer(8888) → gateway(9876)
2. 经网关访问：`http://localhost:9876/api/user/1`（若 Gateway 配置了 JWT/安全，以当前代码为准；默认 Gateway 23 无 OAuth，直接访问）
3. Feign 路径：`http://localhost:9876/feign/...`（见 Consumer 控制器映射）
4. 编译：`mvn -pl spring-cloud-23 -am compile`

## 与后续课程

- **第 24 课**：**Config Server、OAuth2、Zipkin、Kafka Stream** 官方栈。

        ## Docker 一键启动

        本课已提供 **Docker Compose**，无需本地安装 JDK/Maven 即可启动演示（首次会镜像内 Maven 编译，耗时较长）。

        ```bash
        cd spring-cloud-23
        docker compose up --build -d
        ```

        - 查看日志：`docker compose logs -f`
        - 停止：`docker compose down -v`
        - 验证：Gateway http://localhost:9876/api/...（见课内 README）
- Eureka 控制台默认账号：`roncoo` / `123456`

        > 容器内已通过环境变量将 Eureka 地址改为 `eureka`（或第 05 课集群 hostname），并开启 `prefer-ip-address` 以便服务间调用。
