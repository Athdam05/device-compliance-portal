# Step 13 – Configuration Management Script (Ansible)
**Student:** Atharva Anand Damale (23102C0004)

## 1. Configuration specification – what the portal needs on a server
| Category | Requirement | Ansible task |
|---|---|---|
| **Packages** | `openjdk-11-jre-headless` (the app is built for Java 11), `curl`, `ca-certificates`, `supervisor` (process manager) | `apt` – Install prerequisite packages |
| **User / group** | system group `dcmp` and unprivileged system user `dcmp` (shell `/usr/sbin/nologin`, home `/opt/dcmp`) | `group`, `user` |
| **Folders** | `/opt/dcmp` (0755), `/opt/dcmp/releases/<version>` (0755), `/var/lib/dcmp/data` (0750, H2 database), `/var/log/dcmp` (0755) – all owned by `dcmp` | `file` (loop) |
| **Files** | `/opt/dcmp/releases/<version>/app.war` (0640, from the Jenkins-built artefact); symlink `/opt/dcmp/current` → active release; `/etc/supervisor/conf.d/dcmp.conf` (service definition from a Jinja2 template) | `copy`, `file state=link`, `template` |
| **Ports** | application listens on **8080/tcp** (published as 8093 on the lab host); sshd on 22/tcp for Ansible | `wait_for` |
| **Services** | `dcmp` runs under supervisor as user `dcmp`, auto-start and auto-restart, env `SPRING_PROFILES_ACTIVE`, `SPRING_DATASOURCE_URL=jdbc:h2:file:/var/lib/dcmp/data/dcmp` | handler `supervisorctl reread / update / restart` |
| **Verification** | `GET /actuator/health` must return 200 and contain `UP` | `uri` with retries |

All tunable values (version, profile, port, folders, heap) are in [`ansible/group_vars/all.yml`](../ansible/group_vars/all.yml).
The deployed layout keeps one folder per version, so a previous release can be re-activated by repointing `current` (used in step 14).

## 2. Files
| File | Purpose |
|---|---|
| `ansible/inventory/hosts.ini` | inventory – group `dcmp_servers`, host `dcmp-node`, SSH user/key |
| `ansible/playbook.yml` | the playbook (14 tasks + 1 handler) |
| `ansible/templates/dcmp.conf.j2` | supervisor program definition |
| `ansible/group_vars/all.yml` | variables |
| `ansible/ansible.cfg` | Ansible settings |
| `ansible/Dockerfile.control` / `Dockerfile.node` | lab control node (Ansible in `python:3.12-slim`) and fresh managed node (`ubuntu:22.04` + sshd + python3 + supervisord) |
| `ansible/run.sh` | `up` / `play` / `check` / `destroy` helper |

## 3. Lab setup
Windows cannot run Ansible as a control node, so Ansible runs in a container; the target is a **fresh Ubuntu 22.04 container**
on the same Docker network (`dcmp-net`), reached over SSH with a lab-only ed25519 key (generated locally by `run.sh`, git-ignored).
The managed node starts with only sshd, python3, sudo and supervisord – everything else is installed by the playbook.
```
bash ansible/run.sh up      # build images, start fresh node, ansible -m ping  → "pong"
bash ansible/run.sh play    # ansible-playbook playbook.yml -e app_version=1.0.6
```

## 4. First execution (log: [`ansible/logs/first-run.log`](../ansible/logs/first-run.log))
`PLAY RECAP: dcmp-node ok=14 changed=8 unreachable=0 failed=0`

Changed on first run: packages, group, user, folders, WAR, `current` symlink, supervisor definition, service restart (handler).
Report task output: `dcmp 1.0.6 (env=dev) is UP on port 8080`.

### Independent verification of the node (not just the Ansible log)
| Check | Result |
|---|---|
| Health from the host via published port | `curl localhost:8093/actuator/health` → `{"status":"UP"}` |
| User | `uid=999(dcmp)` |
| Layout | `current -> /opt/dcmp/releases/1.0.6`; `app.war` owned by `dcmp`, mode 0640 |
| Java | `openjdk version "11.0.32.1"` |
| Service | `supervisorctl status`: `dcmp RUNNING`, `sshd RUNNING`; java process runs as user `dcmp` |
| Application | login as the seeded admin returns 302 (success) |

### Idempotency preview (log: [`ansible/logs/second-run.log`](../ansible/logs/second-run.log))
Re-running immediately gives `ok=13 changed=0 failed=0`. Formal evidence is part of step 14.

## 5. Known limitations
- `--check` (dry run) fails on a *brand-new* node (`python3-apt must be installed to use check mode`) because that
  node has not been prepared yet; real runs install it automatically. Dry runs work on an already-configured node.
- The managed node is a container, so supervisor is used instead of systemd; on a normal VM the `template` + handler would
  produce a systemd unit instead.
- The SSH key and the 44 MB WAR are not committed (`ansible/keys/`, `ansible/artifacts/` are git-ignored).
  `run.sh` creates the key; the WAR is copied from the Jenkins build archive (build #6 → version 1.0.6).
