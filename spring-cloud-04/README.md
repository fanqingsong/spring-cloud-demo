# 第 04 课 · Eureka 进阶与 Actuator

## 学习目标

- 了解 Eureka Server 的**自我保护、驱逐间隔**等参数含义
- 会使用 **Actuator** 暴露构建信息与实例状态页
- 理解 **instanceId、prefer-ip-address、租约** 等客户端实例配置

## 本课讲什么

在 02 课「能注册」的基础上，本课讲**注册中心与实例在运行层面的细节**：数据中心标识、关闭自我保护便于实验、Actuator `/info`、以及客户端拉取注册表与心跳间隔。

## 模块结构

与 02 课相同：`service` + `provider` + `consumer`（三模块）。

## 核心功能

1. **Server 调优示例**：`enable-self-preservation=false`、`eviction-interval-timer-in-ms`（实验环境更易看到实例下线）
2. **Actuator**：Provider/Consumer 引入 `spring-boot-starter-actuator`，配合 `info.build.*=@project.*@` 展示 Maven 坐标
3. **实例元数据**：`eureka.instance.instanceId=${spring.application.name}:${random.value}` 等

## 如何实现

- 启动类仍用 `@EnableEurekaServer` / `@EnableEurekaClient`
- `EurekaSecurityConfiguration` 类已存在，但本课 **service 模块尚未引入 Security**（为 05 课认证做准备）
- POM 中 Provider/Consumer 增加 **actuator**、**devtools**

## 建议启动与验证

1. 按 02 课顺序启动三个应用
2. 访问 Provider 的 Actuator（若已暴露）：如 `http://localhost:7777/info`（具体以 `management.*` 配置为准）
3. 在 Eureka 控制台查看实例 **IP、端口、instanceId**

## 与后续课程

- **第 05 课**：Eureka **HTTP 认证** + **三节点集群**。
- 本课仍**没有** Consumer 调用 Provider 的业务代码。
