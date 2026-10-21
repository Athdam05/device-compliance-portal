# Step 14 – Automated Provisioning and Reliability Validation
**Student:** Atharva Anand Damale (23102C0004)

All runs use `ansible/playbook.yml` (and `ansible/rollback.yml`) against a managed node container; raw logs are in `ansible/logs/`.

## 1. Clean target environment (log: `step14-0-clean-node.log`)
A brand-new Ubuntu 22.04 node (`dcmp-node`, image `dcmp-node:base`) was created. It only has sshd, python3, sudo and supervisord.
Proof that it is clean before provisioning: `java: NOT installed`, `id: 'dcmp': no such user`, `/opt/dcmp: No such file or directory`.

## 2. Provisioning (log: `step14-1-provision-1.0.6.log`)
`APP_VERSION=1.0.6 bash ansible/run.sh play`
**Result:** `ok=17 changed=8 failed=0` – packages, user, folders, WAR, `current` symlink, service definition installed;
`dcmp 1.0.6 (env=dev) is UP on port 8080`.

## 3. Idempotency (log: `step14-2-idempotency-rerun.log`)
Same command run again on the configured node: **`ok=16 changed=0 failed=0`** – nothing was changed.

## 4. Health check
Built into the playbook: wait for port 8080, then `GET /actuator/health` must return 200 and contain `UP` (retries 6 x 5 s).
Observed from the host through the published port: `curl localhost:8093/actuator/health` → `{"status":"UP"}`.
Upgrade to release **1.0.7** (`step14-3-upgrade-1.0.7.log`, `changed=5`, message "active release: '1.0.6' -> new release: '1.0.7'")
changes the home page to `Release: 1.0.7`.

## 5. Rollback / recovery demonstrations
| # | Scenario | How | Result |
|---|---|---|---|
| A | **Bad release is rejected and rolled back automatically** (`step14-4-bad-release-auto-rollback.log`) | Deploy release `1.0.8`, a deliberately corrupted WAR (simulated bad artefact). The JVM cannot start, so the health check fails. | Play enters the `rescue` section: *"ROLLBACK – release 1.0.8 failed its health check; restoring previous release '1.0.7'"*, re-points `/opt/dcmp/current` to `releases/1.0.7`, removes the failed folder, restores the service definition, restarts, health check **UP**. Final message: *"Release 1.0.8 FAILED health check - rolled back to 1.0.7 (UP)."* The play is marked failed on purpose so the bad release is reported. Page afterwards: `Release: 1.0.7`. |
| B | **Manual rollback to an earlier stable release** (`step14-5-manual-rollback-1.0.6.log`) | `APP_VERSION=1.0.6 bash ansible/run.sh rollback` (`rollback.yml`) | "rolling back '1.0.7' -> '1.0.6'", "rollback complete: release 1.0.6 is UP", `current -> /opt/dcmp/releases/1.0.6` |
| C | **Process crash** (`step14-6-crash-and-reboot-recovery.log`) | `kill -9` of the application's java process | supervisor restarts it automatically; health returns `UP` |
| D | **Node reboot** (same log) | `docker restart dcmp-node` | sshd and the application start again by themselves; health `UP` |
| E | Promote latest stable (`step14-7-final-1.0.7.log`) | `APP_VERSION=1.0.7 bash ansible/run.sh play` | `active release '1.0.6' -> '1.0.7'`, UP, final state of the lab node is 1.0.7 |

## 6. Problem found and fixed during testing
The first attempt at scenario A (`step14-4a-first-attempt-label-bug.log`) did roll back the code and the app was healthy, but the home page
still said `Release: 1.0.8`: the rollback restored the symlink but not the service definition, which still carried the failed release's
`APP_VERSION` label. Fix: the `rescue` section now re-renders the service definition with the previous release label (variable `release_label`)
before restarting. Re-test: page shows `Release: 1.0.7` after the failed deployment. (Note: Ansible extra-vars `-e app_version=…` always win over
task-level `vars`, so a separate variable name was needed.)

## 7. How it works
Releases live in `/opt/dcmp/releases/<version>/app.war`; `/opt/dcmp/current` is a symlink to the active release. Deployment records the old
link target, switches the link, restarts and health-checks; any failure triggers the rescue path. Because old releases stay on disk (only a *failed*
release folder is removed), a manual rollback is just re-pointing the link.

## 8. Limitations
- The node is a container (supervisor instead of systemd) and the "bad release" is a corrupted file, not a real faulty build.
- Release 1.0.7 includes the small change that shows the release label on the home page (`app.version`).
- Rollback restores code and service definition; the H2 database on `/var/lib/dcmp/data` is shared across releases and is not rolled back.
- Naming: the Ansible release labels (1.0.6, 1.0.7, 1.0.8) are independent of the Docker image tags in step 12 (`dcmp:1.0.N`, where N is the Jenkins build number). Release 1.0.6 was deliberately taken from Jenkins build #6; 1.0.7 is a locally built WAR that adds the release label to the home page.
