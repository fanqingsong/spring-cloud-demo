#!/bin/sh
set -e

NACOS_SERVER="${NACOS_SERVER:-nacos:8848}"
BASE="http://${NACOS_SERVER}"

wait_nacos() {
	i=0
	while [ "$i" -lt 60 ]; do
		if curl -sf "${BASE}/nacos/v1/console/health/readiness" >/dev/null; then
			return 0
		fi
		i=$((i + 1))
		sleep 2
	done
	echo "Nacos 未就绪: ${BASE}" >&2
	exit 1
}

post_config() {
	dataId=$1
	group=$2
	content=$3
	curl -sf -X POST "${BASE}/nacos/v1/cs/configs" \
		--data-urlencode "dataId=${dataId}" \
		--data-urlencode "group=${group}" \
		--data-urlencode "content=${content}"
}

wait_nacos

post_config "spring-cloud-nacos-common.properties" "SHARED" "common.course-tag=Roncoo-Nacos-Demo
common.config-source=nacos-config-center"

post_config "spring-cloud-nacos-provider.properties" "DEFAULT_GROUP" "provider.greeting=你好，来自 Nacos 配置中心
provider.instance-tag=provider-primary"

post_config "spring-cloud-nacos-consumer.properties" "DEFAULT_GROUP" "consumer.hint=可在控制台修改本配置，观察动态刷新"

echo "Nacos 演示配置已导入。"
