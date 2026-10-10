# 第 06 课 · RestTemplate 与负载均衡调用

## 学习目标

- 使用 **`@LoadBalanced RestTemplate`** 通过**服务名**调用 HTTP 接口
- 理解**同一 `spring.application.name` 多实例**在 Eureka 中的呈现
- 能阅读 Provider 端 REST 控制器返回的 JSON

## 本课讲什么

微服务之间最常见的同步调用方式之一：`RestTemplate` + 注册中心 + 客户端负载均衡（Spring Cloud **LoadBalancer**，替代已下线的 Ribbon 客户端）。

## 模块结构

| 模块 | 说明 |
|------|------|
| `spring-cloud-06-service` | Eureka（带 Security） |
| `spring-cloud-06-provider-01/02/03` | 三个进程，**同名** `spring-cloud-provider`，端口 7778–7780 |
| `spring-cloud-06-provider` | 可选单实例对照（7777） |
| `spring-cloud-06-consumer` | 发起 HTTP 调用 |

## 核心功能

1. **ConsumerApplication**：定义 `@LoadBalanced RestTemplate` Bean
2. **UserController**：URL 写为 `http://spring-cloud-provider/api/user/{id}`，由 LoadBalancer 解析为某一实例
3. **ApiUserController**：Provider 返回 `User` JSON；不同实例可返回不同标识（如无境1/2/3）

## 如何实现

- 依赖：`spring-cloud-starter-netflix-eureka-client` + **`spring-cloud-starter-loadbalancer`**
- 要点：**主机名必须是服务 ID**（与 `spring.application.name` 一致），不能写死 `localhost:7778`（除非不用负载均衡）

## 建议启动与验证

1. 启动 Eureka → 启动 **provider-01、02、03** → 启动 consumer
2. 多次请求 Consumer 的 `/user/{id}`（具体路径见 `UserController` 的 `@RequestMapping`）
3. 观察日志或返回内容是否在多实例间**轮询或随机**（默认策略）

## 与后续课程

- **第 08 课**：两个不同服务名 + **按服务配置负载策略**。
- **第 10 课**：用 **OpenFeign** 替代手写 RestTemplate URL。
