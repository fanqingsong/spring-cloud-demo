# 第 09 课 · 自定义负载均衡规则

## 学习目标

- 阅读 **`AbstractLoadBalancerRule`** 子类，理解「从 Server 列表中选一个实例」的逻辑
- 将自定义类名配置到 **`NFLoadBalancerRuleClassName`**
- 结合多实例 Provider，验证**非默认**的选择行为

## 本课讲什么

在 08 课「随机 / 轮询等内置规则」之上，本课实现 **RoncooCustomRule**（示例：优先选择端口为 7779 的实例），体现负载均衡可扩展。

## 模块结构

- `spring-cloud-09-service`
- `spring-cloud-09-provider-01/02`（同服务名，端口 7778/7779）
- `spring-cloud-09-consumer`

## 核心功能

1. **RoncooCustomRule**：在 `choose()` 中遍历 `Server`，按端口等条件挑选
2. **Consumer properties**：`spring-cloud-provider.ribbon.NFLoadBalancerRuleClassName=com.roncoo.education.configuration.RoncooCustomRule`
3. **UserController**：RestTemplate 调用 `spring-cloud-provider`

## 如何实现

- 自定义类放在 Consumer 模块（LoadBalancer 客户端侧生效）
- 确保类在 classpath 且类名与配置一致

## 建议启动与验证

1. 启动两个 Provider 实例（7778、7779）
2. 多次请求 Consumer，观察是否**偏向 7779**（以你本地 Rule 实现为准）

## 与后续课程

- **第 10 课**：引入 **OpenFeign**，减少 RestTemplate 模板代码。
