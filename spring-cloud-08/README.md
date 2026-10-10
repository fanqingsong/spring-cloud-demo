# 第 08 课 · 多服务与负载均衡策略

## 一句话先懂

第 06 课只有**一个**逻辑服务、三台机器。本课变成**两套**服务（两个部门），并且第一次回答：「挑机器时，能不能指定规则，比如改成随机？」

## 学习目标

- 区分「逻辑服务名」和「实例」：两套 Provider 是两个名字，不是六台随便混在一起
- 理解**负载均衡规则**是「从列表里怎么选一台」的策略
- 知道本仓库用配置键 `应用名.ribbon.NFLoadBalancerRuleClassName` 来点名规则类（对照旧视频的 Ribbon）
- 了解 `@RibbonClient` 的 Java 配法在本课是**整段注释**，真正生效的是 properties

## 本课在整条链路里的位置

| 课 | 新增 |
|----|------|
| 06 | 一个服务名 + 默认怎么挑实例 |
| **本课** | **两个服务名 + 用配置指定 RandomRule** |
| 09 | 自己写一个 Rule，固定打到某端口 |

---

## 知识点讲解

### 1. 两个逻辑服务：通讯录上的两个部门

**是什么**

| 服务名 | 模块 | 端口 | 返回名 |
|--------|------|------|--------|
| `spring-cloud-provider` | provider-01 / 02 | 7778 / 7779 | 无境1 / 无境2 |
| `spring-cloud-provider2` | provider2-01 / 02 | 7780 / 7781 | 无境3 / 无境4 |

它们在 Eureka 里是**两行应用**，互不顶替。Consumer 要调哪一套，就在 URL 里写哪一个名字。

**有什么用**

真实系统很少只有一个后端。订单服务、用户服务必须是不同的 `spring.application.name`，否则负载均衡会把「查用户」的请求打到「下订单」的机器上。

**本课对外入口**

- `GET http://localhost:8888/user/{id}` → `http://spring-cloud-provider/api/user/{id}`
- `GET http://localhost:8888/user/2/{id}` → `http://spring-cloud-provider2/api/user/{id}`

`/user/2/` 只是 Consumer 自己起的路径前缀，用来区分「调第二套服务」，不是 Provider 的路径。

### 2. 负载均衡规则（IRule / RandomRule）

**是什么**

拿到「这个服务名下有哪些实例」之后，还要决定**这一次用哪一台**。常见策略：

| 规则直觉 | 含义 |
|----------|------|
| 轮询（RoundRobin） | 1、2、3、1、2、3… 轮着来 |
| 随机（Random） | 每次掷骰子 |
| 自定义 | 第 09 课：比如「必须选 7779」 |

**有什么用**

默认轮询最公平；随机能避免「刚好每次都打到正在重启的那台」这种同步踩坑；后面还可以按机房、权重来选。

**生活类比**

公司有两部客服电话。轮询是前台按桌签依次分配；随机是闭眼戳一份工号。规则改的是前台怎么分，不是电话号码本身。

### 3. 为什么配置键还叫 `*.ribbon.*`

原课程使用 Netflix Ribbon。Spring Cloud 2020 之后 Ribbon 被移除，本仓库运行时是 **Spring Cloud LoadBalancer**。为了对照视频，properties 仍使用：

```properties
# 格式：应用名.ribbon.NFLoadBalancerRuleClassName=规则全类名
spring-cloud-provider.ribbon.NFLoadBalancerRuleClassName=com.netflix.loadbalancer.RandomRule
spring-cloud-provider2.ribbon.NFLoadBalancerRuleClassName=com.netflix.loadbalancer.RandomRule
```

**键的前半段必须等于服务名**，这样「部门 A 随机、部门 B 轮询」才能分开配。本课两套都配成随机，方便你观察「不是严格 1-2-1-2」。

Java 里的 `@RibbonClient`、`RandomRuleConfig` 在本课是**整文件注释**，防止和 properties 打架。想对照旧视频，打开那些文件看注释即可，不要以为改 Java 就会生效。

---

## 模块结构

- `spring-cloud-08-service`（8761）
- `spring-cloud-08-provider-01/02` → `spring-cloud-provider`
- `spring-cloud-08-provider2-01/02` → `spring-cloud-provider2`
- `spring-cloud-08-consumer`（8888）

## 建议启动与验证

1. 启动 Eureka、两套 Provider（各至少一台）、Consumer
2. `curl http://localhost:8888/user/1` 多次，name 应在无境1 / 无境2 间变化
3. `curl http://localhost:8888/user/2/1` 多次，应在无境3 / 无境4 间变化
4. Eureka 控制台应能看到**两个**应用名

后续 09、10 课的 Compose **往往不再起 provider2**。那些课里若再访问 `/user/2/{id}`，会失败，这是环境差异，不是接口写错。

## 与后续课程

- **第 09 课**：`RoncooCustomRule`，用代码决定「选谁」

## Docker 一键启动

```bash
cd spring-cloud-08
docker compose up --build -d
```

- 日志：`docker compose logs -f`
- 停止：`docker compose down -v`
- 验证：`curl http://localhost:8888/user/1` 与 `curl http://localhost:8888/user/2/1`
- Eureka：[http://localhost:8761](http://localhost:8761)，`roncoo` / `123456`
