# 第 16 课 · 熔断与负载均衡组合

## 学习目标

- 同时运用 **Resilience4j 熔断** 与 **负载均衡策略配置**
- 对比 14 课 properties 差异（Hystrix 注释、RandomRule 启用等）

## 本课讲什么

仓库中**无第 15 课**代码。16 课在 14 课熔断基础上，重新强调 **provider / provider2 的 RandomRule** 属性，形成「调用链保护 + 多实例选择」的组合实验。

## 模块结构

五模块 `*-16`。

## 核心功能

- `@CircuitBreaker` + `@LoadBalanced RestTemplate` + Feign 并存
- `spring-cloud-provider.ribbon.NFLoadBalancerRuleClassName=RandomRule`（及 provider2）

## 如何实现

与 14 课相同依赖；差异主要在 **application.properties** 与负载规则是否启用。

## 建议启动与验证

1. 启动两个 Provider 实例
2. 多次调用并观察实例分布 + 停 Provider 测 fallback

## 与后续课程

- **第 17 课**：Provider **`server.port=0`** 随机端口，更贴近云环境多实例。

        ## Docker 一键启动

        本课已提供 **Docker Compose**，无需本地安装 JDK/Maven 即可启动演示（首次会镜像内 Maven 编译，耗时较长）。

        ```bash
        cd spring-cloud-16
        docker compose up --build -d
        ```

        - 查看日志：`docker compose logs -f`
        - 停止：`docker compose down -v`
        - 验证：Eureka：http://localhost:8761（`roncoo` / `123456`）；Consumer：http://localhost:8888
- Eureka 控制台默认账号：`roncoo` / `123456`

        > 容器内已通过环境变量将 Eureka 地址改为 `eureka`（或第 05 课集群 hostname），并开启 `prefer-ip-address` 以便服务间调用。
