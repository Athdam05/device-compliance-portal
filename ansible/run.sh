#!/usr/bin/env bash
# Step 13 helper: builds the lab images and runs the playbook against the managed-node container.
#   bash ansible/run.sh up        build images, create network, start a FRESH managed node
#   bash ansible/run.sh play      run the playbook (idempotent - safe to repeat)
#   bash ansible/run.sh check     dry run (--check --diff)
#   bash ansible/run.sh destroy   remove the managed node and network
set -euo pipefail
cd "$(dirname "$0")/.."
export MSYS_NO_PATHCONV=1                       # keep git-bash from rewriting /work paths
ROOT="$(pwd -W 2>/dev/null || pwd)"             # Windows path for docker -v when in git-bash
NET=dcmp-net; NODE=dcmp-node; HOST_PORT="${HOST_PORT:-8093}"
VERSION="${APP_VERSION:-1.0.6}"

keys() {
  if [ ! -f ansible/keys/id_ed25519 ]; then
    mkdir -p ansible/keys
    ssh-keygen -q -t ed25519 -N "" -C "dcmp-lab-ansible" -f ansible/keys/id_ed25519   # lab-only key, git-ignored
  fi
}

ansible_run() {
  docker run --rm --network "$NET" -v "$ROOT:/work" -e ANSIBLE_CONFIG=/work/ansible/ansible.cfg dcmp-ansible \
    sh -c "mkdir -p /root/.ssh && cp /work/ansible/keys/id_ed25519 /root/.ssh/ && chmod 600 /root/.ssh/id_ed25519 && $*"
}

case "${1:-}" in
  up)
    keys
    docker build -q -t dcmp-ansible -f ansible/Dockerfile.control ansible
    docker build -q -t dcmp-node:base -f ansible/Dockerfile.node ansible
    docker network inspect "$NET" >/dev/null 2>&1 || docker network create "$NET"
    docker rm -f "$NODE" >/dev/null 2>&1 || true
    docker run -d --name "$NODE" --hostname "$NODE" --network "$NET" -p "$HOST_PORT:8080" dcmp-node:base
    sleep 3
    ansible_run "ansible dcmp_servers -m ping"
    ;;
  play)  ansible_run "ansible-playbook playbook.yml -e app_version=$VERSION ${EXTRA:-}" ;;
  check) ansible_run "ansible-playbook playbook.yml -e app_version=$VERSION --check --diff" ;;
  destroy) docker rm -f "$NODE" >/dev/null 2>&1 || true; docker network rm "$NET" >/dev/null 2>&1 || true ;;
  *) echo "usage: $0 up|play|check|destroy"; exit 1 ;;
esac
