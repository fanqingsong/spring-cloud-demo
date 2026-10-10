# 第 27 课 · Nacos 双 Provider 与权重负载

## 学习目标

- 同一 `spring.application.name` 注册 **两个 Provider 实例**（不同端口、不同标识）
- 理解 Nacos **实例权重（weight）** 如何影响 Spring Cloud **LoadBalancer** 选实例
- 用 Consumer 批量调用统计 **命中分布**

## 前置课

- [第 25 课](../spring-cloud-25/README.md)：Nacos 注册发现  
- [第 06 课](../spring-cloud-06/README.md)：多实例概念（Eureka 版）

## 模块结构

| 模块 / 容器 | 端口 | 权重（默认 Compose） | 实例标识 |
|-------------|------|----------------------|----------|
| `provider-high` | 7777 | **100** | `weight-high` |
| `provider-low` | 7778 | **1** | `weight-low` |
| `spring-cloud-27-consumer` | 8888 | — | 发起统计调用 |

两个 Provider 使用**同一 JAR**、同一服务名 **`spring-cloud-27-provider`**，通过环境变量区分权重与标签。

## 核心实现

- Provider：`spring.cloud.nacos.discovery.weight` + `provider.instance-label`  
- Consumer：`@LoadBalanced RestTemplate` 循环调用  
  `http://spring-cloud-27-provider/api/instance-label`  
- 依赖：`nacos-discovery` + `loadbalancer`（由 Alibaba 提供 **基于权重的 NacosLoadBalancer**）

## 建议启动与验证

1. 启动 Nacos → 两个 Provider → Consumer  
2. 单次调用：`GET http://localhost:8888/demo/weight?times=100`  
3. 查看 JSON 中 `hitsByInstanceLabel`：`weight-high` 次数应**远大于** `weight-low`（约 100:1，存在随机波动）  
4. 在 Nacos 控制台 **服务详情 → 实例列表** 修改权重，不重启应用，再次统计观察变化  

## 扩展实验

- 将两实例权重都设为 `50`，分布应接近 1:1  
- 下线 `provider-low` 容器，统计应全部落在 `weight-high`

## Docker 一键启动

本课已提供 **Docker Compose**（含 Nacos、初始化配置脚本、Provider、Consumer），无需本地安装 JDK/Maven 即可启动演示（首次会镜像内 Maven 编译，耗时较长）。

```bash
cd spring-cloud-27
docker compose up --build -d
```

- 查看日志：`docker compose logs -f`
- 停止：`docker compose down -v`
- 验证：http://localhost:8888/demo/weight?times=200（weight-high 命中应远多于 weight-low）

> Compose 会通过 `nacos-init` 自动写入演示配置；应用通过环境变量 `NACOS_SERVER_ADDR=nacos:8848` 连接注册/配置中心。
