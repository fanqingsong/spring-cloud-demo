# 第 05 课 · Eureka 安全与集群

## 学习目标

- 为 Eureka Server 配置 **Spring Security HTTP Basic**
- 理解客户端 `defaultZone` 中**嵌入用户名密码**的写法
- 了解 **多 Eureka 节点互相注册** 组成注册中心集群

## 本课讲什么

生产上注册中心通常需要**访问控制**；高可用则需要**多个 Eureka 节点互相同步注册表**。本课用 3 个 service 模块模拟集群，并用统一账号 `roncoo/123456` 访问。

## 模块结构

| 模块 | 说明 |
|------|------|
| `spring-cloud-05-service` | 单节点 Eureka（带 Security，可与集群对照） |
| `spring-cloud-05-service-01/02/03` | 三节点集群，端口 8761/8762/8763 |
| `spring-cloud-05-provider` / `consumer` | 向集群注册 |

## 核心功能

1. **认证**：`spring.security.user.name/password` + `EurekaSecurityConfiguration`（禁用 CSRF，全路径 Basic 认证）
2. **集群**：各节点 `eureka.instance.hostname=roncoo1/2/3`，`defaultZone` 列出**其他节点**的 eureka 地址
3. **客户端**：`eureka.client.serviceUrl.defaultZone=http://roncoo:123456@roncoo1:8761/eureka/`（示例）

## 如何实现

- 所有 **service\*** 模块 POM 增加 `spring-boot-starter-security`
- **hosts 映射**：本地实验需在 `/etc/hosts` 配置 `roncoo1/roncoo2/roncoo3` 指向本机或对应机器，否则集群无法按 hostname 互通

## 建议启动与验证

1. 配置 hosts 后，依次启动 `service-01`、`service-02`、`service-03`
2. 启动 provider、consumer
3. 任一节点的 Eureka 控制台应能看到**来自其他节点的副本**及已注册服务

## 与后续课程

- **第 06 课**：在「能安全注册」的前提下，开始 **REST 调用与多 Provider 实例**。
