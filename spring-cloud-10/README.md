# 第 10 课 · OpenFeign 声明式调用

## 一句话先懂

RestTemplate 每次都要手写 URL、HTTP 方法、返回类型。Feign 让你**只声明一个 Java 接口**，框架生成实现：看起来像调本地方法，实际仍是 HTTP + 服务发现 + 负载均衡。

## 学习目标

- 理解「声明式」：接口 + 注解 = 远程调用，没有手写 client 实现类
- 会用 `@EnableFeignClients` 和 `@FeignClient("服务名")`
- 能对比同一课里 **RestTemplate 路径**和 **Feign 路径**
- 知道 `spring.cloud.openfeign.circuitbreaker.enabled=true` 只是**打开熔断开关**，本课还没有降级方法

## 本课在整条链路里的位置

| 课 | 调用怎么写 |
|----|------------|
| 06～09 | 手写 `restTemplate.getForObject("http://服务名/...")` |
| **本课** | **Consumer 内新增 `IUserBiz` 接口** |
| 11 | 把这个接口抽到独立 api 模块，给多人复用 |

---

## 知识点讲解

### 1. OpenFeign：用接口描述「我要调谁的哪个 HTTP」

**是什么**

```java
@FeignClient("spring-cloud-provider")
public interface IUserBiz {
    @GetMapping("/api/user/{id}")
    String view(@PathVariable("id") int id);
}
```

启动时，OpenFeign 为这个接口生成代理对象。你 `@Autowired IUserBiz` 再 `userBiz.view(1)`，代理会：

1. 用服务名 `spring-cloud-provider` 做发现和负载均衡（和 RestTemplate 同一套）
2. 拼出 `GET /api/user/1`
3. 把响应体塞进返回值

**有什么用**

- URL 不会在 Controller 里散落成字符串
- 参数用 `@PathVariable` / `@RequestParam`，和写 Spring MVC 几乎一样
- 多个调用方可以共享同一份接口（第 11 课）

**生活类比**

RestTemplate 像每次打电话都自己拨号、自己说「我要转某某分机」。Feign 像前台给你一张「技术部对内分机表」，你只写「找张三」，后面的拨号由前台完成。

### 2. `@EnableFeignClients`：扫描并注册这些接口

**是什么**

加在 Consumer 启动类上，告诉 Spring：「去扫 `@FeignClient`，做成 Bean。」扫不到，注入 `IUserBiz` 就会失败。

本课接口和启动类在同一个工程里，默认扫描就能找到。第 11 课接口跑到别的 jar，要保证包名能被扫到，或写明 `basePackages`。

### 3. 和 RestTemplate 并存，方便对照

本课故意留了两套入口：

| 入口 | 实现 | 最终打到 Provider |
|------|------|-------------------|
| `GET /user/{id}` | RestTemplate | `/api/user/{id}` |
| `GET /feign/user/{id}` | `IUserBiz.view` | 同样是 `/api/user/{id}` |

对外路径不同，**后端是同一个接口**。多请求几次，两边都应在无境1 / 无境2 间切换（本课 properties 给 provider 配了 RandomRule）。

`/user/2/{id}` 仍指向 `spring-cloud-provider2`，本课 Compose **没有**这套实例，默认会失败。

### 4. `circuitbreaker.enabled=true` 不等于已经会降级

**是什么**

这行配置表示：Feign 调用可以交给 Spring Cloud CircuitBreaker（本仓库是 Resilience4j）包一层。

**本课还没有** `fallback` 类。开关打开后，下游挂了，你看到的仍是报错，而不是友好的兜底数据。真正的降级从第 14 课（RestTemplate）和第 17 课（Feign fallback）开始讲。

把它理解成：「预留了保险丝盒，还没装保险丝。」

---

## 模块结构

| 模块 | 端口 | 说明 |
|------|------|------|
| `spring-cloud-10-service` | 8761 | Eureka |
| `spring-cloud-10-provider-01/02` | 7778 / 7779 | 同名 `spring-cloud-provider` |
| `spring-cloud-10-consumer` | 8888 | 内含 `IUserBiz`、`FeignUserController` |

依赖：`spring-cloud-starter-openfeign`。`IUserBiz` 的 `value` 必须等于 Provider 的 `spring.application.name`。

## 建议启动与验证

1. 启动 Eureka、两台 Provider、Consumer
2. `curl http://localhost:8888/user/1`（RestTemplate）
3. `curl http://localhost:8888/feign/user/1`（Feign）
4. 两边都应返回 User 的 JSON 字符串；对比日志，Feign 路径不再出现手写 URL

## 与后续课程

- **第 11 课**：Feign 接口和实体拆到 api / bean 模块，这是企业里更常见的结构

## Docker 一键启动

```bash
cd spring-cloud-10
docker compose up --build -d
```

- 日志：`docker compose logs -f`
- 停止：`docker compose down -v`
- 验证：`curl http://localhost:8888/feign/user/1`
- Eureka：[http://localhost:8761](http://localhost:8761)，`roncoo` / `123456`
