# 第 19 课 · 监控聚合与多 Consumer

## 学习目标

- 了解原 **Netflix Turbine** 聚合多条熔断流的概念（现网多用 **Micrometer + Prometheus/Grafana**）
- 理解 **多个 Consumer 应用名** 同时注册到 Eureka 的场景
- 阅读 **turbine 模块** 升级说明（本仓库改为 **Actuator** 占位）

## 本课讲什么

原课程用 Turbine 把多个服务的 Hystrix 流汇总到一个 Dashboard。Hystrix 下线后，本仓库保留 **`spring-cloud-turbine-19`** 模块名，POM 改为 **Actuator + Eureka Client**，properties 中 **turbine.\*** 配置保留作对照。

Consumer 模块使用应用名 **`spring-cloud-consumer2`**，端口 **8886**，metadata `cluster=RONCOO`。

## 模块结构

- 五模块 `*-19`
- **`spring-cloud-turbine-19`**（9999，`spring-cloud-turbine`）
- **`spring-cloud-service-19`** 含 Hystrix Dashboard 依赖已移除（升级后仅 Eureka + Security）

## 核心功能

1. 双 Consumer 身份设计（配置中常写 `consumer` + `consumer2`；完整演示可能需**再启一个 consumer 实例**或复制配置）
2. Turbine 模块：学习 **监控入口** 概念，运行 `TurbineApplication` 可注册到 Eureka
3. Feign + Resilience4j 延续前课

## 如何实现

- 不要期望 Turbine UI 与原视频一致；请结合 README 与 **Actuator** 端点理解演进
- 若跑聚合实验：确保 Eureka 上至少有 **consumer2** 与 provider 实例

## 建议启动与验证

1. 启动 service → provider → consumer-19 → turbine-19
2. 查看 Eureka 是否出现 `spring-cloud-consumer2`、`spring-cloud-turbine`
3. 访问 turbine 进程 Actuator health

## 与后续课程

- **第 20 课**：新增 **Spring Cloud Gateway** 模块（9876）。

        ## Docker 一键启动

        本课已提供 **Docker Compose**，无需本地安装 JDK/Maven 即可启动演示（首次会镜像内 Maven 编译，耗时较长）。

        ```bash
        cd spring-cloud-19
        docker compose up --build -d
        ```

        - 查看日志：`docker compose logs -f`
        - 停止：`docker compose down -v`
        - 验证：Eureka：http://localhost:8761（`roncoo` / `123456`）；Consumer：http://localhost:8888
- Eureka 控制台默认账号：`roncoo` / `123456`

        > 容器内已通过环境变量将 Eureka 地址改为 `eureka`（或第 05 课集群 hostname），并开启 `prefer-ip-address` 以便服务间调用。
