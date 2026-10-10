# 第 25 课 · Nacos 注册发现与配置中心

## 学习目标

- 用 **Nacos** 替代 Eureka，完成「注册中心 + Provider + Consumer」最小闭环
- 掌握 Nacos **配置管理**：`Data ID` / `Group` / **共享配置**、`spring.config.import`、**动态刷新**
- 了解 Nacos 控制台还可演示的 **命名空间、实例权重、元数据、配置历史** 等能力

## 与 Eureka 课（02 / 04 / 05）的对照

| 能力 | Eureka 课 | 本课（Nacos） |
|------|-----------|----------------|
| 服务注册与发现 | `@EnableEurekaServer` / Client | `@EnableDiscoveryClient` + `spring-cloud-starter-alibaba-nacos-discovery` |
| 注册中心进程 | 自建 Eureka Server 模块 | **独立 Nacos Server**（Docker 或本地安装） |
| 配置中心 | 无（见第 24 课 Spring Cloud Config） | **同一套 Nacos** 的 Config 模块 |
| 控制台 | Eureka Dashboard | Nacos 控制台（服务列表 + 配置管理） |

## 模块结构

| 模块 | 默认端口 | 角色 |
|------|----------|------|
| Nacos Server | 8848 | 注册 + 配置（Compose 中独立容器） |
| `spring-cloud-25-provider` | 7777 | 注册、读配置、REST API |
| `spring-cloud-25-consumer` | 8888 | 注册、读配置、`RestTemplate` 按服务名调用 Provider |

## 本课覆盖的 Nacos 功能

### 1. 服务注册与发现（对标第 02 / 06 课）

- 依赖：`spring-cloud-starter-alibaba-nacos-discovery` + `spring-cloud-starter-loadbalancer`
- Consumer 使用 `@LoadBalanced RestTemplate`，URL 为 `http://spring-cloud-nacos-provider/...`
- 在 Nacos 控制台 **服务管理 → 服务列表** 查看实例与健康状态

### 2. 配置管理（Nacos 特有，Eureka 不具备）

- 依赖：`spring-cloud-starter-alibaba-nacos-config`
- Boot 3 使用 **`spring.config.import`** 拉取配置（不再使用 bootstrap.yml）
- 演示三类配置源：
  - **应用私有**：`spring-cloud-nacos-provider.properties` / `spring-cloud-nacos-consumer.properties`（`DEFAULT_GROUP`）
  - **共享配置**：`spring-cloud-nacos-common.properties`（`Group = SHARED`）
- **`@RefreshScope` + `@ConfigurationProperties`**：配置变更后自动刷新（`?refresh=true`）
- 备用：手动触发 **`POST /actuator/refresh`**

### 3. 控制台可继续体验的 Nacos 能力（README 实验步骤）

| 功能 | 说明 |
|------|------|
| **命名空间（Namespace）** | 环境隔离；本地可设 `NACOS_NAMESPACE=<uuid>` 并在控制台创建同名空间 |
| **Group** | 本课共享配置使用 `SHARED`，与默认组区分 |
| **实例元数据** | Provider 配置了 `spring.cloud.nacos.discovery.metadata.*`，可在实例详情查看 |
| **权重（Weight）** | 多实例同服务名时，在控制台调权重，配合 LoadBalancer 观察流量倾斜 |
| **配置历史与回滚** | 配置列表 → 历史版本 → 回滚 |
| **监听查询** | 查看哪些客户端在监听某 Data ID（排查刷新问题） |

> **未在本课写代码、但与 Spring Cloud 衔接的能力**：Gateway `lb://服务名`（见第 23 课，仅把注册中心换成 Nacos）、OpenFeign + Nacos（见第 10 课模式）、Nacos 认证与集群部署（生产运维向，见 [Nacos 官方文档](https://nacos.io/docs/latest/)）。

## 核心实现要点

**Provider / Consumer 公共配置片段**：

```properties
spring.cloud.nacos.server-addr=${NACOS_SERVER_ADDR:127.0.0.1:8848}
spring.config.import=optional:nacos:${spring.application.name}.properties?refresh=true,\
optional:nacos:spring-cloud-nacos-common.properties?group=SHARED&refresh=true
```

**验证用 HTTP 接口**：

| 地址 | 说明 |
|------|------|
| `GET http://localhost:8888/user/1` | Consumer 经 Nacos 发现调用 Provider |
| `GET http://localhost:8888/config/local` | Consumer 侧当前 Nacos 配置快照 |
| `GET http://localhost:7777/api/config/snapshot` | Provider 侧配置快照 |
| Nacos 控制台 | http://localhost:8848/nacos （默认 `nacos` / `nacos`；本课 Docker **关闭鉴权** 便于学习） |

## 建议启动与验证（本地 Maven）

1. 启动 Nacos（推荐直接用本课 Docker 只起 Nacos：`docker compose up -d nacos nacos-init`）
2. 在 Nacos **配置管理** 中创建与本课 `nacos/init-config.sh` 相同的三份配置（若已跑过 `nacos-init` 可跳过）
3. 启动 `spring-cloud-25-provider`、`spring-cloud-25-consumer`
4. 访问 `http://localhost:8888/user/1`，JSON 中应含 `greeting` 字段
5. 在控制台修改 `spring-cloud-nacos-provider.properties` 中的 `provider.greeting`，保存后再次请求，观察 **无需重启** 即可生效
6. （可选）修改 `spring-cloud-nacos-common.properties`（`SHARED` 组），调用 `/config/local` 验证共享配置刷新

## 与后续课程

- 已学过 **第 06 课** RestTemplate 调用方式，本课仅把「找服务」从 Eureka 换成 Nacos
- **[第 26 课](../spring-cloud-26/README.md)**：Nacos + Gateway + OpenFeign（对标第 23 课）
- **[第 27 课](../spring-cloud-27/README.md)**：同服务名双 Provider + Nacos 权重与命中统计
- **第 24 课** Spring Cloud Config 侧重 Git/本地文件；Nacos Config 适合 **集中配置 + 控制台改配 + 多环境命名空间**
- 生产环境请开启 **Nacos 鉴权**、持久化（MySQL）与集群，勿使用本课「关闭鉴权」的 Compose 配置

## Docker 一键启动

本课已提供 **Docker Compose**（含 Nacos、初始化配置脚本、Provider、Consumer），无需本地安装 JDK/Maven 即可启动演示（首次会镜像内 Maven 编译，耗时较长）。

```bash
cd spring-cloud-25
docker compose up --build -d
```

- 查看日志：`docker compose logs -f`
- 停止：`docker compose down -v`
- 验证：Nacos http://localhost:8848/nacos；Consumer http://localhost:8888/user/1；配置快照 http://localhost:8888/config/local

> Compose 会通过 `nacos-init` 自动写入演示配置；应用通过环境变量 `NACOS_SERVER_ADDR=nacos:8848` 连接注册/配置中心。
