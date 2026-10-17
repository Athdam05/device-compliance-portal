#!/usr/bin/env bash
# Step 11 - walks through the complete container lifecycle and prints every command it runs.
# Usage: bash scripts/docker-lifecycle-demo.sh   (image device-compliance-portal:1.0.0 must already be built)
set -u
IMAGE=device-compliance-portal
TAG=1.0.0
NAME=dcmp-demo
HOST_PORT=8090

run() { echo; echo "\$ $*"; "$@"; }

run docker image ls "$IMAGE"
run docker image inspect "$IMAGE:$TAG" --format 'id={{.Id}} size={{.Size}} os={{.Os}}/{{.Architecture}} user={{.Config.User}} exposed={{.Config.ExposedPorts}}'
run docker history --no-trunc=false "$IMAGE:$TAG"

docker rm -f "$NAME" >/dev/null 2>&1

echo; echo "== 1. create + start (map host $HOST_PORT -> container 8080, named volume for the database)"
run docker run -d --name "$NAME" -p "$HOST_PORT:8080" -v dcmp-data:/data "$IMAGE:$TAG"

echo; echo "== 2. wait for the application"
for i in $(seq 1 40); do
  curl -fs "http://localhost:$HOST_PORT/actuator/health" >/dev/null 2>&1 && break
  sleep 3
done
run curl -s "http://localhost:$HOST_PORT/actuator/health"; echo
run docker ps --filter "name=$NAME"

echo; echo "== 3. inspect logs / state / resource use"
run docker logs --tail 5 "$NAME"
run docker inspect "$NAME" --format 'status={{.State.Status}} pid={{.State.Pid}} ports={{.NetworkSettings.Ports}} health={{.State.Health.Status}}'
run docker stats --no-stream "$NAME"
run docker exec "$NAME" sh -c 'id && ls -l /data'

echo; echo "== 4. stop"
run docker stop "$NAME"
run docker ps -a --filter "name=$NAME"

echo; echo "== 5. restart (data volume survives)"
run docker start "$NAME"
for i in $(seq 1 40); do
  curl -fs "http://localhost:$HOST_PORT/actuator/health" >/dev/null 2>&1 && break
  sleep 3
done
run curl -s "http://localhost:$HOST_PORT/actuator/health"; echo
run docker restart "$NAME"

echo; echo "== 6. remove container (volume kept), then clean up"
run docker rm -f "$NAME"
run docker ps -a --filter "name=$NAME"
run docker volume ls --filter name=dcmp-data
run docker volume rm dcmp-data
