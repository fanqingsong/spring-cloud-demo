# 第 13 课 · 多模块综合（Feign 工程化）

## 学习目标

- 熟练启动 **五模块** 标准布局：`bean` / `api` / `service` / `provider` / `consumer`
- 巩固 12 课的 Feign 契约、压缩、负载规则配置
- 为后续 **熔断、网关** 等章节打基础

## 本课讲什么

内容与 **第 12 课** 技术点基本一致，模块命名为 `*-13`，代表课程后半段「完整微服务小系统」的固定模板。重点在**工程结构**与**多模块 Maven 编译**，而非全新组件。

## 模块结构

- `spring-cloud-bean-13`
- `spring-cloud-api-13`
- `spring-cloud-service-13`（Eureka，应用名常为 `spring-cloud-server`）
- `spring-cloud-provider-13`（7778，`spring-cloud-provider`）
- `spring-cloud-consumer-13`（8888，`spring-cloud-consumer`）

## 核心功能

- OpenFeign + `UserService` 契约 + `FeignApiUserController`
- `RoncooCustomRule` / Ribbon 属性等（与 12 课同类）
- Eureka 带 Security（`roncoo/123456`）

## 如何实现

- 父 POM `spring-cloud-13` 继承根 `spring-cloud-demo`，`dependencyManagement` 管理 bean、api 版本
- Consumer：`@EnableFeignClients` + 依赖 `spring-cloud-api-13`

## 建议启动与验证

1. `mvn -pl spring-cloud-13 -am compile`
2. 启动顺序：service → provider → consumer
3. 通过 Consumer 的 Feign 接口访问 User 数据

## 与后续课程

- **第 14 课**：Consumer 增加 **Resilience4j** 保护 RestTemplate 调用。

        ## Docker 一键启动

        本课已提供 **Docker Compose**，无需本地安装 JDK/Maven 即可启动演示（首次会镜像内 Maven 编译，耗时较长）。

        ```bash
        cd spring-cloud-13
        docker compose up --build -d
        ```

        - 查看日志：`docker compose logs -f`
        - 停止：`docker compose down -v`
        - 验证：Eureka：http://localhost:8761（`roncoo` / `123456`）；Consumer：http://localhost:8888
- Eureka 控制台默认账号：`roncoo` / `123456`

        > 容器内已通过环境变量将 Eureka 地址改为 `eureka`（或第 05 课集群 hostname），并开启 `prefer-ip-address` 以便服务间调用。
