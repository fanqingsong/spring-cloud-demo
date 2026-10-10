# 第 10 课 · OpenFeign 声明式调用

## 学习目标

- 使用 **`@FeignClient`** 定义 HTTP 接口，由框架生成实现
- 理解 **`@EnableFeignClients`** 与 Feign 接口扫描
- 知道 **`spring.cloud.openfeign.circuitbreaker.enabled=true`** 表示 Feign 与 **Resilience4j** 集成（替代原 Hystrix）

## 本课讲什么

RestTemplate 需要手写 URL 与方法；Feign 用**接口 + 注解**描述 REST 调用。本课 Feign 接口 **`IUserBiz` 写在 Consumer 模块内**，是最小 Feign 示例。

## 模块结构

- `spring-cloud-10-service`
- `spring-cloud-10-provider-01/02`
- `spring-cloud-10-consumer`（含 `IUserBiz`、`FeignUserController`）

## 核心功能

1. **IUserBiz**：`@FeignClient("spring-cloud-provider")` + Spring MVC 注解映射路径
2. **FeignUserController**：注入 `IUserBiz` 对外暴露 HTTP
3. **UserController**：仍保留 RestTemplate 方式，便于对比
4. **熔断开关**：properties 中开启 OpenFeign circuit breaker（需 Resilience4j 依赖与后续课配合 fallback）

## 如何实现

- POM：`spring-cloud-starter-openfeign`
- 启动类：`@EnableFeignClients`
- 服务名与 Provider 的 `spring.application.name` 一致

## 建议启动与验证

1. 启动 Eureka、Provider、Consumer
2. 调用 Feign 暴露的接口（见 `FeignUserController` 路径）
3. 对比 RestTemplate 与 Feign 两种调用链路的日志

## 与后续课程

- **第 11 课**：把 Feign 接口抽到 **api 模块**，bean 模块放实体类。
