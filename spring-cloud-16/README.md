# 第 16 课 · 熔断与负载均衡组合

## 一句话先懂

仓库里**没有第 15 课**代码。16 课不是新中间件，而是把已经学过的两件事放在同一套工程里同时打开：**Resilience4j 熔断**（14 课）+ **按服务名配置的随机负载**（08 课）。用来练习「调用链既要会挑人，又要在人挂了之后会兜底」。

## 学习目标

- 能说清：负载均衡解决「选哪一台」，熔断解决「选完之后失败怎么办」——两者不互相替代
- 对照 14 课，看出本课差异主要在 **properties 是否强调 RandomRule**
- 知道 Docker 默认**只有一台 Provider**，要看随机分布需要自己再起实例

## 本课在整条链路里的位置

14 课把保险丝装上了。本课提醒你：保险丝和选人策略是两条独立配置，可以共存。17 课则换成「随机端口多实例」，更接近云上的启动方式。

---

## 知识点讲解

### 1. 组合意味着什么（以及不意味着什么）

一次 Consumer → Provider 调用的顺序是：

```text
1. LoadBalancer 从 Eureka 列表里挑一台（RandomRule / 轮询 / 自定义）
2. RestTemplate 真正发 HTTP
3. 若失败次数达到阈值，熔断器打开，后续直接走 getFallback
```

**有什么用**

- 只做负载：一台挂了，请求仍可能打到死人身上，直到注册表刷新，而且没有友好返回
- 只做熔断：一台挂了会兜底，但你无法主动把流量分到还活着的兄弟节点（列表里只有一台时更明显）
- 两个都开：有多实例时先尽量选活人；实在不行再降级，避免线程被拖死

本课代码层面的熔断和 14 课相同：`@CircuitBreaker(name = "getUser", fallbackMethod = "getFallback")`，兜底仍是 `"自定义信息"`。Feign **依然没有** fallback。

### 2. 和 14 课差在哪

几乎同一份 Consumer。差别主要是教学强调：

```properties
spring-cloud-provider.ribbon.NFLoadBalancerRuleClassName=com.netflix.loadbalancer.RandomRule
spring-cloud-provider2.ribbon.NFLoadBalancerRuleClassName=com.netflix.loadbalancer.RandomRule
```

`RandomRuleConfig` 等 Java 配置文件仍是注释模板，**真正生效的是上面两行**（和 08 课一样）。工程里也没有现成的 `spring-cloud-provider2` 实例。

### 3. 想看「随机」必须有两台以上

Compose 只起 1 个 Provider 时，随机规则没有第二台可选，看起来和没配规则一样。本地 IDE 再启动一个同名、不同端口的 Provider，或改 Compose 加副本，再多次 `curl /user/1`，才能看到 name 变化。

熔断实验则不需要两台：停掉那唯一的 Provider，`/user/1` 应回 `"自定义信息"`。

---

## 模块结构

五模块 `*-16`，端口 8761 / 7778 / 8888。

## 建议启动与验证

1. 按 14 课先验证熔断（停 Provider → 兜底文案）
2. 若要看随机：再起一个 `spring-cloud-provider` 实例，多次请求 `/user/1`
3. 不要用 `/user/2/{id}` 当主实验（provider2 默认不在）

## 与后续课程

- **第 17 课**：`server.port=0`，同一份 Provider 程序启动多次也不撞端口

## Docker 一键启动

```bash
cd spring-cloud-16
docker compose up --build -d
```

- 日志：`docker compose logs -f`
- 停止：`docker compose down -v`
- 验证：`curl http://localhost:8888/user/1`；停 provider 容器后再请求应看到兜底
- Eureka：[http://localhost:8761](http://localhost:8761)，`roncoo` / `123456`
