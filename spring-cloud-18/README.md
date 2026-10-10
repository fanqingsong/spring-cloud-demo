# 第 18 课 · Actuator 监控

## 一句话先懂

业务接口回答「给用户什么数据」；**Actuator 回答「这个进程自己还好不好」**。K8s 探活、Eureka 状态页、后面的监控大盘，用的都是这扇窗，而不是去调 `/api/user/1` 碰运气。

第 04 课已经碰过 Actuator 和 `/info`。本课在「后半段五模块模板」上把它当作**监控依赖**再强调一遍，并为 19 课的「监控聚合」占位做铺垫。

## 学习目标

- 知道 Actuator 是 **spring-boot-starter-actuator**，不是 Eureka 的一部分
- 能访问 `/actuator/health` 判断进程存活
- 理解生产环境必须**限制暴露哪些端点**（本教学项目从简）
- 继续沿用前课的 Feign fallback + RestTemplate 熔断，本课不新增调用方式

## 本课在整条链路里的位置

| 课 | 和监控的关系 |
|----|----------------|
| 04 | 第一次引入 Actuator、构建信息、状态页路径 |
| **本课** | 在综合工程里把依赖「摆正」，用 health 做验证 |
| 19 | 原视频用 Turbine 聚合多条熔断流；本仓库改为 Actuator 占位模块 |

---

## 知识点讲解

### 1. Actuator 端点：给机器读的 HTTP

**是什么**

引入依赖后，应用在业务端口之外（默认同一端口、`/actuator` 前缀）暴露一组管理接口，例如：

| 端点 | 作用 |
|------|------|
| `/actuator/health` | 活着吗、磁盘/DB 是否 down（本课主要用这个） |
| `/actuator/info` | 自定义信息、构建坐标（04 课的 `info.build.*`） |
| `/actuator/metrics` | 内存、QPS 等指标（本课不展开） |

**有什么用**

- 编排系统：进程起了但 Spring 还没就绪时，不要接流量
- 注册中心：点实例名跳到状态页
- 监控：后面接 Micrometer + Prometheus，而不是解析业务 JSON

**本课怎么体现**

Provider、Consumer 的 POM 都有 Actuator。properties **没有**写 `management.endpoints.web.exposure.include`。Spring Boot 3 默认至少暴露 `health`。所以验证请走：

```text
http://localhost:7778/actuator/health
http://localhost:8888/actuator/health
```

若 04 课那种 `/info` 404，原因见第 04 课 README「Boot 3 路径差异」。

### 2. 为什么生产不能把 Actuator 全部敞开

`/actuator/env`、`/actuator/heapdump` 能看到环境变量和内存快照。教学项目在本地无所谓；生产必须：

- 只暴露 health / info / prometheus 等必要项
- 单独管理端口或加认证
- 不要把 dump 端点挂到公网

本课不演示这些加固，但概念要先建立。

### 3. 和熔断、负载的关系

本课 Consumer 仍是：

- `GET /user/{id}` + `@CircuitBreaker` → 兜底 `"自定义信息"`
- `GET /feign/user/{id}` + `RcFeignFallback`
- properties 再次启用 RandomRule（Compose 仍常为单 Provider）

Actuator **不替代**熔断。健康检查说「进程还在」，熔断说「最近调用失败率太高」。一个看进程，一个看调用质量。

Provider 端口从 17 课的 `0` **改回固定 7778**，方便你记住 health 地址。

---

## 模块结构

五模块 `*-18`。无 Gateway、无 Turbine。

## 建议启动与验证

1. 启动后访问两个 health 地址，应返回 `"status":"UP"`
2. 业务：`curl http://localhost:8888/user/1`、`/feign/user/1`
3. Eureka 控制台点实例，看状态页链接是否指向你配置的 path（本系列多为 `/info`）

## 与后续课程

- **第 19 课**：多一个 Consumer 身份 + 名为 turbine 的模块（升级后只是又一个 Actuator 进程）

## Docker 一键启动

```bash
cd spring-cloud-18
docker compose up --build -d
```

- 日志：`docker compose logs -f`
- 停止：`docker compose down -v`
- 验证：`curl http://localhost:7778/actuator/health`
- Eureka：[http://localhost:8761](http://localhost:8761)，`roncoo` / `123456`
