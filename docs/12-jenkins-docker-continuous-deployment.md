# Step 12 – Jenkins–Docker Continuous Deployment
**Student:** Atharva Anand Damale (23102C0004)

## 1. Registry
A private local registry runs as a container (no account or credentials needed):
```
docker run -d --name registry --restart unless-stopped -p 5000:5000 -v registry-data:/var/lib/registry registry:2
curl http://localhost:5000/v2/_catalog        # {"repositories":["dcmp"]}
```

## 2. Pipeline (`Jenkinsfile`, branch `feature/8-docker-cd`)
```
Checkout → Build (11 unit tests) → Package → Selenium Tests (6 browser tests) → Deploy (Tomcat) → Verify
         → Docker Build → Docker Push → Docker Deploy
```
The three Docker stages are only reached if every earlier stage passed (a failing test stops the pipeline – see step 10).

| Stage | What it does |
|---|---|
| Docker Build | `docker build --label git.commit=<sha> -t localhost:5000/dcmp:1.0.<BUILD_NUMBER> -t localhost:5000/dcmp:latest .` |
| Docker Push | pushes both tags and prints `/v2/dcmp/tags/list` from the registry |
| Docker Deploy | `docker rm -f dcmp-app`, `docker pull` the new version **back from the registry**, `docker run -d --name dcmp-app -p 8092:8080 -v dcmp-app-data:/data -e SPRING_PROFILES_ACTIVE=<DEPLOY_ENV>`, then waits for `/actuator/health` |

Parameters/variables: `DEPLOY_ENV` (Jenkins parameter → Spring profile), `APP_VERSION=1.0.${BUILD_NUMBER}`, `REGISTRY=localhost:5000`, `DOCKER_PORT=8092`.

## 3. Evidence – build #6 (commit `192d536`)
| Check | Result |
|---|---|
| Unit tests | 11 / 11 passed |
| Selenium | 6 / 6 passed |
| Registry tags | `{"name":"dcmp","tags":["latest","1.0.6"]}` |
| Container | `dcmp-app  localhost:5000/dcmp:1.0.6  Up (healthy)  0.0.0.0:8092->8080/tcp` |
| Image traceability | label `git.commit` = `192d536acf4ee300388c2038a1a433e0c1a96c7f` (same as the commit built) |
| Application | `/actuator/health` → `UP`; home page shows `Environment: DEV`; login works |
| Pipeline | `Finished: SUCCESS` |

Deployed URLs: Docker `http://localhost:8092/` · Tomcat `http://localhost:8081/dcmp/` · Registry `http://localhost:5000/v2/_catalog`.

## 4. Notes and limitations
- Build #6 was started manually (**Build with Parameters**). **Build #7 was started automatically** by SCM polling after the docs commit `386d8d0` was pushed to `feature/8-docker-cd` (Jenkins: "Started by an SCM change"); it built, tested, pushed `dcmp:1.0.7` and redeployed the container without any click - the end-to-end commit-to-container flow. Registry tags: `1.0.6`, `1.0.7`, `latest`.
- The registry is plain HTTP on localhost, which Docker permits without extra configuration. It is not suitable for a remote host.
- Every build adds a new `1.0.N` tag, so earlier versions stay available in the registry – used for rollback in step 14.
- The Tomcat deployment from step 8 still runs in the same pipeline; the Docker container is an additional deployment target.
