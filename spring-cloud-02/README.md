# 第 02 课 · Eureka 入门

## 学习目标

- 理解微服务为什么要**服务注册与发现**
- 能启动 Eureka Server，并让 Provider、Consumer **注册到注册中心**
- 看懂 `spring.application.name` 与 `eureka.client.serviceUrl.defaultZone` 的作用

## 本课讲什么

这是 Spring Cloud 的**最小闭环**：一个注册中心、两个只负责「注册」的应用（还没有业务 HTTP 调用）。先建立「服务名 ↔ 实例地址」在 Eureka 控制台里的直观印象。

## 模块结构

| 模块 | 默认端口 | 角色 |
|------|----------|------|
| `spring-cloud-02-service` | 8761 | Eureka Server |
| `spring-cloud-02-provider` | 7777 | 服务提供者（客户端） |
| `spring-cloud-02-consumer` | 8888 | 服务消费者（客户端） |

## 核心功能

1. **注册中心**：不注册自己、不拉取别人，只维护注册表。
2. **Provider / Consumer**：启动后向 Eureka 上报本机 IP 与端口，服务名分别为 `spring-cloud-provider`、`spring-cloud-consumer`。

## 如何实现

- **Server**：`@EnableEurekaServer`（见 `SpringCloud02ServiceApplication`）
- **Client**：`@EnableEurekaClient`（见 Provider / Consumer 启动类）
- **依赖**：Server 使用 `spring-cloud-starter-netflix-eureka-server`；Client 使用 `spring-cloud-starter-netflix-eureka-client` + `spring-cloud-starter-loadbalancer`（为后续 RestTemplate 负载均衡做准备）

**关键配置（service）**：

```properties
eureka.client.register-with-eureka=false
eureka.client.fetch-registry=false
```

**关键配置（provider/consumer）**：

```properties
eureka.client.serviceUrl.defaultZone=http://localhost:8761/eureka/
```

## 建议启动与验证

1. 启动 `spring-cloud-02-service`
2. 启动 `spring-cloud-02-provider`、`spring-cloud-02-consumer`
3. 浏览器打开 `http://localhost:8761`，在 Eureka 界面应看到两个应用实例

## 与后续课程

- **第 04 课**：在 Eureka 上增加 Actuator、实例 ID、续约参数等运维向配置。
- **第 06 课**：Consumer 开始用 **RestTemplate** 按服务名调用 Provider 的 REST 接口。
