# 第 06 课 · RestTemplate 与负载均衡调用

## 一句话先懂

前面几课把通讯录建好了。本课第一次认真做**服务之间的业务调用**：Consumer 不写死 IP，只写服务名；Eureka 里同一个名字下挂了 **3 台 Provider**，每次请求由客户端挑一台。

## 学习目标

- 理解 **客户端负载均衡**和「Nginx 那种服务端负载均衡」有何不同
- 会用 `@LoadBalanced RestTemplate`，URL 主机名写成 **服务名**
- 能从返回的 JSON 看出请求落到了「无境1 / 无境2 / 无境3」哪一台

## 本课在整条链路里的位置

| 课 | 调用情况 |
|----|----------|
| 02 | 只有一次 `/hello`，单实例 |
| 04 / 05 | 几乎不讲业务调用 |
| **本课** | **同名三实例 + RestTemplate** |
| 08 | 两个不同服务名，并开始配「怎么挑实例」的规则 |
| 10 | 用 OpenFeign 代替手写 URL |

---

## 知识点讲解

### 1. RestTemplate：Spring 里发 HTTP 的老工具

**是什么**

一个 Java API：`getForObject(url, 返回类型)` 就能发 GET。本课 Consumer 的 `UserController` 用它去调 Provider 的 `/api/user/{id}`。

**有什么用**

微服务之间最常见的同步调用就是 HTTP。RestTemplate 直观，缺点是 URL、HTTP 方法都要自己拼。第 10 课的 Feign 就是为了少写这些模板代码。

对外入口：

```text
GET http://localhost:8888/user/{id}
```

内部再转成对 Provider 的：

```text
GET http://spring-cloud-provider/api/user/{id}
```

### 2. 客户端负载均衡（Spring Cloud LoadBalancer）

**是什么**

- **服务端负载均衡**（如 Nginx）：调用方只认识一个入口，由入口后面分发
- **客户端负载均衡**：调用方自己持有一份实例列表，**在发请求前就选好目标机器**

`@LoadBalanced` 就是给 RestTemplate 接上后者。列表来自 Eureka 本地缓存。

**有什么用**

少一层代理，调用方还能按规则（轮询、随机、自定义）选实例。原课程用的 Netflix Ribbon 已从 Spring Cloud 移除，本仓库用官方 **LoadBalancer**；配置文件里仍可能看到 `*.ribbon.*` 键名，那是为了对照旧视频，从第 08 课开始会碰到。

**生活类比**

点外卖：你可以让平台统一派最近的店（服务端）；也可以自己打开三家分店的电话，轮着打（客户端）。`@LoadBalanced` 属于第二种。

### 3. 同一 `spring.application.name` 的多个实例

**是什么**

`provider-01` / `02` / `03` 三个进程，**应用名都是 `spring-cloud-provider`**，端口分别是 7778、7779、7780。在 Eureka 控制台里，它们出现在**同一行应用**下面，是三列实例。

**有什么用**

这就是水平扩展：加机器不改服务名，Consumer 的 URL 一行都不用动。为了让你「看见」分发效果，三台返回的 `User.name` 分别做成 **无境1 / 无境2 / 无境3**。

多次请求 `http://localhost:8888/user/1`，JSON 里的名字应会在三个值之间切换（默认策略近似轮询，不要要求严格 1-2-3-1-2-3）。

### 4. 为什么主机名必须是服务 ID

错误写法（直连，失去发现和负载）：

```text
http://localhost:7778/api/user/1
```

正确写法：

```text
http://spring-cloud-provider/api/user/1
```

`@LoadBalanced` 只拦截「能在 Eureka 里查到的服务名」。写成 IP 或 localhost，它当普通 HTTP 走，三台机器永远只用你写死的那一台。

代码里还留着已注释的直连 URL，是原视频的对照，不要打开它当正式写法。

---

## 模块结构

| 模块 | 端口 | 应用名 | 说明 |
|------|------|--------|------|
| `spring-cloud-06-service` | 8761 | `spring-cloud-server` | Eureka（带 Security） |
| `spring-cloud-06-provider-01` | 7778 | `spring-cloud-provider` | 返回「无境1」 |
| `spring-cloud-06-provider-02` | 7779 | 同上 | 「无境2」 |
| `spring-cloud-06-provider-03` | 7780 | 同上 | 「无境3」 |
| `spring-cloud-06-provider` | 7777 | 同上 | 可选单实例对照，Compose 不用 |
| `spring-cloud-06-consumer` | 8888 | `spring-cloud-consumer` | 发起调用 |

## 建议启动与验证

1. Eureka → 三个 provider-0x → Consumer
2. 控制台应在 `SPRING-CLOUD-PROVIDER` 下看到 3 个实例
3. 多次执行：`curl http://localhost:8888/user/1`
4. 观察返回 JSON 的 name 是否在无境1/2/3 间变化
5. 对照直连：`curl http://localhost:7778/api/user/1` 会**固定**无境1

账号：Eureka `roncoo` / `123456`

## 与后续课程

- **第 08 课**：再加一套服务名 `spring-cloud-provider2`，并开始用配置指定随机规则
- **第 10 课**：同样的调用改写成 `@FeignClient`

## Docker 一键启动

```bash
cd spring-cloud-06
docker compose up --build -d
```

- 日志：`docker compose logs -f`
- 停止：`docker compose down -v`
- 验证：多次 `curl http://localhost:8888/user/1`，看 name 是否在三个实例间切换
- Eureka：[http://localhost:8761](http://localhost:8761)，`roncoo` / `123456`
