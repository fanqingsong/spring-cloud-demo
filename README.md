## 项目地址汇总
### Spring Cloud Demo：[码云地址](https://gitee.com/roncoocom/spring-cloud-demo) | [Github地址](https://github.com/roncoo/spring-cloud-demo)
### Spring Boot Demo：[码云地址](https://gitee.com/roncoocom/spring-boot-demo) | [Github地址](https://github.com/roncoo/spring-boot-demo)

### 本项目为Spring cloud的基础教程

### 学习指南

- **课程总索引**：[docs/课程索引.md](docs/课程索引.md)
- 每一课目录下的 **`README.md`** 含：学习目标、功能说明、实现要点、启动验证（示例：[spring-cloud-06/README.md](spring-cloud-06/README.md)）。

### 课程教学点一览

| 课次 | 代码目录 | 教学点 | 涉及技术 |
| --- | --- | --- | --- |
| 02 | [spring-cloud-02](spring-cloud-02/README.md) | Eureka 最小闭环：注册中心、Provider/Consumer 注册 | `@EnableEurekaServer` / `@EnableEurekaClient` |
| 04 | [spring-cloud-04](spring-cloud-04/README.md) | Eureka Server 参数、实例元数据、Actuator `/info` | Actuator、租约与拉取间隔 |
| 05 | [spring-cloud-05](spring-cloud-05/README.md) | Eureka HTTP 认证、三节点注册中心集群 | Spring Security Basic、多 `defaultZone` |
| 06 | [spring-cloud-06](spring-cloud-06/README.md) | 服务间 REST 调用、同服务名多实例 | `@LoadBalanced RestTemplate`、LoadBalancer |
| 08 | [spring-cloud-08](spring-cloud-08/README.md) | 两个逻辑服务、按服务名配置负载策略 | 多 `application.name`、负载规则属性 |
| 09 | [spring-cloud-09](spring-cloud-09/README.md) | 自定义负载均衡规则 | `RoncooCustomRule`（自定义选实例） |
| 10 | [spring-cloud-10](spring-cloud-10/README.md) | 声明式 HTTP 调用 | OpenFeign、`@FeignClient` |
| 11 | [spring-cloud-11](spring-cloud-11/README.md) | Feign 接口与实体分包（api / bean） | Maven 多模块、Feign 参数映射 |
| 12 | [spring-cloud-12](spring-cloud-12/README.md) | Feign 与 Provider 共享契约、客户端配置 | `UserService` 契约、Feign Logger/压缩、固定 URL |
| 13 | [spring-cloud-13](spring-cloud-13/README.md) | 五模块微服务模板（后半段综合练习） | 同 12，工程命名 `-13` |
| 14 | [spring-cloud-14](spring-cloud-14/README.md) | 服务熔断与降级（RestTemplate） | Resilience4j、`@CircuitBreaker`、fallback |
| 16 | [spring-cloud-16](spring-cloud-16/README.md) | 熔断与负载策略组合 | Resilience4j + RandomRule 等 |
| 17 | [spring-cloud-17](spring-cloud-17/README.md) | Provider 随机端口、多 JVM 多实例 | `server.port=0`、Eureka 多实例 |
| 18 | [spring-cloud-18](spring-cloud-18/README.md) | 微服务监控端点 | Actuator |
| 19 | [spring-cloud-19](spring-cloud-19/README.md) | 多 Consumer、监控聚合（原 Turbine 课） | 第二 Consumer 身份、Turbine 模块→Actuator |
| 20 | [spring-cloud-20](spring-cloud-20/README.md) | API 网关模块引入 | Spring Cloud Gateway（WebFlux） |
| 22 | [spring-cloud-22](spring-cloud-22/README.md) | 网关全局过滤器、Feign 降级 | `GlobalFilter`、Feign `fallback` |
| 23 | [spring-cloud-23](spring-cloud-23/README.md) | 网关路由、OpenFeign 熔断 | `spring.cloud.gateway.routes`、`lb://` |
| 24 | [spring-cloud-24](spring-cloud-24/README.md) | Spring 官方云原生栈综合 | Config、Authorization Server/JWT、Zipkin、Stream/Kafka、SpringDoc |

> **说明**：原视频课次 **01、03、07、15、21** 本仓库无独立代码，请对照视频或跳过。  
> **环境**：JDK 21、Maven 3.9+；根 POM 为 Spring Boot 3.4.7 + Spring Cloud 2024.0.3。

- 教程视频：[免费篇](http://www.roncoo.com/course/view/e4189c9db6474745b5e578983cddd112)
- 教程视频：[Spring boot全集](http://www.roncoo.com/course/view/c99516ea604d4053908c1768d6deee3d#boxTwo)
- 教程视频：[Srping cloud第一季](http://www.roncoo.com/course/view/cc8fbd6749f94f2fa015641ef96b9460#boxTwo)

### 项目文档
- spring-boot-demo [教程文档](http://www.roncoo.com/article/detail/124661)

### 项目说明
- 源码只供学习使用，更多请看视频

### 技术栈升级说明（2026）

本仓库原配套 **Spring Boot 1.5 + Spring Cloud Dalston/Camden + Netflix 全家桶**，其中多项组件已停止演进或从 Spring Cloud 中移除。已整体升级到当前仍维护的组合：

| 原技术 | 现状 | 本仓库替代 |
| --- | --- | --- |
| Spring Boot 1.5 / Java 8 | 已 EOL | **Spring Boot 3.4.7 + Java 21** |
| Spring Cloud Dalston/Camden | 已 EOL | **Spring Cloud 2024.0.3** |
| `spring-cloud-starter-feign` | 已更名 | **`spring-cloud-starter-openfeign`** |
| Netflix Ribbon | 已移除 | **`spring-cloud-starter-loadbalancer`** |
| Netflix Hystrix / Dashboard | 已停止维护 | **Resilience4j**（`spring-cloud-starter-circuitbreaker-resilience4j`） |
| Netflix Zuul 1 | 已停止维护 | **Spring Cloud Gateway** |
| Turbine 聚合监控 | 依赖 Hystrix，已过时 | 模块保留为 **Actuator** 入口；生产环境请用 **Micrometer + Prometheus/Grafana** |
| Eureka | 维护模式，仍可用 | 继续 **`spring-cloud-starter-netflix-eureka-*`**（教学场景足够；新项目可评估 Nacos/Consul） |

- 根目录 `pom.xml` 为 BOM 父工程；**02–12、13–24** 课均已按「一课一文件夹」聚合。
- 配置文件中仍可能保留 **Zuul/Ribbon/Hystrix 注释** 以便对照原视频。
- 完整网关/熔断示例见 **`spring-cloud-23`**（Gateway + Resilience4j + OpenFeign）。
- **Spring 官方栈扩展**见 **`spring-cloud-24`**（Config Server、Authorization Server、Micrometer Tracing/Zipkin、Gateway JWT、Spring Cloud Stream/Kafka、SpringDoc OpenAPI）。详见 [spring-cloud-24/README.md](spring-cloud-24/README.md)。
- 本地编译需 **JDK 21** 与 **Maven 3.9+**：`mvn -pl spring-cloud-24 -am compile`

### 技术交流
* QQ3群: 738785494
* QQ2群: 601146630 (满)
* QQ1群: 213097382 (满)

## 开源项目 
### roncoo-jui-springboot
- 项目地址：[码云地址](https://gitee.com/roncoocom/roncoo-jui-springboot) | [Github地址](https://github.com/roncoo/roncoo-jui-springboot)
- 该项目是为了大家更好地运用Spring Boot的功能，进行实战。
- 如果没有使用过Spring Boot，也是一个学习的好项目。

### roncoo-recharge
- 项目地址：[码云地址](https://gitee.com/roncoocom/roncoo-recharge) | [Github地址](https://github.com/roncoo/roncoo-recharge)
- 具备话费充值、流量充值、话费卡兑换功能；
- 可以拓展其他充值兑换业务，比如虚拟币充值；
- 也适用于支付、鉴权等业务功能的拓展。