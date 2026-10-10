# 第 11 课 · Feign API 模块化

## 学习目标

- 用 **Maven 多模块** 拆分：`bean`（实体）、`api`（Feign 接口）、`consumer` / `provider` / `service`
- 理解 Consumer **只依赖 api 模块** 即可调用远程服务
- 熟悉 Feign 与 Spring MVC 注解在 **参数传递** 上的常见坑（注释中的错误示例）

## 本课讲什么

企业项目通常不会把 `@FeignClient` 写在 Consumer 里，而是独立 **API  jar** 供多个调用方依赖。本课建立与 13 课以后相同的五模块结构雏形。

## 模块结构

| 模块 | 职责 |
|------|------|
| `spring-cloud-11-bean` | `User` 等共享模型 |
| `spring-cloud-11-api` | `IUserBiz` 等 Feign 接口 |
| `spring-cloud-11-provider-01` | REST 实现 |
| `spring-cloud-11-consumer` | Feign 调用方 |
| `spring-cloud-11-service` | Eureka |

父 POM **`dependencyManagement`** 统一管理 `bean`、`api` 版本。

## 核心功能

1. **IUserBiz**：多种 `@GetMapping` / `@RequestParam` / `Map` 传参写法（含注释说明不推荐用法）
2. **ApiUserController**：Provider 端复杂参数绑定
3. **FeignUserController**：调用 `view1` 等方法

## 如何实现

- Consumer POM 依赖 `spring-cloud-11-api`，不再在 Consumer 内定义 Feign 接口
- api 模块依赖 `openfeign` + `bean`

## 建议启动与验证

1. 根目录或本课目录：`mvn -pl spring-cloud-11 -am compile`
2. 启动 service → provider → consumer
3. 按 `FeignUserController` 路径测试 Feign 调用

## 与后续课程

- **第 12 课**：**UserService 契约**、Feign **Configuration**、日志与压缩。

        ## Docker 一键启动

        本课已提供 **Docker Compose**，无需本地安装 JDK/Maven 即可启动演示（首次会镜像内 Maven 编译，耗时较长）。

        ```bash
        cd spring-cloud-11
        docker compose up --build -d
        ```

        - 查看日志：`docker compose logs -f`
        - 停止：`docker compose down -v`
        - 验证：Eureka：http://localhost:8761（`roncoo` / `123456`）；Consumer：http://localhost:8888
- Eureka 控制台默认账号：`roncoo` / `123456`

        > 容器内已通过环境变量将 Eureka 地址改为 `eureka`（或第 05 课集群 hostname），并开启 `prefer-ip-address` 以便服务间调用。
