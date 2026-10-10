# 第 17 课 · Provider 随机端口

## 一句话先懂

前面每台 Provider 都在 properties 里写死 `7778`。一台电脑要再开一个同样的进程，就会「端口被占用」。`server.port=0` 的意思是：**启动时向操作系统要一个空闲端口**，自己是几号，再登记到 Eureka。调用方仍然只认服务名，根本不关心端口是多少。

## 学习目标

- 理解 `server.port=0` 不是「关掉端口」，而是「随机可用端口」
- 能在 Eureka 控制台看到**两条**同名实例、端口不同
- 体会：Consumer 代码一行不用改，因为 URL 里写的是服务名
- 顺带看到本课 Feign 已配置 `fallback = RcFeignFallback`（比 14 课多出来的保护）

## 本课在整条链路里的位置

云环境和容器里，端口经常是编排系统分配的。本课用最小改动模拟这一点。18 课再把 Actuator 当作监控依赖正式引入（其实前几课 POM 里已经出现过）。

---

## 知识点讲解

### 1. `server.port=0`：让操作系统发号

**是什么**

Spring Boot 里 `0` 是特殊值：绑定到一个随机空闲端口。启动日志里会出现 `Tomcat started on port(s): 4xxxx`。Eureka 注册的是**实际端口**，不是字面量 0。

**有什么用**

- 同一台机器、同一个 jar，用 IDE 点两次运行，不再改配置
- 和容器「映射随机主机端口」的思路一致：进程内不假设自己永远是 7778

**不是什么**

不是「不提供 HTTP」。没有端口就没有 Web。只是端口到运行时才知道。

Docker Compose 本课为了方便你在宿主机 curl，反而用环境变量写成了 `7778` 和 `7779` 两个固定映射。**「随机」更适合本地把 Provider 主类跑两遍**；Compose 演示的是「同 jar、两容器、两端口」。

### 2. 调用方为什么无感

Consumer 写的是：

```text
http://spring-cloud-provider/api/user/{id}
```

LoadBalancer 问 Eureka：「这个名字现在有哪些 IP:端口？」再选一台。Provider 今天是 7778 还是 45123，不出现在 Consumer 代码里。这正是 02 课「不要写死地址」的完整兑现。

### 3. 本课 Feign 开始有降级类

`IUserBiz` 声明了 `fallback = RcFeignFallback.class`。演示入口改为返回 `User`：

```text
GET /feign/user/{id}  →  userBiz.find(id)  →  GET /api/user/find/{id}
```

停 Provider 后，Feign 走 fallback（实现里对 `view1` 会给 `"system error"` 一类兜底；`find` 的兜底以 `RcFeignFallback` 源码为准）。RestTemplate 路径仍是 14 课那套 `"自定义信息"`。

properties 里可能看到 `feign.hystrix.enabled=false` 等 Hystrix 遗留项，**没有对应依赖**，可当历史注释读。本课 RandomRule 属性整段注释掉了，负载用框架默认策略即可。

---

## 模块结构

| 模块 | 端口 | 说明 |
|------|------|------|
| service-17 | 8761 | Eureka |
| provider-17 | **properties 为 0**；Compose 为 7778 与 7779 各一容器 | 同名 `spring-cloud-provider` |
| consumer-17 | 8888 | 熔断 + Feign fallback |
| bean / api | — | 同前 |

## 建议启动与验证

**本地看随机端口**

1. 启动 Eureka
2. IDE 把 `ProviderApplication` 跑**两遍**
3. 控制台出现两条 `spring-cloud-provider`，端口是两个不同的随机数
4. `curl http://localhost:8888/user/1` 多次，负载到不同实例

**Compose**

控制台仍是两条实例，端口是 7778 / 7779（被环境变量固定，便于映射）。

## 与后续课程

- **第 18 课**：把 Actuator 当成「监控课」再讲一次 health 端点

## Docker 一键启动

```bash
cd spring-cloud-17
docker compose up --build -d
```

- 日志：`docker compose logs -f`
- 停止：`docker compose down -v`
- 验证：Eureka [http://localhost:8761](http://localhost:8761) 应看到两个 `spring-cloud-provider`
- 账号：`roncoo` / `123456`
