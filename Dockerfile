# Step 11 - container image for the Device Compliance Management Portal.
# Two stages: Maven builds the WAR, a slim JRE image runs it (Spring Boot executable WAR, embedded Tomcat).

# ---- build stage ----
FROM maven:3.9.9-eclipse-temurin-11 AS build
WORKDIR /build
COPY pom.xml .
RUN mvn -B -q dependency:go-offline
COPY src ./src
RUN mvn -B -q clean package -DskipTests

# ---- runtime stage ----
FROM eclipse-temurin:11-jre
LABEL org.opencontainers.image.title="device-compliance-portal" \
      org.opencontainers.image.authors="Atharva Anand Damale (23102C0004)"

# run as an unprivileged user; /data holds the H2 database so it can be mounted as a volume
RUN useradd --system --create-home dcmp && mkdir /data && chown dcmp /data
USER dcmp
WORKDIR /app
COPY --from=build /build/target/device-compliance-portal-*.war app.war

ENV PORT=8080 \
    SPRING_PROFILES_ACTIVE=dev \
    SPRING_DATASOURCE_URL=jdbc:h2:file:/data/dcmp;AUTO_SERVER=TRUE
EXPOSE 8080
VOLUME /data

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
  CMD curl -fs http://localhost:${PORT}/actuator/health || exit 1

ENTRYPOINT ["java", "-jar", "app.war"]
