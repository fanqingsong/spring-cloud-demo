# 第 14 课 · 服务熔断（Resilience4j）

## 一句话先懂

前面调用都假设 Provider「一定在」。现实里下游会超时、会挂。如果不加保护，Consumer 的线程会全部堵在等待上，再把更上游拖死——这叫**雪崩**。熔断就是给这次调用加一把**保险丝**：连续失败就断开，立刻走兜底逻辑（降级）。

## 学习目标

- 能用自己的话区分：**超时、重试、熔断、降级**各管什么
- 会在 RestTemplate 方法上使用 `@CircuitBreaker` + `fallbackMethod`
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

- `name` 只是这把保险丝的名字，方便日志和监控区分多条调用
- fallback 方法必须和原方法在**同一个类**，参数列表兼容（通常多一个 `Throwable` 也可以，以你代码为准）
- 本课没在 properties 里细调失败次数、打开时长，用的是 Resilience4j **默认阈值**。教学验证用「直接停进程」足够触发

`GET /user/2/{id}` **没有**加熔断，而且指向不存在的 provider2，不要用它做本课实验。

### 4. 本课不保护 Feign

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
2. **停掉 Provider**，再 curl 同一地址，应变成 `自定义信息`
3. 重新启动 Provider，等重新注册后，再 curl 应恢复 JSON

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
