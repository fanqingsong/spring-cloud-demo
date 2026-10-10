# 第 12 课 · Feign 契约与客户端配置

## 学习目标

- 用 **`UserService` 接口** 作为 Provider 与 Feign 的**共同契约**
- 使用 **`RcFeignConfiguration`** 配置 Feign 日志级别等
- 了解 **`@FeignClient(url=...)`** 固定 URL（不走 Eureka）与 **请求/响应压缩**

## 本课讲什么

在 11 课模块化基础上，强调**接口契约下沉**（DDD/API 先行）：Provider 的 `FeignApiUserController implements UserService`，Feign 的 `IUserBiz extends UserService`，保证路径一致。并演示 Feign 调试日志与 gzip 压缩配置。

## 模块结构

五模块：`bean`、`api`、`service`、`provider-01`、`consumer`（与 11 课同构）。

## 核心功能

1. **UserService**（bean 模块）：定义 `/api/user/find/{id}` 等契约方法
2. **IUserBiz extends UserService**：`@FeignClient(..., configuration = RcFeignConfiguration.class)`
3. **IRoncooBiz**：`url = "http://www.roncoo.com"` 直连外部站点（教学示例）
4. **RcFeignConfiguration**：`Logger.Level.FULL`
5. **properties**：`logging.level.com.roncoo.education.feign=debug`、`feign.compression.request/response.enabled=true`

## 如何实现

- 契约接口放在 **bean**，Feign 继承并加 `@FeignClient`
- Provider 实现同一接口，避免 Feign 路径与 Controller 不一致

## 建议启动与验证

1. 启动全套服务
2. 调用 `find`、`view1` 等接口
3. 打开 debug 日志观察 Feign 请求/响应行

## 与后续课程

- **第 13 课**：相同能力，换 `-13` 聚合工程命名，进入「后半段」综合练习。
- **第 14 课**：在 Consumer 增加 **Resilience4j 熔断**。

        ## Docker 一键启动

        本课已提供 **Docker Compose**，无需本地安装 JDK/Maven 即可启动演示（首次会镜像内 Maven 编译，耗时较长）。

        ```bash
        cd spring-cloud-12
        docker compose up --build -d
        ```

        - 查看日志：`docker compose logs -f`
        - 停止：`docker compose down -v`
        - 验证：Eureka：http://localhost:8761（`roncoo` / `123456`）；Consumer：http://localhost:8888
- Eureka 控制台默认账号：`roncoo` / `123456`

        > 容器内已通过环境变量将 Eureka 地址改为 `eureka`（或第 05 课集群 hostname），并开启 `prefer-ip-address` 以便服务间调用。
