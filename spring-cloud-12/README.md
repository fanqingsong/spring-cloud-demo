# 第 12 课 · Feign 契约与客户端配置

## 一句话先懂

第 11 课保证「调用方共用一份接口」。本课再往前一步：Provider 的 Controller **implements 同一个接口**，路径由接口说了算——这叫**契约**。另外演示 Feign 的日志、gzip 压缩，以及「不走注册中心、写死 URL」的客户端。

## 学习目标

- 理解 **契约接口**：Feign 与 Provider 共同遵守同一组路径和方法签名
- 会给某个 `@FeignClient` 挂上 `configuration = RcFeignConfiguration.class`
- 能打开 Feign **FULL** 日志，看见真实请求行
- 知道 `@FeignClient(url=...)` 会**绕过 Eureka**

## 本课在整条链路里的位置

工程结构和 11 课相同（bean / api / service / provider / consumer）。第 13 课几乎是本课的「换了个文件夹名」的综合练习模板。

---

## 知识点讲解

### 1. 契约（Contract）：先定接口，两边各写实现

**是什么**

```text
bean 模块  UserService
              │
     ┌────────┴────────┐
     │                 │
IUserBiz extends    FeignApiUserController
  UserService         implements UserService
（再加 @FeignClient）  （Provider 真正处理 HTTP）
```

`UserService` 上的 `@GetMapping("/api/user/find/{id}")` 既是 Feign 要拼的路径，也是 Provider 要映射的路径。改一处，两边一起变。

**有什么用**

11 课只保证 Consumer 之间不各写各的。若 Provider 的 Controller 手写了一个稍微不同的路径（多一个斜杠、方法名换了），Feign 仍会 404，而且要运行时才发现。契约把这种错误提前到「编译期：你没实现接口」。

**生活类比**

11 课是「大家都领同一本分机手册」。本课是「总机和分机手册用同一份印刷版」，手册改号码，前台和各部门同时换。

本课 `GET /feign/user/{id}` 会同时打：

- `userBiz.find(id)` → Provider 的 `/api/user/find/{id}`（契约方法）
- `userBiz.view1(id)` → `/api/user/{id}`（接口上额外声明的方法）

### 2. RcFeignConfiguration：只影响这一个 Feign 客户端

**是什么**

`@FeignClient(..., configuration = RcFeignConfiguration.class)` 里指定的配置类。本课它把 Feign 日志级别设为 `Logger.Level.FULL`（请求头、正文都打）。

**有什么用**

联调时最怕「我以为发出去了，对端说没收到」。FULL 日志等于把 HTTP 对话摊在 Consumer 日志里。生产环境通常改回 BASIC 或 NONE，避免把隐私打进日志。

配合：

```properties
logging.level.com.roncoo.education.feign=debug
```

只打开 Feign 接口所在包的 debug，避免整个工程刷屏。

### 3. 请求 / 响应压缩

```properties
feign.compression.request.enabled=true
feign.compression.response.enabled=true
feign.compression.request.min-request-size=2048
```

**是什么**

体超过约 2KB 的 JSON/XML 用 gzip 传，对端再解压。

**有什么用**

内网小 JSON 几乎感觉不到；大报文、跨机房时能省带宽。本课体都很小，**重点是认识开关**，不要指望从 `/feign/user/1` 看出速度差异。

### 4. 固定 URL 的 Feign：不走注册中心

```java
@FeignClient(value = "roncoo", url = "www.roncoo.com")
```

**是什么**

`url` 写死主机后，Feign **不再**用 Eureka 查 `roncoo` 这个名字，而是直接访问该网站。`FeignUserController` 每次还会请求 `course/list.html` 并打印结果。

**有什么用**

调第三方、调还没进注册中心的遗留系统时用。缺点：没有发现、没有本课那种多实例负载；外网不通时，`/feign/user/{id}` 可能被这个外部调用拖慢或拖失败。

教学上把它当成「Feign 不一定绑定 Eureka」的反例即可。

---

## 模块结构

五模块：`spring-cloud-12-bean` / `api` / `service` / `provider-01`（7778） / `consumer`（8888）。

## 建议启动与验证

1. 启动全套
2. `curl http://localhost:8888/feign/user/1`（观察 Consumer 日志里的 Feign FULL 输出）
3. 直连契约接口：`curl http://localhost:7778/api/user/find/1`
4. 若外网访问 `www.roncoo.com` 失败，先看日志里是外部调用超时，再判断是不是 Provider 的问题

## 与后续课程

- **第 13 课**：同样能力，模块改名为 `*-13`，作为后半段固定模板
- **第 14 课**：RestTemplate 上加熔断，下游挂了返回兜底

## Docker 一键启动

```bash
cd spring-cloud-12
docker compose up --build -d
```

- 日志：`docker compose logs -f`
- 停止：`docker compose down -v`
- 验证：`curl http://localhost:8888/feign/user/1`
- Eureka：[http://localhost:8761](http://localhost:8761)，`roncoo` / `123456`
