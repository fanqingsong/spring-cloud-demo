#!/usr/bin/env python3
"""为各 spring-cloud-XX 课生成 docker-compose.yml 并更新 README Docker 小节。"""
from __future__ import annotations

import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

HEADER = textwrap.dedent("""\
    # Docker Compose 演示（本课）
    # 在仓库根目录或本课目录执行：
    #   docker compose up --build -d
    # 停止并清理：
    #   docker compose down -v
""")

README_DOCKER_MARKER = "## Docker 一键启动"


def yaml_quote(s: str) -> str:
    if any(c in s for c in ":{}[],&*#?|-<>=!%@`"):
        return f'"{s}"'
    return s


def build_block(lesson: str, module: str) -> str:
    return f"""    build:
      context: ..
      dockerfile: docker/Dockerfile
      args:
        LESSON: {lesson}
        MODULE: {module}"""


def eureka_server_env(lesson: str, *, secured: bool) -> dict[str, str]:
    if lesson == "spring-cloud-05":
        return {}  # 集群节点单独配置
    if secured:
        return {
            "EUREKA_CLIENT_SERVICEURL_DEFAULTZONE": "http://roncoo:123456@eureka:8761/eureka/",
            "EUREKA_CLIENT_SERVICEURL_RONCOOZONE": "http://roncoo:123456@eureka:8761/eureka/",
            "SPRING_SECURITY_USER_NAME": "roncoo",
            "SPRING_SECURITY_USER_PASSWORD": "123456",
        }
    return {"EUREKA_CLIENT_SERVICEURL_DEFAULTZONE": "http://eureka:8761/eureka/"}


def eureka_client_env(*, secured: bool, zones: bool) -> dict[str, str]:
    env = {"EUREKA_INSTANCE_PREFERIPADDRESS": "true"}
    if secured:
        url = "http://roncoo:123456@eureka:8761/eureka/"
        env["EUREKA_CLIENT_SERVICEURL_DEFAULTZONE"] = url
        if zones:
            env["EUREKA_CLIENT_SERVICEURL_RONCOOZONE"] = url
    else:
        env["EUREKA_CLIENT_SERVICEURL_DEFAULTZONE"] = "http://eureka:8761/eureka/"
    return env


def render_service(
    name: str,
    lesson: str,
    module: str,
    port: int | None,
    env: dict[str, str],
    *,
    hostname: str | None = None,
    network_aliases: list[str] | None = None,
    depends: list[str] | None = None,
    publish: bool = True,
) -> str:
    lines = [f"  {name}:", build_block(lesson, module)]
    if hostname:
        lines.append(f"    hostname: {hostname}")
    if network_aliases:
        lines.append("    networks:")
        lines.append("      default:")
        lines.append("        aliases:")
        for alias in network_aliases:
            lines.append(f"          - {alias}")
    if env:
        lines.append("    environment:")
        for k, v in env.items():
            lines.append(f"      {k}: {yaml_quote(v)}")
    if depends:
        lines.append("    depends_on:")
        for d in depends:
            lines.append(f"      {d}:")
            lines.append("        condition: service_started")
    if port is not None and publish:
        lines.append("    ports:")
        lines.append(f'      - "{port}:{port}"')
    return "\n".join(lines)




class Lesson:
    def __init__(
        self,
        lesson: str,
        services: list[dict],
        *,
        secured_eureka: bool = True,
        eureka_zones: bool = False,
        verify: str | None = None,
    ):
        self.lesson = lesson
        self.services = services
        self.secured_eureka = secured_eureka
        self.eureka_zones = eureka_zones
        self.verify = verify


def lesson_05_cluster() -> Lesson:
    nodes = [
        ("eureka-1", "spring-cloud-05-service-01", 8761, "roncoo1"),
        ("eureka-2", "spring-cloud-05-service-02", 8762, "roncoo2"),
        ("eureka-3", "spring-cloud-05-service-03", 8763, "roncoo3"),
    ]
    peer = (
        "http://roncoo:123456@roncoo1:8761/eureka/,"
        "http://roncoo:123456@roncoo2:8762/eureka/,"
        "http://roncoo:123456@roncoo3:8763/eureka/"
    )
    svcs = []
    for name, mod, port, host in nodes:
        svcs.append(
            {
                "name": name,
                "module": mod,
                "port": port,
                "hostname": host,
                "network_aliases": [host],
                "role": "eureka-cluster",
                "env": {
                    "EUREKA_INSTANCE_HOSTNAME": host,
                    "EUREKA_CLIENT_SERVICEURL_DEFAULTZONE": peer,
                    "SPRING_SECURITY_USER_NAME": "roncoo",
                    "SPRING_SECURITY_USER_PASSWORD": "123456",
                },
            }
        )
    client_env = {
        "EUREKA_INSTANCE_PREFERIPADDRESS": "true",
        "EUREKA_CLIENT_SERVICEURL_DEFAULTZONE": peer,
    }
    svcs.append(
        {"name": "provider", "module": "spring-cloud-05-provider", "port": 7777, "env": client_env}
    )
    svcs.append(
        {"name": "consumer", "module": "spring-cloud-05-consumer", "port": 8888, "env": client_env}
    )
    return Lesson(
        "spring-cloud-05",
        svcs,
        secured_eureka=False,
        verify="浏览器打开 http://localhost:8761（或 8762/8763），Eureka 控制台账号 `roncoo` / `123456`",
    )


def lesson_17() -> Lesson:
    client = eureka_client_env(secured=True, zones=False)
    return Lesson(
        "spring-cloud-17",
        [
            {"name": "eureka", "module": "spring-cloud-service-17", "port": 8761, "role": "eureka"},
            {
                "name": "provider-1",
                "module": "spring-cloud-provider-17",
                "port": 7778,
                "env": {**client, "SERVER_PORT": "7778"},
            },
            {
                "name": "provider-2",
                "module": "spring-cloud-provider-17",
                "port": 7779,
                "env": {**client, "SERVER_PORT": "7779"},
            },
            {"name": "consumer", "module": "spring-cloud-consumer-17", "port": 8888, "env": client},
        ],
        verify="Eureka 控制台 http://localhost:8761 应看到两个 `spring-cloud-provider` 实例",
    )


def standard(
    lesson: str,
    eureka_module: str,
    provider_modules: list[tuple[str, int]],
    consumer_module: str,
    consumer_port: int = 8888,
    *,
    secured: bool = True,
    zones: bool = True,
    extras: list[dict] | None = None,
    verify: str | None = None,
) -> Lesson:
    svcs: list[dict] = [
        {"name": "eureka", "module": eureka_module, "port": 8761, "role": "eureka"},
    ]
    client = eureka_client_env(secured=secured, zones=zones)
    for i, (mod, port) in enumerate(provider_modules, start=1):
        name = "provider" if len(provider_modules) == 1 else f"provider-{i}"
        svcs.append({"name": name, "module": mod, "port": port, "env": dict(client)})
    svcs.append(
        {"name": "consumer", "module": consumer_module, "port": consumer_port, "env": dict(client)}
    )
    if extras:
        svcs.extend(extras)
    if verify is None:
        verify = (
            f"Eureka：http://localhost:8761"
            + ("（`roncoo` / `123456`）" if secured else "")
            + f"；Consumer：http://localhost:{consumer_port}"
        )
    return Lesson(lesson, svcs, secured_eureka=secured, eureka_zones=zones, verify=verify)


LESSONS: list[Lesson] = [
    standard(
        "spring-cloud-02",
        "spring-cloud-02-service",
        [("spring-cloud-02-provider", 7777)],
        "spring-cloud-02-consumer",
        secured=False,
        zones=False,
        verify="Eureka 控制台 http://localhost:8761 应看到 provider 与 consumer",
    ),
    standard(
        "spring-cloud-04",
        "spring-cloud-04-service",
        [("spring-cloud-04-provider", 7777)],
        "spring-cloud-04-consumer",
        secured=True,
        zones=False,
        verify="http://localhost:8761 与 Consumer http://localhost:8888",
    ),
    lesson_05_cluster(),
    standard(
        "spring-cloud-06",
        "spring-cloud-06-service",
        [
            ("spring-cloud-06-provider-01", 7778),
            ("spring-cloud-06-provider-02", 7779),
            ("spring-cloud-06-provider-03", 7780),
        ],
        "spring-cloud-06-consumer",
        verify="多次 POST/GET Consumer `/user/{id}` 观察多 Provider 负载（见课内 README）",
    ),
    standard(
        "spring-cloud-08",
        "spring-cloud-08-service",
        [
            ("spring-cloud-08-provider-01", 7778),
            ("spring-cloud-08-provider-02", 7779),
            ("spring-cloud-08-provider2-01", 7780),
            ("spring-cloud-08-provider2-02", 7781),
        ],
        "spring-cloud-08-consumer",
    ),
    standard(
        "spring-cloud-09",
        "spring-cloud-09-service",
        [("spring-cloud-09-provider-01", 7778), ("spring-cloud-09-provider-02", 7779)],
        "spring-cloud-09-consumer",
    ),
    standard(
        "spring-cloud-10",
        "spring-cloud-10-service",
        [("spring-cloud-10-provider-01", 7778), ("spring-cloud-10-provider-02", 7779)],
        "spring-cloud-10-consumer",
    ),
    standard(
        "spring-cloud-11",
        "spring-cloud-11-service",
        [("spring-cloud-11-provider-01", 7778)],
        "spring-cloud-11-consumer",
    ),
    standard(
        "spring-cloud-12",
        "spring-cloud-12-service",
        [("spring-cloud-12-provider-01", 7778)],
        "spring-cloud-12-consumer",
    ),
    standard(
        "spring-cloud-13",
        "spring-cloud-service-13",
        [("spring-cloud-provider-13", 7778)],
        "spring-cloud-consumer-13",
    ),
    standard(
        "spring-cloud-14",
        "spring-cloud-service-14",
        [("spring-cloud-provider-14", 7778)],
        "spring-cloud-consumer-14",
    ),
    standard(
        "spring-cloud-16",
        "spring-cloud-service-16",
        [("spring-cloud-provider-16", 7778)],
        "spring-cloud-consumer-16",
    ),
    lesson_17(),
    standard(
        "spring-cloud-18",
        "spring-cloud-service-18",
        [("spring-cloud-provider-18", 7778)],
        "spring-cloud-consumer-18",
    ),
    standard(
        "spring-cloud-19",
        "spring-cloud-service-19",
        [("spring-cloud-provider-19", 7778)],
        "spring-cloud-consumer-19",
        extras=[
            {
                "name": "turbine",
                "module": "spring-cloud-turbine-19",
                "port": 9999,
                "env": eureka_client_env(secured=True, zones=True),
            }
        ],
    ),
    standard(
        "spring-cloud-20",
        "spring-cloud-service-20",
        [("spring-cloud-provider-20", 7778)],
        "spring-cloud-consumer-20",
        consumer_port=8886,
        extras=[
            {
                "name": "gateway",
                "module": "spring-cloud-gateway-20",
                "port": 9876,
                "env": eureka_client_env(secured=True, zones=True),
            },
            {
                "name": "turbine",
                "module": "spring-cloud-turbine-20",
                "port": 9999,
                "env": eureka_client_env(secured=True, zones=True),
            },
        ],
        verify="Gateway http://localhost:9876；Eureka http://localhost:8761",
    ),
    standard(
        "spring-cloud-22",
        "spring-cloud-service-22",
        [("spring-cloud-provider-22", 7778)],
        "spring-cloud-consumer-22",
        extras=[
            {
                "name": "gateway",
                "module": "spring-cloud-gateway-22",
                "port": 9876,
                "env": eureka_client_env(secured=True, zones=True),
            },
            {
                "name": "turbine",
                "module": "spring-cloud-turbine-22",
                "port": 9999,
                "env": eureka_client_env(secured=True, zones=True),
            },
        ],
    ),
    standard(
        "spring-cloud-23",
        "spring-cloud-service-23",
        [("spring-cloud-provider-23", 7778)],
        "spring-cloud-consumer-23",
        extras=[
            {
                "name": "gateway",
                "module": "spring-cloud-gateway-23",
                "port": 9876,
                "env": eureka_client_env(secured=True, zones=True),
            },
            {
                "name": "turbine",
                "module": "spring-cloud-turbine-23",
                "port": 9999,
                "env": eureka_client_env(secured=True, zones=True),
            },
        ],
        verify="Gateway http://localhost:9876/api/...（见课内 README）",
    ),
]


def compose_for_lesson(lesson: Lesson) -> str:
    lines = [HEADER, f"name: {lesson.lesson}", "", "services:"]
    eureka_names = [s["name"] for s in lesson.services if s.get("role", "").startswith("eureka")]
    for svc in lesson.services:
        role = svc.get("role", "app")
        env = dict(svc.get("env") or {})
        if role == "eureka":
            env = {**eureka_server_env(lesson.lesson, secured=lesson.secured_eureka), **env}
        elif role == "eureka-cluster":
            pass  # env already complete
        elif "env" not in svc:
            env = eureka_client_env(secured=lesson.secured_eureka, zones=lesson.eureka_zones)

        depends = None
        if role not in ("eureka", "eureka-cluster"):
            depends = eureka_names if eureka_names else None
            if depends is None and role == "app":
                depends = ["eureka"]

        block = render_service(
            svc["name"],
            lesson.lesson,
            svc["module"],
            svc.get("port"),
            env,
            hostname=svc.get("hostname"),
            network_aliases=svc.get("network_aliases"),
            depends=depends,
        )
        if role not in ("eureka", "eureka-cluster", "infra"):
            block += "\n    restart: unless-stopped"
        lines.append(block)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def readme_docker_section(lesson: Lesson) -> str:
    cred = ""
    if lesson.secured_eureka and lesson.lesson != "spring-cloud-05":
        cred = "\n- Eureka 控制台默认账号：`roncoo` / `123456`"
    elif lesson.lesson == "spring-cloud-05":
        cred = "\n- Eureka 控制台默认账号：`roncoo` / `123456`（三节点见 8761/8762/8763）"
    return textwrap.dedent(
        f"""\
        {README_DOCKER_MARKER}

        本课已提供 **Docker Compose**，无需本地安装 JDK/Maven 即可启动演示（首次会镜像内 Maven 编译，耗时较长）。

        ```bash
        cd {lesson.lesson}
        docker compose up --build -d
        ```

        - 查看日志：`docker compose logs -f`
        - 停止：`docker compose down -v`
        - 验证：{lesson.verify or "见上文「建议启动与验证」"}{cred}

        > 容器内已通过环境变量将 Eureka 地址改为 `eureka`（或第 05 课集群 hostname），并开启 `prefer-ip-address` 以便服务间调用。
        """
    )


def readme_docker_section_nacos(lesson: Lesson) -> str:
    return textwrap.dedent(
        f"""\
        {README_DOCKER_MARKER}

        本课已提供 **Docker Compose**（含 Nacos、初始化配置脚本、Provider、Consumer），无需本地安装 JDK/Maven 即可启动演示（首次会镜像内 Maven 编译，耗时较长）。

        ```bash
        cd {lesson.lesson}
        docker compose up --build -d
        ```

        - 查看日志：`docker compose logs -f`
        - 停止：`docker compose down -v`
        - 验证：{lesson.verify or "见上文「建议启动与验证」"}

        > Compose 会通过 `nacos-init` 自动写入演示配置；应用通过环境变量 `NACOS_SERVER_ADDR=nacos:8848` 连接注册/配置中心。
        """
    )


def patch_readme(lesson_dir: Path, section: str) -> None:
    readme = lesson_dir / "README.md"
    if not readme.exists():
        return
    text = readme.read_text(encoding="utf-8")
    if README_DOCKER_MARKER in text:
        start = text.index(README_DOCKER_MARKER)
        rest = text[start + len(README_DOCKER_MARKER) :]
        end = len(text)
        for marker in ("\n## ", "\n---"):
            idx = rest.find(marker)
            if idx != -1:
                end = start + len(README_DOCKER_MARKER) + idx
                break
        tail = text[end:].lstrip("\n")
        text = text[:start].rstrip() + "\n\n" + section.rstrip() + "\n"
        if tail:
            text += "\n" + tail
    else:
        text = text.rstrip() + "\n\n" + section.rstrip() + "\n"
    readme.write_text(text, encoding="utf-8")


def nacos_standalone_block() -> str:
    nacos_image = "swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/nacos/nacos-server:v2.4.3"
    return f"""  nacos:
    image: {nacos_image}
    environment:
      MODE: standalone
      NACOS_AUTH_ENABLE: "false"
      JVM_XMS: 256m
      JVM_XMX: 512m
    ports:
      - "8848:8848"
      - "9848:9848"
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8848/nacos/v1/console/health/readiness || exit 1"]
      interval: 5s
      timeout: 5s
      retries: 36
      start_period: 30s"""


def _append_restart(out: str, names: tuple[str, ...]) -> str:
    for name in names:
        marker = f"  {name}:"
        idx = out.find(marker)
        if idx == -1:
            continue
        next_svc = out.find("\n  ", idx + len(marker))
        segment = out[idx:next_svc] if next_svc != -1 else out[idx:]
        if "restart:" in segment:
            continue
        insert = segment.rstrip() + "\n    restart: unless-stopped\n"
        out = out[:idx] + insert + (out[next_svc:] if next_svc != -1 else "")
    return out


def _patch_depends_nacos_healthy(out: str) -> str:
    return out.replace(
        "      nacos:\n        condition: service_started",
        "      nacos:\n        condition: service_healthy",
    )


def compose_lesson_26() -> str:
    client_env = {"NACOS_SERVER_ADDR": "nacos:8848"}
    blocks = [
        HEADER,
        "name: spring-cloud-26",
        "",
        "services:",
        nacos_standalone_block(),
        render_service(
            "provider",
            "spring-cloud-26",
            "spring-cloud-26-provider",
            7777,
            dict(client_env),
            depends=["nacos"],
        ),
        render_service(
            "consumer",
            "spring-cloud-26",
            "spring-cloud-26-consumer",
            8888,
            dict(client_env),
            depends=["nacos", "provider"],
        ),
        render_service(
            "gateway",
            "spring-cloud-26",
            "spring-cloud-26-gateway",
            9876,
            dict(client_env),
            depends=["nacos", "provider", "consumer"],
        ),
    ]
    out = _patch_depends_nacos_healthy("\n".join(blocks).rstrip() + "\n")
    return _append_restart(out, ("provider", "consumer", "gateway"))


def compose_lesson_27() -> str:
    base = {"NACOS_SERVER_ADDR": "nacos:8848"}
    high_env = {
        **base,
        "NACOS_DISCOVERY_WEIGHT": "100",
        "PROVIDER_INSTANCE_LABEL": "weight-high",
    }
    low_env = {
        **base,
        "SERVER_PORT": "7778",
        "NACOS_DISCOVERY_WEIGHT": "1",
        "PROVIDER_INSTANCE_LABEL": "weight-low",
    }
    blocks = [
        HEADER,
        "name: spring-cloud-27",
        "",
        "services:",
        nacos_standalone_block(),
        render_service(
            "provider-high",
            "spring-cloud-27",
            "spring-cloud-27-provider",
            7777,
            high_env,
            depends=["nacos"],
        ),
        render_service(
            "provider-low",
            "spring-cloud-27",
            "spring-cloud-27-provider",
            7778,
            low_env,
            depends=["nacos"],
        ),
        render_service(
            "consumer",
            "spring-cloud-27",
            "spring-cloud-27-consumer",
            8888,
            dict(base),
            depends=["nacos", "provider-high", "provider-low"],
        ),
    ]
    out = _patch_depends_nacos_healthy("\n".join(blocks).rstrip() + "\n")
    return _append_restart(out, ("provider-high", "provider-low", "consumer"))


def compose_lesson_25() -> str:
    nacos_image = "swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/nacos/nacos-server:v2.4.3"
    curl_image = "swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/curlimages/curl:8.10.1"
    client_env = {"NACOS_SERVER_ADDR": "nacos:8848"}
    blocks = [
        HEADER,
        "name: spring-cloud-25",
        "",
        "services:",
        f"""  nacos:
    image: {nacos_image}
    environment:
      MODE: standalone
      NACOS_AUTH_ENABLE: "false"
      JVM_XMS: 256m
      JVM_XMX: 512m
    ports:
      - "8848:8848"
      - "9848:9848"
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8848/nacos/v1/console/health/readiness || exit 1"]
      interval: 5s
      timeout: 5s
      retries: 36
      start_period: 30s""",
        """  nacos-init:
    image: """
        + curl_image
        + """
    volumes:
      - ./nacos/init-config.sh:/init-config.sh:ro
    environment:
      NACOS_SERVER: nacos:8848
    entrypoint: ["/bin/sh", "/init-config.sh"]
    depends_on:
      nacos:
        condition: service_healthy""",
        render_service(
            "provider",
            "spring-cloud-25",
            "spring-cloud-25-provider",
            7777,
            dict(client_env),
            depends=["nacos-init"],
        ),
        render_service(
            "consumer",
            "spring-cloud-25",
            "spring-cloud-25-consumer",
            8888,
            dict(client_env),
            depends=["nacos-init", "provider"],
        ),
    ]
    out = "\n".join(blocks).rstrip() + "\n"
    for name in ("provider", "consumer"):
        marker = f"  {name}:"
        idx = out.find(marker)
        if idx == -1:
            continue
        next_svc = out.find("\n  ", idx + len(marker))
        segment = out[idx:next_svc] if next_svc != -1 else out[idx:]
        if "restart:" in segment:
            continue
        insert = segment.rstrip() + "\n    restart: unless-stopped\n"
        out = out[:idx] + insert + (out[next_svc:] if next_svc != -1 else "")
    # nacos-init 依赖 service_completed_successfully
    out = out.replace(
        "      nacos-init:\n        condition: service_started",
        "      nacos-init:\n        condition: service_completed_successfully",
    )
    return out


def compose_lesson_24() -> str:
    client = eureka_client_env(secured=True, zones=False)
    config_import = "optional:configserver:http://config:config-secret@config-server:8888"
    oauth_issuer = "http://auth-server:9000"
    zipkin = "http://zipkin:9411/api/v2/spans"
    common = {
        **client,
        "SPRING_CONFIG_IMPORT": config_import,
        "SPRING_SECURITY_OAUTH2_RESOURCESERVER_JWT_ISSUER_URI": oauth_issuer,
        "MANAGEMENT_ZIPKIN_TRACING_ENDPOINT": zipkin,
    }
    consumer_env = {
        **common,
        "SPRING_SECURITY_OAUTH2_CLIENT_PROVIDER_SPRING_ISSUER_URI": oauth_issuer,
    }
    stream_env = {
        "SPRING_CLOUD_STREAM_KAFKA_BINDER_BROKERS": "kafka:9094",
    }
    auth_env = {"APP_OAUTH2_ISSUER": oauth_issuer}
    eureka_env = {
        "EUREKA_CLIENT_SERVICEURL_DEFAULTZONE": "http://roncoo:123456@eureka:8761/eureka/",
        "SPRING_SECURITY_USER_NAME": "roncoo",
        "SPRING_SECURITY_USER_PASSWORD": "123456",
    }

    blocks = [
        HEADER,
        "name: spring-cloud-24",
        "",
        "services:",
        """  zipkin:
    image: swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/openzipkin/zipkin:3.4
    ports:
      - "9411:9411\"""",
        """  kafka:
    image: swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/apache/kafka:3.8.0
    ports:
      - "9092:9092"
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093,PLAINTEXT_INTERNAL://0.0.0.0:9094
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092,PLAINTEXT_INTERNAL://kafka:9094
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,PLAINTEXT_INTERNAL:PLAINTEXT
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka:9093
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT_INTERNAL""",
        render_service(
            "config-server",
            "spring-cloud-24",
            "spring-cloud-config-server-24",
            8888,
            {},
        ),
        render_service("eureka", "spring-cloud-24", "spring-cloud-service-24", 8761, eureka_env),
        render_service(
            "auth-server",
            "spring-cloud-24",
            "spring-cloud-auth-server-24",
            9000,
            auth_env,
            depends=["eureka"],
        ),
        render_service(
            "provider",
            "spring-cloud-24",
            "spring-cloud-provider-24",
            7778,
            common,
            depends=["eureka", "config-server", "auth-server", "zipkin"],
        ),
        render_service(
            "consumer",
            "spring-cloud-24",
            "spring-cloud-consumer-24",
            7779,
            consumer_env,
            depends=["eureka", "config-server", "auth-server", "provider", "zipkin"],
        ),
        render_service(
            "gateway",
            "spring-cloud-24",
            "spring-cloud-gateway-24",
            9876,
            common,
            depends=["eureka", "config-server", "auth-server", "provider", "zipkin"],
        ),
        render_service(
            "stream",
            "spring-cloud-24",
            "spring-cloud-stream-24",
            7780,
            stream_env,
            depends=["kafka"],
        ),
    ]
    spring_services = (
        "config-server",
        "eureka",
        "auth-server",
        "provider",
        "consumer",
        "gateway",
        "stream",
    )
    out = "\n".join(blocks).rstrip() + "\n"
    for name in spring_services:
        marker = f"  {name}:"
        idx = out.find(marker)
        if idx == -1:
            continue
        next_svc = out.find("\n  ", idx + len(marker))
        segment = out[idx:next_svc] if next_svc != -1 else out[idx:]
        if "restart:" in segment:
            continue
        insert = segment.rstrip() + "\n    restart: unless-stopped\n"
        out = out[:idx] + insert + (out[next_svc:] if next_svc != -1 else "")
    return out


def main() -> None:
    for lesson in LESSONS:
        out = ROOT / lesson.lesson / "docker-compose.yml"
        out.write_text(compose_for_lesson(lesson), encoding="utf-8")
        patch_readme(ROOT / lesson.lesson, readme_docker_section(lesson))
        print(f"Wrote {out.relative_to(ROOT)}")

    out25 = ROOT / "spring-cloud-25" / "docker-compose.yml"
    out25.write_text(compose_lesson_25(), encoding="utf-8")
    l25 = Lesson(
        "spring-cloud-25",
        [],
        verify=(
            "Nacos http://localhost:8848/nacos；Consumer http://localhost:8888/user/1；"
            "配置快照 http://localhost:8888/config/local"
        ),
    )
    patch_readme(ROOT / "spring-cloud-25", readme_docker_section_nacos(l25))
    print(f"Wrote {out25.relative_to(ROOT)}")

    out26 = ROOT / "spring-cloud-26" / "docker-compose.yml"
    out26.write_text(compose_lesson_26(), encoding="utf-8")
    l26 = Lesson(
        "spring-cloud-26",
        [],
        verify=(
            "Gateway http://localhost:9876/api/user/1 与 "
            "http://localhost:9876/feign/user/1；Nacos http://localhost:8848/nacos"
        ),
    )
    patch_readme(ROOT / "spring-cloud-26", readme_docker_section_nacos(l26))
    print(f"Wrote {out26.relative_to(ROOT)}")

    out27 = ROOT / "spring-cloud-27" / "docker-compose.yml"
    out27.write_text(compose_lesson_27(), encoding="utf-8")
    l27 = Lesson(
        "spring-cloud-27",
        [],
        verify="http://localhost:8888/demo/weight?times=200（weight-high 命中应远多于 weight-low）",
    )
    patch_readme(ROOT / "spring-cloud-27", readme_docker_section_nacos(l27))
    print(f"Wrote {out27.relative_to(ROOT)}")

    out24 = ROOT / "spring-cloud-24" / "docker-compose.yml"
    out24.write_text(compose_lesson_24(), encoding="utf-8")
    l24 = Lesson(
        "spring-cloud-24",
        [],
        verify=(
            "Zipkin http://localhost:9411；先取 Token（见 README）再访问 Gateway "
            "http://localhost:9876；Stream POST http://localhost:7780/messages?body=hi"
        ),
    )
    patch_readme(ROOT / "spring-cloud-24", readme_docker_section(l24))
    print(f"Wrote {out24.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
