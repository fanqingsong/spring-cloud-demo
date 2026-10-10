## 项目地址汇总
### Spring Cloud Demo：[码云地址](https://gitee.com/roncoocom/spring-cloud-demo) | [Github地址](https://github.com/roncoo/spring-cloud-demo)
### Spring Boot Demo：[码云地址](https://gitee.com/roncoocom/spring-boot-demo) | [Github地址](https://github.com/roncoo/spring-boot-demo)

### 本项目为Spring cloud的基础教程

### 学习指南

- **课程总索引**：[docs/课程索引.md](docs/课程索引.md)
- **每一课**进入对应目录阅读 **`README.md`**（如 `spring-cloud-06/README.md`），含：学习目标、功能说明、实现要点、启动验证。

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

- 根目录 `pom.xml` 为 BOM 父工程；章节 **13–23** 已挂到该父 POM 下。
- 第 **2–12** 课与 **13–24** 课目录一致：每课一个文件夹（如 `spring-cloud-02/`、`spring-cloud-11/`），其下为各子模块。
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