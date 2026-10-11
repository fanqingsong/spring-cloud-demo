# 第 14 课 · 服务熔断（Resilience4j）

## 一句话先懂

前面调用都假设 Provider「一定在」。现实里下游会超时、会挂。如果不加保护，Consumer 的线程会全部堵在等待上，再把更上游拖死——这叫**雪崩**。熔断就是给这次调用加一把**保险丝**：连续失败就断开，立刻走兜底逻辑（降级）。

## 学习目标

- 能用自己的话区分：**超时、重试、熔断、降级**各管什么
- 会在 RestTemplate 方法上使用 `@CircuitBreaker` + `fallbackMethod`
- 能对照 `application.properties` 说出 **闭合 → 打开 → 半开** 每一步谁在决策
- 知道原视频的 Hystrix 已停更，本仓库用 **Resilience4j**
- 能用「停掉 Provider 再调 Consumer」验证兜底字符串

## 本课在整条链路里的位置

骨架仍是 13 课的五模块。只在 Consumer 的 **RestTemplate 路径**上加保护。Feign 路径本课**没有** fallback，停 Provider 后 `/feign/user/{id}` 仍会失败——这是刻意对照。

---

## 知识点讲解

### 1. 雪崩：一次故障如何变成全家停电

**是什么**

Consumer 有有限的线程处理用户请求。每个请求若同步等待 Provider 30 秒，只要下游一慢，线程池很快耗尽。新用户进不来，健康的别的接口也被堵死。多个服务彼此调用时，故障会沿调用链向上扩散。

**有什么用（为什么要熔断）**

保险丝跳闸后，短时间内**不再尝试**已经明确有问题的下游，给它恢复时间，也给自己留线程去处理别的事。

**生活类比**

家里短路时，电闸跳开，整屋暂时没电，但不会把电线烧着、连累整栋楼。过一会儿再合闸（半开 / 探测），好了就恢复供电。

### 2. 熔断 vs 降级（两个常被混在一起的词）

| 词 | 是什么 | 本课对应 |
|----|--------|----------|
| 熔断（Circuit Breaker） | 根据失败率决定「继续试 / 直接拒绝」 | `@CircuitBreaker(name = "getUser", ...)` |
| 降级（Fallback） | 拒绝或失败之后**返回什么替代品** | `getFallback` 返回 `"自定义信息"` |

可以熔断但不降级（直接抛错）；也可以降级但不熔断（每次失败都现场 catch）。本课两个一起用：跳闸后给调用方一句友好文本，而不是一堆异常栈。

原课程用 Netflix Hystrix。它已停止维护。注解换成 Resilience4j 的 `@CircuitBreaker`，**启动类不必再写** `@EnableCircuitBreaker`。

配置文件里若还看到 `feign.hystrix.enabled` 之类，是对照旧视频的说明性残留，本课 POM **没有** Hystrix 依赖。

### 3. `@CircuitBreaker` 怎么接到 RestTemplate 上

```java
@CircuitBreaker(name = "getUser", fallbackMethod = "getFallback")
public String get(@PathVariable int id) {
    return restTemplate.getForObject("http://spring-cloud-provider/api/user/{id}", String.class, id);
}

public String getFallback(int id) {   // 参数要能对上，返回类型要兼容
    return "自定义信息";
}
```

**要点**

- `name` 只是这把保险丝的名字，方便日志和监控区分多条调用；**必须和** `resilience4j.circuitbreaker.instances.<name>` **对上**
- fallback 方法必须和原方法在**同一个类**，参数列表兼容（通常多一个 `Throwable` 也可以，以你代码为准）
- 阈值写在 Consumer 的 `application.properties`，实例名必须是 `getUser`（见下一节逐项对照）。注解要生效还需 `resilience4j-spring-boot3` + `spring-boot-starter-aop`

`GET /user/2/{id}` **没有**加熔断，而且指向不存在的 provider2，不要用它做本课实验。

### 4. 熔断的运作过程（对照配置）

配置都在 `spring-cloud-consumer-14` 的 `application.properties`，前缀是 `resilience4j.circuitbreaker.instances.getUser.*`。`getUser` 必须和 `@CircuitBreaker(name = "getUser")` 一致，否则注解走默认阈值，你改的数字不生效。

**三种状态**（家里电闸的三种姿势）

```text
闭合 CLOSED  ──失败率≥50% 或 慢调用率≥80%──►  打开 OPEN
     ▲                                              │
     │                         等满 10s（automatic-transition=true）
     │                                              ▼
     └──────── 3 次探测成功 ──────── 半开 HALF_OPEN
                3 次探测失败 ──────────────► 再打开
```

| 状态 | 这次请求会不会打 Provider | 失败后调用方看到什么 |
|------|---------------------------|----------------------|
| 闭合 | 会，真的发 HTTP | 远程异常 → `getFallback` → `"自定义信息"` |
| 打开 | **不会**，立刻拒绝 | `CallNotPermittedException` → 同样走 `getFallback` |
| 半开 | 只放行 **3** 个探测，多出来的仍拒绝 | 探测失败或超额拒绝 → 还是 `getFallback` |

调用方永远看到 `"自定义信息"`，所以**不能只看响应判断状态**。要看 Consumer 日志：闭合/半开时会先打到 Provider（连接拒绝、超时等），打开后远程调用根本不会发生，只有 `调用远程接口异常，返回自定义信息`。

**配置怎么驱动这三态**

| 配置项 | 本课取值 | 在过程里干什么 |
|--------|----------|----------------|
| `sliding-window-type` | `COUNT_BASED` | 按**次数**滑动，不是按时间。最近 N 次调用组成窗口 |
| `sliding-window-size` | `10` | 窗口最多记住最近 10 次（成功 / 失败 / 慢） |
| `minimum-number-of-calls` | `5` | **至少 5 次**才开始算失败率、慢调用率。避免刚启动 1 次失败就跳闸 |
| `failure-rate-threshold` | `50` | 窗口内失败率 **≥ 50%** → 闭合变打开 |
| `slow-call-duration-threshold` | `2s` | 单次调用超过 2 秒，记一笔「慢」（成功但慢也算） |
| `slow-call-rate-threshold` | `80` | 窗口内慢调用占比 **≥ 80%** → 同样跳闸。和失败率是**两条独立保险丝** |
| `wait-duration-in-open-state` | `10s` | 打开后先冷静 10 秒，这期间一律不打 Provider |
| `automatic-transition-from-open-to-half-open-enabled` | `true` | 满 10 秒**自动**进入半开。若为 `false`，要等下一次请求来了才切半开 |
| `permitted-number-of-calls-in-half-open-state` | `3` | 半开时最多放行 3 个探测。3 个都回来再裁决：达标回闭合，不达标再打开 |

**用本课数字走一遍（停掉 Provider 后连续 `curl /user/1`）**

1. **第 1～4 次（仍闭合）**  
   窗口里还不满 5 次，`minimum-number-of-calls` 拦着不算比率。每次都会真的访问 `http://spring-cloud-provider/...`，失败后再进 `getFallback`。

2. **第 5 次（跳闸）**  
   5 次全失败，失败率 100% ≥ `failure-rate-threshold=50`，状态切到**打开**。第 5 次本身已经打过 Provider，返回的仍是 `"自定义信息"`。

3. **随后 10 秒（打开）**  
   `wait-duration-in-open-state=10s`。再 curl **不会**发 HTTP，熔断器直接拒绝，fallback 立刻返回。这就是保险丝的意义：给下游恢复时间，也给自己留线程。

4. **满 10 秒 → 半开**  
   `automatic-transition-from-open-to-half-open-enabled=true`，到点自动半开。接下来最多 3 个请求被放去「探路」：
   - Provider **还停着**：3 次探测都失败 → 再打开，再等 10 秒。
   - Provider **已起来**：探测成功、失败率掉到阈值以下 → 回到闭合，后面又是正常 JSON。

**两个容易误会的点**

- **慢调用 ≠ 超时掐断**。`slow-call-duration-threshold=2s` 只是统计口径：调完了发现超过 2 秒，记一笔慢。本课没有配 TimeLimiter，熔断器**不会**在 2 秒处把线程砍掉。Provider 完全挂掉时，你看到的是连接失败，走的是「失败率」那条线，不是「慢调用」那条。
- **fallback 不是熔断本身**。第 1～4 次还没跳闸，也会进 `getFallback`——那是「这次调用失败了，给个替代品」。打开之后的 fallback，才是「保险丝已经跳了，连试都不试」。两个入口同一个方法，状态不同。

### 5. 本课不保护 Feign

`/feign/user/{id}` 还是光秃秃的远程调用。停 Provider 后：

| 入口 | 期望 |
|------|------|
| `GET /user/1` | `"自定义信息"` |
| `GET /feign/user/1` | 报错（无 fallback） |

第 17 课才给 Feign 配 `RcFeignFallback`。先只在一条链路上把「保险丝」看明白。

---

## 模块结构

五模块 `*-14`，端口仍是 8761 / 7778 / 8888。Consumer POM 增加 `spring-cloud-starter-circuitbreaker-resilience4j`。

## 建议启动与验证

1. 全套启动后：`curl http://localhost:8888/user/1` 应是 User JSON
2. **停掉 Provider**，连续 curl 同一地址：前几次仍会打到已挂的下游再降级；大约第 5 次后进入打开，10 秒内再 curl 不再打 Provider，响应一直是 `自定义信息`
3. 打开期间把 Provider 拉起来，**立刻** curl 仍是兜底（还在等 10 秒）；等半开探测通过后，再 curl 应恢复 JSON

## 与后续课程

- **第 16 课**：熔断保留，再强调负载规则（组合练习，新东西不多）
- **第 17 课**：Feign 也加上 fallback；Provider 改随机端口

## Docker 一键启动

```bash
cd spring-cloud-14
docker compose up --build -d
```

- 日志：`docker compose logs -f`
- 停止单个 Provider 容器后再 `curl http://localhost:8888/user/1`，应看到兜底文案
- 全部停止：`docker compose down -v`
- Eureka：[http://localhost:8761](http://localhost:8761)，`roncoo` / `123456`
