# 第 25 课 · Nacos 注册发现与配置中心

## 一句话先懂

前面十几课，**通讯录**是 Eureka，**配置文件**要么在 jar 里，要么在第 24 课的 Config Server。Nacos 把这两件事放进**同一个产品**：控制台既能看服务列表，也能改配置并推给客户端。模型没变，换了一家实现。

## 学习目标

- 能对照 Eureka 课，说出 Nacos 里「服务名 / 实例 / 发现」分别对应什么
- 掌握 Data ID、Group、共享配置、`spring.config.import`
- 理解 `@RefreshScope`：控制台改一句，接口里的字马上变，不必重启
- 知道命名空间、权重、元数据是控制台能力，本课代码只演示了其中一部分

## 与 Eureka 课（02 / 04 / 05）的对照

| 能力 | Eureka 课 | 本课 |
|------|-----------|------|
| 服务怎么找到彼此 | Eureka Server 模块 | **独立 Nacos 进程**（Docker 或安装包） |
| 客户端怎么接入 | `eureka-client` + `defaultZone` | `nacos-discovery` + `server-addr` |
| 配置中心 | 无（见 24 课 Config） | **同一套 Nacos** |
| 控制台 | 8761 那张表 | `http://localhost:8848/nacos` |

---

## 知识点讲解

### 1. Nacos 作为注册中心

**是什么**

Provider / Consumer 启动后向 `127.0.0.1:8848`（Compose 里是 `nacos:8848`）登记。Consumer 使用 `@LoadBalanced RestTemplate`，URL 为：

```text
http://spring-cloud-nacos-provider/api/user/{id}
```

主机名必须等于对方的 `spring.application.name`，和 Eureka 课完全一样。

**有什么用**

你已经熟悉的「按服务名调用」可以原样搬过来。差别是：不必自己写一个 `*-service` 模块当注册中心，Nacos 是现成服务器。

控制台：**服务管理 → 服务列表**。Provider 还带了元数据 `version=1.0`、`region=local`，点实例详情能看见。元数据类似 04 课的标签，默认不改变怎么选实例。

### 2. Nacos 作为配置中心

**是什么**

配置不再只靠本地文件。Boot 3 用 `spring.config.import` 拉取（老视频里的 `bootstrap.yml` 可以忘掉）：

```properties
spring.config.import=optional:nacos:${spring.application.name}.properties?refresh=true,\
optional:nacos:spring-cloud-nacos-common.properties?group=SHARED&refresh=true
```

三个词：

| 词 | 是什么 | 本课例子 |
|----|--------|----------|
| **Data ID** | 一份配置的文件名 | `spring-cloud-nacos-provider.properties` |
| **Group** | 文件的分组，避免重名 | 应用私有用默认组；共享用 `SHARED` |
| **Namespace** | 更大的隔离（常用来分环境） | 本课默认 public，可用 `NACOS_NAMESPACE` |

`optional:` 表示 Nacos 暂时连不上时应用仍能启动（用本地默认值），避免「配置中心一抖，所有服务起不来」。

**有什么用**

- 应用私有：问候语、实例标签
- 共享组：课程标签这种「很多服务都该一样」的项，改一次全员受益

`nacos-init` 容器会把三份演示配置自动写入，免去你在控制台从零新建。

### 3. 动态刷新：改完立刻用

**是什么**

配置类加上 `@RefreshScope`（以及 `@ConfigurationProperties`）。`?refresh=true` 让客户端监听 Nacos。控制台点「发布」后，长连接推过来，字段更新。

也可用 `POST /actuator/refresh` 手动刷（本课暴露了 `health,info,refresh`）。

**有什么用**

改一句文案、开关一个功能，不必走发布流水线。当然，改数据源 URL 这种「必须重建连接池」的项，不能幻想全都热更新。

**建议亲手做一次**

1. `curl http://localhost:8888/user/1`，记住 JSON 里的 `greeting`
2. 控制台改 `spring-cloud-nacos-provider.properties` 的 `provider.greeting` 并发布
3. 再 curl，字应已变
4. 再改 `SHARED` 组的 `spring-cloud-nacos-common.properties`，用 `/config/local` 看共享项

### 4. 控制台还可以玩、但本课没写进代码的

| 能力 | 作用 |
|------|------|
| 命名空间 | 一套 Nacos 隔离 dev / prod，避免配错环境 |
| 权重 | 多实例时流量倾斜（**第 27 课专门做**） |
| 配置历史 / 回滚 | 发错配置可以退回 |
| 监听查询 | 看哪些客户端盯着某 Data ID，排查「我改了它怎么不刷新」 |

本课 Docker **关闭 Nacos 鉴权**，图个学习方便。生产必须开鉴权、持久化到 MySQL、并做集群。

---

## 模块结构

| 模块 | 端口 | 应用名 / 角色 |
|------|------|----------------|
| Nacos | 8848 | 注册 + 配置 |
| `spring-cloud-25-provider` | 7777 | `spring-cloud-nacos-provider` |
| `spring-cloud-25-consumer` | 8888 | `spring-cloud-nacos-consumer` |

## 验证用 HTTP

| 地址 | 说明 |
|------|------|
| `GET :8888/user/1` | 经发现调用 Provider |
| `GET :8888/config/local` | Consumer 当前配置快照 |
| `GET :8888/config/via-provider` | 再经 Provider 看一份 |
| `GET :7777/api/config/snapshot` | Provider 快照 |
| 控制台 | http://localhost:8848/nacos |

## 建议启动与验证

1. 推荐直接本课 `docker compose up --build -d`；或先 `up -d nacos nacos-init` 再本地起两个应用
2. 走一遍 `/user/1` 和改配置刷新
3. 对照第 06 课：调用方式没变，只是通讯录换了 Nacos

## 与后续课程

- **[第 26 课](../spring-cloud-26/README.md)**：加上 Gateway + OpenFeign（对标 23）
- **[第 27 课](../spring-cloud-27/README.md)**：双实例 + 权重
- 第 24 课 Config 偏 Git/文件仓库；Nacos 偏控制台改配 + 命名空间

## Docker 一键启动

```bash
cd spring-cloud-25
docker compose up --build -d
```

- 日志：`docker compose logs -f`
- 停止：`docker compose down -v`
- 验证：控制台 8848；`curl http://localhost:8888/user/1`

> `nacos-init` 负责写入演示配置；应用用 `NACOS_SERVER_ADDR=nacos:8848` 连接。
