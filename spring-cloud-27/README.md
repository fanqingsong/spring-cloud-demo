# 第 27 课 · Nacos 双 Provider 与权重负载

## 一句话先懂

第 06 课用「无境1 / 无境2」让你看见请求会换机器。本课更进一步：**两台机器能力不一样时，让强的多接、弱的少接**。在 Nacos 里这叫实例 **weight（权重）**；Spring Cloud Alibaba 的 LoadBalancer 会按权重抽签。

## 学习目标

- 理解「同名多实例」和「权重」是两层概念：先有多台，再谈分多少
- 会读 `spring.cloud.nacos.discovery.weight` 和 Compose 环境变量
- 会用 Consumer 的统计接口看命中次数，而不是凭感觉
- 能在控制台改权重、不重启，再跑一轮统计

## 前置课

- [第 25 课](../spring-cloud-25/README.md)：Nacos 发现
- [第 06 课](../spring-cloud-06/README.md)：多实例（Eureka、无权重）

---

## 知识点讲解

### 1. 权重：抽签时票数不同

**是什么**

两台 Provider 都叫 `spring-cloud-27-provider`，用**同一份 jar**。Compose 用环境变量区分：

| 容器 | 端口 | 权重 | 标签 |
|------|------|------|------|
| provider-high | 7777 | **100** | `weight-high` |
| provider-low | 7778 | **1** | `weight-low` |

对应配置：

```properties
spring.cloud.nacos.discovery.weight=${NACOS_DISCOVERY_WEIGHT:1}
provider.instance-label=${PROVIDER_INSTANCE_LABEL:provider-default}
```

Consumer 循环请求 `http://spring-cloud-27-provider/api/instance-label`，数每个标签出现几次。

**有什么用**

新机器 8 核、旧机器 2 核时，平均轮询会把旧机器打满。权重让你按容量摊流量。灰度发布也可以：新版本先给权重 1，观察后再加大。

**生活类比**

两名收银员，熟练工有 100 张号票、新人 1 张。顾客抽号，绝大多数排到熟练工。不是「永远不让新人干活」，而是概率不同。所以 100 次调用里 **high 远多于 low**，但 low 仍可能偶尔命中；不要要求严格 100:1。

### 2. 谁在根据权重做选择

规则发生在 **Consumer 的 LoadBalancer**（Alibaba 提供的 `NacosLoadBalancer`），不是 Nacos 服务器替你转发 HTTP。Nacos 只保存「这台机器 weight=100」。和 Eureka 课一样：客户端拿列表、客户端做决定。

因此：

- 改权重：控制台改完，客户端刷新实例信息后，下一轮统计就会变，**不必重启 Provider**
- 统计接口在 Consumer：`GET /demo/weight?times=100`（`times` 允许 1～500）

直连单机（绕过负载）：

```text
GET :7777/api/instance-label  →  weight-high
GET :7778/api/instance-label  →  weight-low
GET :7777/api/user/1          →  JSON 里带 nacosWeight: 100
```

### 3. 本课没有的东西

没有 Gateway、没有 Feign、没有 Nacos 配置导入、Compose **没有** `nacos-init`。只为把「权重」看清楚。Nacos 控制台同样关鉴权。

---

## 模块结构

见上表。Consumer 端口 8888。

## 建议启动与验证

1. 启动 Nacos 与两个 Provider、Consumer
2. `curl 'http://localhost:8888/demo/weight?times=100'`
3. 看 `hitsByInstanceLabel`：`weight-high` 应远大于 `weight-low`
4. 控制台 **服务详情 → 实例列表** 把两台都改成 50，再统计，应接近 1:1
5. 停掉 `provider-low`，统计应全部落到 `weight-high`

## 扩展实验

- 权重改成 0 或下线实例，观察是否还被选中（以 Nacos / LoadBalancer 当前行为为准）
- 对照 09 课自定义 Rule：那是写死端口；本课是用注册中心元数据（权重）影响官方选择器

## Docker 一键启动

```bash
cd spring-cloud-27
docker compose up --build -d
```

- 日志：`docker compose logs -f`
- 停止：`docker compose down -v`
- 验证：`curl 'http://localhost:8888/demo/weight?times=200'`

> 应用通过 `NACOS_SERVER_ADDR=nacos:8848` 注册；权重由 Compose 环境变量注入。
