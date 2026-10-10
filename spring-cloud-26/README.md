# 第 26 课 · Nacos + Gateway + OpenFeign

## 学习目标

- 在 **Nacos** 注册中心下，用 **Spring Cloud Gateway** 的 `lb://服务名` 做路由（对标第 23 课 Eureka 版）
- Consumer 通过 **OpenFeign** 调用 Provider，并启用 **Resilience4j 熔断 + fallback**
- 理解「网关 → 消费者(Feign) → 提供者」与「网关 → 提供者」两条链路

## 前置课

- [第 25 课](../spring-cloud-25/README.md)：Nacos 注册与配置入门
- [第 23 课](../spring-cloud-23/README.md)：Gateway + Feign（Eureka）对照

## 模块结构

| 模块 | 端口 | 说明 |
|------|------|------|
| Nacos | 8848 | 注册中心（Compose 独立容器） |
| `spring-cloud-26-provider` | 7777 | REST `/api/user/{id}` |
| `spring-cloud-26-consumer` | 8888 | Feign 入口 `/feign/user/{id}` |
| `spring-cloud-26-gateway` | 9876 | 路由转发 |
| `spring-cloud-26-api` | — | `@FeignClient` + fallback |

## 核心功能

1. **Gateway 路由**（`application.properties`）  
   - `/api/**` → `lb://spring-cloud-26-provider`  
   - `/feign/**` → `lb://spring-cloud-26-consumer`  
2. **OpenFeign**：`IUserBiz` 指向 `spring-cloud-26-provider`  
3. **熔断降级**：`spring.cloud.openfeign.circuitbreaker.enabled=true` + `UserFeignFallback`

## 建议启动与验证

1. 启动 Nacos → Provider → Consumer → Gateway（或 Docker 一键）  
2. **直连 Provider（经网关）**：`GET http://localhost:9876/api/user/1`  
3. **Feign（经网关）**：`GET http://localhost:9876/feign/user/1`  
4. 停止 Provider 后再次请求 `/feign/user/1`，应看到 fallback JSON  
5. Nacos 控制台 **服务列表** 中应有 gateway / provider / consumer 三个服务

## 与第 27 课

- 本课侧重 **网关 + 声明式调用**  
- [第 27 课](../spring-cloud-27/README.md) 侧重 **同服务名多实例 + Nacos 权重**

## Docker 一键启动

本课已提供 **Docker Compose**（含 Nacos、初始化配置脚本、Provider、Consumer），无需本地安装 JDK/Maven 即可启动演示（首次会镜像内 Maven 编译，耗时较长）。

```bash
cd spring-cloud-26
docker compose up --build -d
```

- 查看日志：`docker compose logs -f`
- 停止：`docker compose down -v`
- 验证：Gateway http://localhost:9876/api/user/1 与 http://localhost:9876/feign/user/1；Nacos http://localhost:8848/nacos

> Compose 会通过 `nacos-init` 自动写入演示配置；应用通过环境变量 `NACOS_SERVER_ADDR=nacos:8848` 连接注册/配置中心。
