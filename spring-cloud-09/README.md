# 第 09 课 · 自定义负载均衡规则

## 一句话先懂

第 08 课用的是框架自带的「随机」。本课自己写一个选择器：**列表里谁的端口是 7779，就一直挑谁**。用来证明「挑哪一台」是可以按业务改的，不是框架写死的。

## 学习目标

- 理解负载均衡规则的本质：输入是「可用实例列表」，输出是「其中一个」
- 能读懂 `RoncooCustomRule.choose()` 在干什么
- 会用 `@LoadBalancerClient` 把自定义规则挂到指定服务名（旧视频里的 `NFLoadBalancerRuleClassName` 仅作对照）
- 知道规则写在 **Consumer 端**（谁发起调用，谁做选择）

## 本课在整条链路里的位置

内置规则用腻了就自己写。第 10 课不再扩展规则，而是换一种调用写法（Feign）。

---

## 知识点讲解

### 1. 自定义 Rule：把「选实例」变成一段 if

**是什么**

`RoncooCustomRule` 实现 `ReactorServiceInstanceLoadBalancer`（原课程是 Ribbon 的 `AbstractLoadBalancerRule`），核心仍是 `choose()`：

1. 向 `ServiceInstanceListSupplier` 要「当前能连的实例列表」
2. 遍历，找到 `port == 7779` 的那一台
3. 找不到则返回空响应（调用失败），不要假设一定有匹配实例

**有什么用**

教学上：让你看见请求**稳定打到「无境2」**（provider-02，端口 7779），证明配置真的换了规则。

企业里更常见的自定义条件是：同机房优先、灰度标签、权重、把预发布实例排除。端口写死只是最小例子。

**生活类比**

08 课的随机是「闭眼抓阄」；本课是「点名：只要 7779 号工位」。点名规则贴在**打电话的人（Consumer）**桌上，被叫的人（Provider）不用改代码。

### 2. 规则为什么必须配在 Consumer

负载均衡发生在**发请求之前**。Provider 只负责提供 `/api/user/{id}`，它不知道也不应该知道调用方怎么挑自己的兄弟节点。所以在 Consumer 里用：

```java
@LoadBalancerClient(name = "spring-cloud-provider", configuration = RoncooCustomRuleConfig.class)
```

类也放在 Consumer 模块。`application.properties` 里的 `*.ribbon.NFLoadBalancerRuleClassName` 是旧视频对照，**不会**驱动 Spring Cloud LoadBalancer。

本课没有部署 provider2。`UserController` 里的 `/user/2/{id}` 本课默认调不通。

### 3. 只起一台 7778 时会发生什么

规则写死要 7779。若只启动 provider-01（7778）：

- `choose()` 找不到目标，返回空响应
- 调用方会看到负载均衡选实例失败

这不是 Eureka 坏了，是规则与实际实例集合不匹配。自定义规则一定要考虑「条件一个都不满足」时的退路。

---

## 模块结构

| 模块 | 端口 | 说明 |
|------|------|------|
| `spring-cloud-09-service` | 8761 | Eureka |
| `spring-cloud-09-provider-01` | 7778 | 无境1（按规则应很少被选中） |
| `spring-cloud-09-provider-02` | 7779 | 无境2（规则指定） |
| `spring-cloud-09-consumer` | 8888 | 使用 `RoncooCustomRule` |

## 建议启动与验证

1. **两台 Provider 都要启动**，否则规则可能空转
2. 多次 `curl http://localhost:8888/user/1`
3. 返回的 name 应**稳定为无境2**
4. 对照：直连 `curl http://localhost:7778/api/user/1` 仍是无境1，说明 Provider 都活着，只是 Consumer 不选它

## 与后续课程

- **第 10 课**：引入 OpenFeign，少写 RestTemplate URL；负载均衡仍然在客户端发生

## Docker 一键启动

```bash
cd spring-cloud-09
docker compose up --build -d
```

- 日志：`docker compose logs -f`
- 停止：`docker compose down -v`
- 验证：多次 `curl http://localhost:8888/user/1`，应一直是无境2
- Eureka：[http://localhost:8761](http://localhost:8761)，`roncoo` / `123456`
