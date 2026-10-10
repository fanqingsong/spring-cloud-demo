# 第 11 课 · Feign API 模块化

## 一句话先懂

第 10 课把 Feign 接口写在 Consumer 里面，只有这一个调用方方便。企业里常常是「很多个服务都要调用户服务」——接口应该做成**独立的 jar**，谁依赖谁就能调，而不是复制一份接口到每个 Consumer。

## 学习目标

- 理解 Maven 多模块里 **bean（实体） / api（Feign 接口） / 可运行应用** 的分工
- 知道 Consumer **只依赖 api** 就能注入远程接口
- 能看懂 `IUserBiz` 里多种传参写法，以及注释中「哪种会启动失败」
- 会编译：先装 bean/api，再启动应用

## 本课在整条链路里的位置

这是后面「五模块标准模板」的雏形。第 12 课会再往下挖：Provider 和 Feign **实现同一个契约接口**，保证路径永远一致。

---

## 知识点讲解

### 1. 为什么要把 Feign 接口拆出去

**是什么**

| 模块 | 里面有什么 | 能不能独立运行 |
|------|------------|----------------|
| `spring-cloud-11-bean` | `User` 等共享模型 | 否，只是 jar |
| `spring-cloud-11-api` | `@FeignClient` 接口 `IUserBiz` | 否 |
| `spring-cloud-11-provider-01` | 真正的 REST 实现 | 是 |
| `spring-cloud-11-consumer` | 注入 `IUserBiz` 对外再暴露 HTTP | 是 |
| `spring-cloud-11-service` | Eureka | 是 |

**有什么用**

- 改路径或改字段时，只改一处 jar，所有调用方一起升级
- Provider 和 Consumer 不再各自复制一份 `User` 类（字段对不齐是微服务里的常见事故）
- 新人加入只要依赖 api，不必翻 Consumer 源码找「到底调的哪个 URL」

**生活类比**

第 10 课是每个部门自己手抄一份分机表。本课是行政印发**标准分机手册**（api jar），各部门领手册用，手册改版统一换。

### 2. Maven 多模块和 dependencyManagement

**是什么**

父 POM（`spring-cloud-11`）在 `dependencyManagement` 里锁定 `bean`、`api` 的版本。子模块写依赖时通常**不用再写版本号**，避免「Consumer 用 1.0 的 User、Provider 用 1.1 的 User」。

**有什么用**

多模块最怕版本漂移。先 `mvn -pl spring-cloud-11 -am compile`（或 install）保证 api/bean 已被构建，再启动应用，否则 IDE 会提示找不到 `IUserBiz`。

### 3. Feign 传参：看起来像 MVC，细节更严

**是什么**

Feign 使用 Spring MVC 注解，但运行时是「拼 HTTP」，不是「本进程方法调用」。常见坑（接口注释里有反例）：

- GET 却想传一个复杂对象当 `@RequestBody`：很多客户端不支持，或对不上 Provider
- `@PathVariable` / `@RequestParam` **不写名字**，一旦编译没保留参数名，Feign 不知道键叫什么
- 同一个路径用多种参数组合声明，Provider 端要有对应绑定，否则 400/404

**有什么用**

本课 `IUserBiz` 里堆了 `view1`、`get1`、`get2`… 是**对照教材**，不是都要在生产用。真正对外演示的入口仍是：

```text
GET http://localhost:8888/feign/user/{id}  →  userBiz.view1(id)  →  GET /api/user/{id}
```

其余方法多半只写在接口里，Controller 中对应调用是注释状态。阅读时盯着「注释说不要这么写」的那几处，收获比把每个方法都调一遍更大。

### 4. 扫描路径

`IUserBiz` 在 api 模块的 `com.roncoo.education.feign` 包。Consumer 启动类在 `com.roncoo.education` 下，默认扫描子包就能注册 Feign。若你把接口换到奇怪的包名，需要在 `@EnableFeignClients(basePackages=...)` 里写明。

本课 Compose **只有一台 Provider**，看不到双实例负载；`/user/2/{id}` 指向的 provider2 默认不存在。

---

## 模块结构

见上表。Provider 额外有 `GET/POST /api/user/get/{id}`，用来配合那些教学向的传参方法。

## 建议启动与验证

1. `mvn -pl spring-cloud-11 -am compile`
2. 启动 service → provider → consumer
3. `curl http://localhost:8888/feign/user/1`
4. `curl http://localhost:8888/user/1`（仍是 RestTemplate，便于对照）

## 与后续课程

- **第 12 课**：`UserService` 契约、Feign 日志 / 压缩、固定 URL 不走 Eureka

## Docker 一键启动

```bash
cd spring-cloud-11
docker compose up --build -d
```

- 日志：`docker compose logs -f`
- 停止：`docker compose down -v`
- 验证：`curl http://localhost:8888/feign/user/1`
- Eureka：[http://localhost:8761](http://localhost:8761)，`roncoo` / `123456`
