# 第 08 课 · 多服务与负载均衡策略

## 学习目标

- 同时注册 **两个逻辑服务**（`spring-cloud-provider` 与 `spring-cloud-provider2`）
- 用 **配置文件** 为不同服务指定负载均衡规则类名（教学上对应原 Ribbon 的 `NFLoadBalancerRuleClassName`）
- 了解 `@RibbonClient` / `IRule` Java 配置方式（本仓库中多为**注释**，便于对照旧视频）

## 本课讲什么

Consumer 既要调用主 Provider，也要调用第二套 Provider；并演示**按服务名分别配置**负载策略（如随机 `RandomRule`）。当前运行时由 **Spring Cloud LoadBalancer** 处理，properties 中的 `*.ribbon.*` 为课程遗留命名，部分需配合自定义扩展才完全等价于 Netflix Ribbon 行为。

## 模块结构

- `spring-cloud-08-service`
- `spring-cloud-08-provider-01/02` → 服务名 `spring-cloud-provider`
- `spring-cloud-08-provider2-01/02` → 服务名 `spring-cloud-provider2`
- `spring-cloud-08-consumer`

## 核心功能

1. **UserController**：两个 URL 前缀，分别访问两个服务名
2. **RandomRuleConfig / ProviderConfiguration**：注释掉的 `@RibbonClient` 示范
3. **application.properties**：
   - `spring-cloud-provider.ribbon.NFLoadBalancerRuleClassName=...RandomRule`
   - `spring-cloud-provider2.ribbon.NFLoadBalancerRuleClassName=...RandomRule`

## 如何实现

- 与 06 课相同的 RestTemplate + `@LoadBalanced`
- 通过 **不同 `spring.application.name`** 区分两套 Provider 集群

## 建议启动与验证

1. 启动 Eureka、两套 Provider（各至少一个实例）、Consumer
2. 分别调用指向 provider 与 provider2 的接口，确认都能通
3. 对同一服务多次调用，观察实例切换（与规则配置相关）

## 与后续课程

- **第 09 课**：编写 **自定义 Rule**（`RoncooCustomRule`）并绑定到 provider。
