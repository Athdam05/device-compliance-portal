# Step 11 – Docker Image and Container Lifecycle
**Student:** Atharva Anand Damale (23102C0004)

## 1. Dockerfile ([../Dockerfile](../Dockerfile))
Multi-stage build:
1. **build stage** `maven:3.9.9-eclipse-temurin-11` – resolves dependencies (cached layer) and runs `mvn package -DskipTests`
   (tests are run earlier in the Jenkins pipeline).
2. **runtime stage** `eclipse-temurin:11-jre` – copies only the executable WAR; runs as unprivileged user `dcmp`.

Key settings: `EXPOSE 8080`, `VOLUME /data` (H2 database file), `HEALTHCHECK` on `/actuator/health`,
environment defaults `SPRING_PROFILES_ACTIVE=dev`, `SPRING_DATASOURCE_URL=jdbc:h2:file:/data/dcmp`, `PORT=8080`.
`.dockerignore` keeps `target/`, `.git/`, docs and local data out of the build context.

## 2. Build and tag
```
docker build -t device-compliance-portal:1.0.0 -t device-compliance-portal:latest .
docker image ls device-compliance-portal
```
| Image | ID | Disk usage | Content size |
|---|---|---|---|
| device-compliance-portal:1.0.0 / :latest | 757ff9f424f4 | 526 MB | 146 MB |

Runs as user `dcmp` (uid 999), exposes port 8080.

## 3. Container lifecycle (real run – full output in [11-docker-command-log.txt](11-docker-command-log.txt))
Reproducible with `bash scripts/docker-lifecycle-demo.sh`.

| Phase | Command | Observed result |
|---|---|---|
| Create + start, map ports, mount volume | `docker run -d --name dcmp-demo -p 8090:8080 -v dcmp-data:/data device-compliance-portal:1.0.0` | container started |
| Health | `curl http://localhost:8090/actuator/health` | `{"status":"UP"}`; `docker ps` shows `Up … (healthy)`, `0.0.0.0:8090->8080/tcp` |
| Inspect | `docker inspect`, `docker stats --no-stream`, `docker exec dcmp-demo id` | `status=running`, `health=healthy`, `uid=999(dcmp)` |
| Logs | `docker logs --tail 5 dcmp-demo` | Spring Boot startup lines |
| Stop | `docker stop dcmp-demo` | status `Exited (143)` (SIGTERM, graceful) |
| Start / restart | `docker start dcmp-demo`, `docker restart dcmp-demo` | health UP again |
| Remove | `docker rm -f dcmp-demo` | container gone from `docker ps -a` |
| Clean up volume | `docker volume rm dcmp-data` | volume removed |

### Data persistence check
Created a device in a container with volume `dcmp-persist-data`, destroyed the container (`docker rm -f`), started a **new**
container on the same volume and listed devices: the device `Persist-Check` was still present. (Test containers/volume removed afterwards.)

## 4. Notes
- Host port 8090 is used for the demo so it does not clash with Tomcat (8081), Jenkins (9090) or the Selenium test instance (8082).
- Login seeding (`admin/admin123` etc.) happens on first start of an empty database, so a fresh volume always has the demo users.
- Docker Desktop had to be started manually before the engine was reachable.
