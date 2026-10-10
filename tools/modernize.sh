#!/usr/bin/env bash
# Bulk dependency & config refresh for Spring Cloud demo (Boot 1.5 / Netflix -> Boot 3.4 / current stack)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "Updating pom.xml files..."
find . -name 'pom.xml' -not -path './pom.xml' | while read -r f; do
  sed -i \
    -e 's|<version>1\.5\.[0-9]*\.RELEASE</version>|<version>3.4.7</version>|g' \
    -e 's|<version>Dalston\.BUILD-SNAPSHOT</version>|<version>2024.0.3</version>|g' \
    -e 's|<version>Camden\.SR6</version>|<version>2024.0.3</version>|g' \
    -e 's|<java\.version>1\.8</java\.version>|<java.version>21</java.version>|g' \
    -e 's|spring-cloud-starter-eureka-server|spring-cloud-starter-netflix-eureka-server|g' \
    -e 's|spring-cloud-starter-eureka</artifactId>|spring-cloud-starter-netflix-eureka-client</artifactId>|g' \
    -e 's|spring-cloud-starter-feign|spring-cloud-starter-openfeign|g' \
    -e 's|spring-cloud-starter-hystrix-dashboard||g' \
    -e 's|spring-cloud-starter-hystrix|spring-cloud-starter-circuitbreaker-resilience4j|g' \
    -e 's|spring-cloud-starter-turbine|spring-boot-starter-actuator|g' \
    -e 's|spring-cloud-starter-zuul|spring-cloud-starter-gateway|g' \
    "$f"
done

echo "Updating Java imports..."
find . -name '*.java' | while read -r f; do
  sed -i \
    -e 's|org.springframework.cloud.netflix.feign.FeignClient|org.springframework.cloud.openfeign.FeignClient|g' \
    -e 's|org.springframework.cloud.netflix.feign.EnableFeignClients|org.springframework.cloud.openfeign.EnableFeignClients|g' \
    -e 's|javax.servlet|jakarta.servlet|g' \
    "$f"
done

echo "Updating application.properties security keys..."
find . -name 'application.properties' | while read -r f; do
  sed -i \
    -e 's|^security\.basic\.enabled=.*||g' \
    -e 's|^security\.user\.name=|spring.security.user.name=|g' \
    -e 's|^security\.user\.password=|spring.security.user.password=|g' \
    "$f"
done

echo "Done."
