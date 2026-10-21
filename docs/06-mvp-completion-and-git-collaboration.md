# Step 6 – MVP Completion and Git Collaboration
**Student:** Atharva Anand Damale (23102C0004)

## 1. Updated Backlog (end of Sprint 3)
| # | Task | Status | Delivered in |
|---|---|---|---|
| 1 | Project skeleton (Spring Boot, Maven) | Done | main (initial commits) |
| 2 | Device entity & repository | Done | PR #1 `feature/1-device-create-list-view` |
| 3 | Create device form | Done | PR #1 |
| 4 | List/view devices | Done | PR #1 |
| 5 | Device details page | Done | PR #1 |
| 6 | Update device | Done | PR #3 `feature/2-update-search-dashboard` |
| 7 | Search/filter (name, owner, status) | Done | PR #3 |
| 8 | Compliance rule evaluation | Done (simplified) | PR #1 – antivirus + disk encryption + firewall. **OS-version rule deferred** to backlog |
| 9 | User roles & login (BCrypt, session) | Done | PR #4 `feature/3-roles-workflow` |
| 10 | Status workflow with role checks | Done | PR #4 |
| 11 | Status history log | Done | PR #4 |
| 12 | Summary dashboard | Done | PR #3 |
| 13 | Input validation & error pages | Done (validation); custom error pages deferred | PR #1 |
| 14 | Health endpoint | Done | `/actuator/health` |
| 15 | README & documentation | Done (docs 01-06, README) | main |

**Carried over to next backlog:** OS-version compliance rule, custom error pages, REST/JSON API docs.

## 2. Role matrix (implemented)
| Role | Allowed status moves |
|---|---|
| TECHNICIAN | REPORTED → UNDER_REVIEW → REMEDIATED |
| AUDITOR | REMEDIATED → CLOSED, REMEDIATED → UNDER_REVIEW (reopen) |
| ADMIN | all of the above |

Demo users (seeded, passwords stored as BCrypt hashes): `admin/admin123`, `auditor/auditor123`, `tech/tech123`.
These are demo credentials for the coursework only.

## 3. Git collaboration evidence
- **Second feature branch:** `feature/3-roles-workflow` created from `develop` while `feature/2-update-search-dashboard` was still open.
- **Conflict creation:** both branches edited the header line of `src/main/resources/templates/devices/list.html`
  (feature/2 added the Dashboard link + search form; feature/3 added the logged-in user + logout button).
  After PR #3 was merged into `develop`, merging `origin/develop` into feature/3 produced:
  `CONFLICT (content): Merge conflict in src/main/resources/templates/devices/list.html`.
- **Resolution:** kept both changes in a single header (commit `bb8f57f`). The feature/2 tests were also updated to
  authenticate, since the login interceptor now protects `/devices/**` and `/dashboard`.
  Result: 11 tests pass; manual smoke test of login, workflow, history, search and dashboard succeeded.
- **Pull requests:** #1/#2 (feature 1), #3 (feature 2), #4 (feature 3, with conflict resolution).
- **Tag:** `v1.0.0` marks the release-ready baseline on `main` (created after the release PR merges).

## 4. Release-ready baseline
`mvn clean package` → `target/device-compliance-portal-0.1.0-SNAPSHOT.war` (bootable and Tomcat-deployable).
