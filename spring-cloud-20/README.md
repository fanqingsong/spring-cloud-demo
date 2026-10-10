# 第 20 课 · Spring Cloud Gateway 入门

## 学习目标

- 认识 **API 网关**：统一入口、路由转发、与 Zuul 1 的替代关系
- 启动 **`spring-cloud-gateway-20`** 并注册到 Eureka
- 理解本课 Gateway **尚未配置 routes**（为 22、23 课铺垫）

## 本课讲什么

网关是微服务对外的**单一入口**。本仓库已从 **Zuul** 升级为 **Spring Cloud Gateway**（WebFlux）。20 课仅引入 **Gateway 空壳应用** + 原有微服务 + Turbine 课位，路由规则在 **23 课** 才完整出现。

## 模块结构

- 五模块 `*-20` + **`spring-cloud-gateway-20`** + **`spring-cloud-turbine-20`**
- Gateway 端口 **9876**，`spring.application.name=spring-cloud-gateway`

## 核心功能

1. **GatewayApplication**：`@SpringBootApplication` + 依赖 `spring-cloud-starter-gateway`
2. Eureka Client + LoadBalancer：便于后续 `lb://服务名` 路由
3. Consumer2（8886）与 Turbine 模块同 19 课

## 如何实现

- Gateway 与 Servlet 型 Provider **不同栈**（Gateway 基于 WebFlux），不要合并为一个 Spring Boot 应用
- 本课 properties **无** `spring.cloud.gateway.routes` — 直接访问仍用 Consumer/Provider 端口

## 建议启动与验证

1. 启动 Eureka、Provider、Consumer、Gateway
2. 确认 Gateway 在 Eureka 中注册
3. 尝试访问 Gateway 端口（无路由时可能 404，属预期）

## 与后续课程

- **第 22 课**：**GlobalFilter**（Token 校验）+ **Feign Fallback**
- **第 23 课**：完整 **路由表** + OpenFeign 熔断

        ## Docker 一键启动

        本课已提供 **Docker Compose**，无需本地安装 JDK/Maven 即可启动演示（首次会镜像内 Maven 编译，耗时较长）。

        ```bash
        cd spring-cloud-20
        docker compose up --build -d
        ```

        - 查看日志：`docker compose logs -f`
        - 停止：`docker compose down -v`
        - 验证：Gateway http://localhost:9876；Eureka http://localhost:8761
- Eureka 控制台默认账号：`roncoo` / `123456`

        > 容器内已通过环境变量将 Eureka 地址改为 `eureka`（或第 05 课集群 hostname），并开启 `prefer-ip-address` 以便服务间调用。
