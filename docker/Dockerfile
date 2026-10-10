# 从仓库根目录构建：docker compose 中 context 为 ..
# build-arg LESSON=spring-cloud-02  MODULE=spring-cloud-02-service
ARG MAVEN_IMAGE=swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/maven:3.9.9-eclipse-temurin-21
ARG RUNTIME_IMAGE=swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/eclipse-temurin:21-jre

FROM ${MAVEN_IMAGE} AS build
ARG LESSON
ARG MODULE
WORKDIR /src
COPY docker/settings.xml /root/.m2/settings.xml
COPY . .
RUN set -e; \
    for attempt in 1 2 3; do \
      if mvn -s /root/.m2/settings.xml -pl "${LESSON}/${MODULE}" -am -Dmaven.test.skip=true -q package; then \
        break; \
      fi; \
      if [ "$attempt" -eq 3 ]; then exit 1; fi; \
      echo "Maven package failed (attempt ${attempt}/3), retrying in 15s..."; \
      sleep 15; \
    done; \
    JAR="$(find "/src/${LESSON}/${MODULE}/target" -maxdepth 1 -name '*.jar' ! -name '*-sources.jar' ! -name '*-javadoc.jar' | head -1)"; \
    test -n "$JAR"; \
    cp "$JAR" /app.jar

FROM ${RUNTIME_IMAGE}
WORKDIR /app
COPY --from=build /app.jar /app/app.jar
ENV JAVA_OPTS=""
ENTRYPOINT ["sh", "-c", "exec java $JAVA_OPTS -jar /app/app.jar"]
