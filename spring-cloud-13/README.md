# 第 13 课 · 多模块综合（Feign 工程化）

## 一句话先懂

本课**几乎没有新组件**。它把第 12 课已经串好的能力，换成 `*-13` 这套固定目录名，作为后半段（熔断、网关、监控）的**标准底板**。重点是「你会不会启动一个五模块工程」，不是再学一个中间件。

## 学习目标

- 能独立完成：编译 → 起 Eureka → 起 Provider → 起 Consumer → 用 Feign 调通
- 再认一次：bean / api / 可运行模块的边界
- 知道后半段课都从这套结构上「加依赖、加注解」，而不是推倒重来

## 本课在整条链路里的位置

课程从这里进入「完整小系统」叙事。14 课起在 **同一个骨架**上加保险丝；20 课起在骨架外再加网关。

---

## 知识点讲解

### 1. 「综合课」在教工程，不在教新协议

**是什么**

五模块：

| 模块 | 端口 | 角色 |
|------|------|------|
| `spring-cloud-bean-13` | — | `User`、`UserService` 契约 |
| `spring-cloud-api-13` | — | `IUserBiz` 等 Feign |
| `spring-cloud-service-13` | 8761 | Eureka（`roncoo` / `123456`） |
| `spring-cloud-provider-13` | 7778 | REST 实现 |
| `spring-cloud-consumer-13` | 8888 | RestTemplate + Feign |

技术点和 12 课同类：OpenFeign、契约、压缩、debug 日志、`RandomRule` 属性。`RoncooCustomRule` 类可能还在工程里，但 properties 用的是 RandomRule。

**有什么用**

后面加熔断时，你不会同时面对「模块不会拆」和「注解不会用」两座山。先把工程跑顺，再叠加 Resilience4j。

### 2. 父 POM 聚合

`spring-cloud-13` 继承仓库根 POM，并在 `dependencyManagement` 里管理 bean、api 版本。日常编译：

```bash
mvn -pl spring-cloud-13 -am compile
```

`-am` 会把依赖的模块一并编进来。只点 Consumer 主类、却没先编 api，是这套工程最常见的启动失败原因。

### 3. 本课没有的东西（避免期待错位）

- **没有** `@CircuitBreaker`（14 课）
- **没有** Feign `fallback` 类
- **没有** Gateway
- Compose **只有一台** Provider，`/user/2/{id}` 默认不可用
- `IRoncooBiz` 仍可能访问外网，和 12 课一样

对外能用的验证口：

```text
GET http://localhost:8888/user/1
GET http://localhost:8888/feign/user/1
GET http://localhost:7778/api/user/1
GET http://localhost:7778/api/user/find/1
```

---

## 建议启动与验证

1. `mvn -pl spring-cloud-13 -am compile`
2. service → provider → consumer
3. 上述四个 URL 都应返回 User 相关 JSON（Feign 那条还会顺带打外部页面，见 12 课说明）

## 与后续课程

- **第 14 课**：在 `UserController` 的 RestTemplate 调用上加熔断和 fallback 方法

## Docker 一键启动

```bash
cd spring-cloud-13
docker compose up --build -d
```

- 日志：`docker compose logs -f`
- 停止：`docker compose down -v`
- 验证：`curl http://localhost:8888/feign/user/1`
- Eureka：[http://localhost:8761](http://localhost:8761)，`roncoo` / `123456`
