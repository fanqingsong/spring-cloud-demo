# 第 05 课 · Eureka 安全与集群

## 一句话先懂

第 02 / 04 课的注册中心是「谁都能打开的单本通讯录」。生产上要解决两件事：**不能谁都能改花名册（认证）**，以及**这本通讯录本身不能只有一份（集群）**。

## 学习目标

- 理解为什么 Eureka 控制台和注册接口需要 **HTTP Basic 认证**
- 会读客户端 `defaultZone` 里 **`http://用户名:密码@主机:端口/eureka/`** 这种写法
- 理解三个 Eureka 节点**互相登记对方地址**后，注册表如何同步
- 知道本地集群必须先做 **hosts 映射**（`roncoo1` / `roncoo2` / `roncoo3`）

## 本课在整条链路里的位置

| 课 | 焦点 |
|----|------|
| 02 / 04 | 单节点、无（或未讲清）认证 |
| **本课** | **锁上门 + 准备三本互相同步的通讯录** |
| 06 | 在「能安全注册」的前提下开始认真做 REST 调用 |

本课 Provider / Consumer **仍然没有业务 Controller**，不要用 8888 去调用户接口。验证只看控制台。

---

## 知识点讲解

### 1. HTTP Basic 认证：给注册中心加一把锁

**是什么**

浏览器或程序访问时，在 HTTP 头里带上 `Authorization: Basic ...`（用户名密码的 Base64）。Spring Security 的 `httpBasic()` 就是这种最简单的「弹出登录框」认证。

**有什么用**

Eureka 的控制台和 `/eureka/**` 注册接口默认是敞开的。内网里被扫到，别人可以：

- 偷看你有哪些服务
- 注册一个假 Provider，把流量骗走

教学项目用固定账号 `roncoo` / `123456` 演示「先锁上门」。生产上应换成密钥管理，并限制网段。

**本课怎么配**

```properties
spring.security.user.name=roncoo
spring.security.user.password=123456
```

`EurekaSecurityConfiguration`：所有路径都要登录，并**关闭 CSRF**。Eureka 客户端用的是非浏览器的心跳 POST，CSRF 开着会把合法注册挡掉，这是 Eureka + Security 的常见坑。

### 2. defaultZone 里嵌入用户名密码

**是什么**

客户端不能只写 `http://localhost:8761/eureka/` 了，必须带上和 Server 一样的账号：

```properties
eureka.client.serviceUrl.defaultZone=http://roncoo:123456@roncoo1:8761/eureka/
```

**有什么用**

Eureka Client 发注册 / 心跳时，会用 URL 里的账号做 Basic 认证。账号错了，日志里会出现 401，控制台永远看不到这个实例。

可以记成：**锁换了，钥匙要塞进报到地址里。**

### 3. Eureka 集群：多本通讯录互抄

**是什么**

单节点 Eureka 挂了，所有服务还在跑，但**新启动的实例无法注册、已有客户端迟早拉不到更新**。集群的做法是：起 2～3 个 Server 进程，**每个节点的 `defaultZone` 填写其他节点的地址**，它们会把各自收到的注册信息复制给同伴。

**有什么用**

- 挂掉一台，另外两台仍能提供查询
- 客户端 `defaultZone` 可以写多个地址，连不上第一个就试下一个

**不是**「三个节点组成一个虚拟 IP」那种负载均衡器。每个节点都是完整的 Eureka，靠**复制**保持接近一致（最终一致，允许短暂不一致）。

**本课怎么配（service-01 示例）**

```properties
eureka.instance.hostname=roncoo1
eureka.client.serviceUrl.defaultZone=http://roncoo:123456@roncoo2:8762/eureka/,http://roncoo:123456@roncoo3:8763/eureka/
```

注意：这里列的是**其他节点**，一般不写自己。三台互相指向，形成一个复制环。

```text
roncoo1:8761  ←→  roncoo2:8762  ←→  roncoo3:8763
     ↑________________复制注册表________________↑
```

打开任意一个控制台，应能在 **DS Replicas**（副本）里看到另外两台，服务列表内容应大致相同。

### 4. hostname 与 hosts：名字必须能解析

**是什么**

集群配置里写的是 `roncoo1` 这种主机名，不是 `localhost`。Eureka 用这个名字生成自己的对外身份，同伴也用这个名字来连它。

**有什么用 / 为什么本地要改 hosts**

你的电脑默认不认识 `roncoo1`。不改 hosts，节点之间复制失败，看起来像「三个独立的空注册中心」。

在 `/etc/hosts`（Windows 是 `C:\Windows\System32\drivers\etc\hosts`）增加：

```text
127.0.0.1 roncoo1 roncoo2 roncoo3
```

**Docker Compose 不需要改你电脑的 hosts**：Compose 自带 DNS，容器名就能互解析。这是一键启动更省事的原因。

### 5. 单节点模块还留着做什么

`spring-cloud-05-service`（8761）是带 Security 的**单节点对照**，方便和 01/02/03 三个集群模块对比。Docker Compose **只用三节点**，不用这个单节点模块。

---

## 模块结构

| 模块 | 端口 | 应用名 | 说明 |
|------|------|--------|------|
| `spring-cloud-05-service` | 8761 | `spring-cloud-server` | 单节点对照（Compose 不用） |
| `spring-cloud-05-service-01` | 8761 | `spring-cloud-server-01` | 集群，hostname=`roncoo1` |
| `spring-cloud-05-service-02` | 8762 | `spring-cloud-server-02` | `roncoo2` |
| `spring-cloud-05-service-03` | 8763 | `spring-cloud-server-03` | `roncoo3` |
| `spring-cloud-05-provider` | 7777 | `spring-cloud-provider` | 只注册，无业务接口 |
| `spring-cloud-05-consumer` | 8888 | `spring-cloud-consumer` | 只注册，无业务接口 |

本地 properties 里 Provider 可能只写了 `roncoo1:8761`，Consumer 甚至写 `localhost:8761`。**以你实际运行方式为准**：Compose 会用环境变量改成三节点完整列表。

## 建议启动与验证

**本地 IDE**

1. 先配 hosts，再按 01 → 02 → 03 启动三个 Server
2. 启动 Provider、Consumer
3. 分别打开 [http://localhost:8761](http://localhost:8761)、8762、8763，账号 `roncoo` / `123456`
4. 每个控制台都应看到另外两个副本，以及 provider / consumer

**不配 hosts 时的典型现象**：节点起得来，但副本列表为空，或客户端 401 / 连不上。

## 与后续课程

- **第 06 课**：通讯录已经能锁、能备份，开始用 RestTemplate 按服务名调 User 接口，并起多个同名 Provider

## Docker 一键启动

```bash
cd spring-cloud-05
docker compose up --build -d
```

- 日志：`docker compose logs -f`
- 停止：`docker compose down -v`
- 验证：[http://localhost:8761](http://localhost:8761)（也可试 8762 / 8763），账号 `roncoo` / `123456`

> 容器网络里用集群 hostname 互指，并开启 `prefer-ip-address`。
