# 第 18 课 · Actuator 监控

## 学习目标

- 在微服务中引入 **`spring-boot-starter-actuator`**
- 了解健康检查、信息端点在**运维与注册**中的用途（如 Eureka status-page）
- 结合负载规则与熔断继续综合练习

## 本课讲什么

Actuator 提供 **/actuator/health** 等端点，是后续 **K8s 探针、监控体系** 的基础。本课在 Provider、Consumer 的 POM 中加入 Actuator；与 19 课「监控聚合」衔接。

## 模块结构

五模块 `*-18`；Provider 恢复固定端口 **7778**；Consumer 启用 **RandomRule** 属性示例。

## 核心功能

- Actuator 依赖就位（具体暴露哪些端点受 `management.endpoints.web.exposure.include` 影响，可按需添加）
- Resilience4j + Feign + Eureka Security

## 如何实现

- 在需要监控的模块 POM 增加 `spring-boot-starter-actuator`
- 生产环境应限制 Actuator 暴露范围，本教学项目以本地为准

## 建议启动与验证

1. 启动服务后访问 `http://localhost:7778/actuator/health`（Provider）
2. 确认 Eureka 实例状态页链接（若配置了 `status-page-url-path`）

## 与后续课程

- **第 19 课**：增加 **Turbine 课位模块** 与第二个 Consumer 身份。
