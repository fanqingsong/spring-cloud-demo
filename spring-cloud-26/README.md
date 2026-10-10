# 第 26 课 · Nacos + Gateway + OpenFeign

## 一句话先懂

把第 23 课那套「大门 + 声明式调用 + 熔断降级」原样搬过来，**唯一换掉的是通讯录：Eureka → Nacos**。若你已理解 `lb://服务名`，本课没有新的网络模型，只是证明这套写法与注册中心品牌无关。

## 学习目标

- 在 Nacos 控制台看到 gateway / provider / consumer 三个服务
- 会走两条链路：网关直转 Provider；网关转 Consumer，再 Feign 打 Provider
- 停 Provider 后，从 Feign 入口看到 **fallback JSON**，而不是一堆异常

## 前置课

- [第 25 课](../spring-cloud-25/README.md)：Nacos 注册（本课**不再演示配置中心**）
- [第 23 课](../spring-cloud-23/README.md)：同一路由思想的 Eureka 版

---

## 知识点讲解

### 1. `lb://` 在 Nacos 下仍然成立

**是什么**

```properties
# /api/**  →  spring-cloud-26-provider
# /feign/** → spring-cloud-26-consumer
```

Gateway 依赖 `nacos-discovery` + `loadbalancer`。`lb://` 的含义没变：按**服务名**查实例，再转发。变的只是「去哪本通讯录查」。

**有什么用**

换注册中心时，业务 URL 和路牌不用重写，只要服务名对齐。这是「面向服务名编程」的回报。

本课 **没有** Nacos Config，也 **没有** `nacos-init`。Compose 只起 Nacos + 三个 Java 应用。不要到控制台找 25 课那三份 Data ID。

### 2. 两条链路（和 23 课一一对应）

```text
GET :9876/api/user/1
  → Provider /api/user/1
  → {"id":1,"name":"无境","via":"spring-cloud-26-provider"}

GET :9876/feign/user/1
  → Consumer /feign/user/1
  → Feign IUserBiz（服务名 spring-cloud-26-provider）
  → 同一个 Provider 接口
```

直连也可以：`7777/api/user/1`、`8888/feign/user/1`。

### 3. Feign fallback：这次返回的是 JSON

**是什么**

```java
@FeignClient(value = "spring-cloud-26-provider", fallback = UserFeignFallback.class)
```

并打开 `spring.cloud.openfeign.circuitbreaker.enabled=true`。降级体类似：

```json
{"id":1,"fallback":true,"message":"Provider 不可用，走 Feign 降级"}
```

**有什么用**

23 课 Feign 降级是一句 `"system error"`。本课做成结构化 JSON，调用方更容易判断「这是兜底，不是真用户」。停掉 Provider 容器后再打 `/feign/user/1`（经网关或直连 Consumer 均可）。

`/api/user/1` 经网关直打 Provider，网关本课没有 fallback，停 Provider 后这条会失败——用来对比「降级写在哪一层，哪一层才能兜住」。

---

## 模块结构

| 模块 | 端口 | 应用名 |
|------|------|--------|
| Nacos | 8848 | — |
| provider | 7777 | `spring-cloud-26-provider` |
| consumer | 8888 | `spring-cloud-26-consumer` |
| gateway | 9876 | `spring-cloud-26-gateway` |
| api | — | `IUserBiz` + `UserFeignFallback` |
| bean | — | 占位模块 |

鉴权：Compose 关闭 Nacos 登录，控制台直接进。

## 建议启动与验证

1. Nacos → Provider → Consumer → Gateway（或 Compose 一键）
2. `curl http://localhost:9876/api/user/1`
3. `curl http://localhost:9876/feign/user/1`
4. `docker compose stop` 掉 provider 后再打第 3 步，应见 fallback JSON
5. 控制台服务列表应有三个名字

## 与第 27 课

本课侧重入口和声明式调用；[第 27 课](../spring-cloud-27/README.md) 侧重「同一服务两台机器、权重不一样」。

## Docker 一键启动

```bash
cd spring-cloud-26
docker compose up --build -d
```

- 日志：`docker compose logs -f`
- 停止：`docker compose down -v`
- 验证：9876 的 `/api/user/1` 与 `/feign/user/1`；Nacos http://localhost:8848/nacos

> 应用通过 `NACOS_SERVER_ADDR=nacos:8848` 做发现。本课不写入 Nacos 配置。
