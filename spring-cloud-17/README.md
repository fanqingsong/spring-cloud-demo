# 第 17 课 · Provider 随机端口

## 学习目标

- 理解 **`server.port=0`**：由 Spring Boot 分配随机可用端口
- 在 Eureka 中仍用 **服务名** 访问，体会与「固定端口多实例」的差异
- 继续练习 Feign + 熔断

## 本课讲什么

本地常开多个 Provider 进程模拟集群；随机端口避免端口冲突。Eureka 注册的是**实际端口**，Consumer 无感知。

## 模块结构

五模块 `*-17`；**provider-17** 使用 `server.port=0`。

## 核心功能

- Provider 启动日志中查看 **实际端口**
- Consumer：Feign + RestTemplate + Resilience4j
- properties 中可能保留 Hystrix 时代配置项作对照（注释或 false）

## 如何实现

- 仅改 Provider 的 `server.port=0`，`spring.application.name` 仍为 `spring-cloud-provider`
- 同一机器可启动**多个 Provider 进程**（多个 JVM），每个随机端口、同一服务名

## 建议启动与验证

1. 启动两个 Provider 应用实例（IDE 运行两次 `ProviderApplication`）
2. Eureka 控制台应看到 **两条** `spring-cloud-provider`
3. Consumer 多次调用，观察负载到不同实例

## 与后续课程

- **第 18 课**：Provider、Consumer 引入 **Actuator** 依赖。
