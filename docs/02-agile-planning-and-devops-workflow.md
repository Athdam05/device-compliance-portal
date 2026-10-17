# Step 2 – Agile Planning and DevOps Workflow
**Project:** Automated Device Compliance Management Portal
**Student:** Atharva Anand Damale (23102C0004)

## 1. User Stories & Acceptance Criteria
| ID | User Story | Acceptance Criteria |
|---|---|---|
| US1 | As an Admin, I want to register a device so it is tracked. | Form validates name, owner, OS, serial; saved device appears in list. |
| US2 | As a user, I want to view all devices and details. | List shows name, owner, status; clicking opens detail page. |
| US3 | As an Admin/Technician, I want to update a device. | Edits persist; validation errors shown inline. |
| US4 | As a user, I want to search devices. | Search by name/owner/status returns matching rows; empty result message shown. |
| US5 | As an Auditor, I want devices auto-evaluated against rules. | Device with outdated OS / no AV / no encryption / firewall off is flagged NON_COMPLIANT. |
| US6 | As a user, I want to log in with a role. | Wrong credentials rejected; menus depend on role. |
| US7 | As staff, I want a status workflow. | Only allowed transitions per role (Technician: Reported->Under Review->Remediated; Auditor/Admin: ->Closed). |
| US8 | As an Auditor, I want status history. | Each transition stores who, when, from, to. |
| US9 | As a manager, I want a dashboard. | Shows totals of compliant, non-compliant, under review devices. |
| US10 | As an Ops engineer, I want a health endpoint. | `/actuator/health` returns UP. |

## 2. Product Backlog (prioritised, 15 tasks)
| # | Task | Story | Pts | Sprint |
|---|---|---|---|---|
| 1 | Project skeleton (Spring Boot, Maven) | - | 2 | 1 |
| 2 | Device entity & repository | US1 | 3 | 1 |
| 3 | Create device form | US1 | 3 | 1 |
| 4 | List/view devices | US2 | 2 | 1 |
| 5 | Device details page | US2 | 2 | 1 |
| 6 | Update device | US3 | 3 | 2 |
| 7 | Search/filter | US4 | 3 | 2 |
| 8 | Compliance rule engine | US5 | 5 | 2 |
| 9 | Roles & login | US6 | 5 | 2 |
| 10 | Status workflow w/ role checks | US7 | 5 | 3 |
| 11 | Status history log | US8 | 3 | 3 |
| 12 | Summary dashboard | US9 | 3 | 3 |
| 13 | Validation & error pages | US1,3 | 2 | 3 |
| 14 | Health endpoint | US10 | 1 | 3 |
| 15 | README & API docs | - | 2 | 3 |

## 3. Sprint Plan (3 sprints x ~1 week)
- **Sprint 1 – Foundation & Feature 1:** tasks 1-5 (device create/list/view). Goal: first working workflow.
- **Sprint 2 – Core MVP:** tasks 6-9 (update, search, rules, login).
- **Sprint 3 – Workflow & Release:** tasks 10-15, release tag v1.0.0.
DevOps work (Jenkins, Docker, Ansible) runs in parallel as a pipeline track.

## 4. Kanban Board (current state)
| Backlog | To Do | In Progress | Review | Done |
|---|---|---|---|---|
| 6-15 | 2,3,4,5 | 1 | - | Step 1 scope, Step 2 planning |

Columns WIP limit: In Progress <= 2, Review <= 2. Board maintained as GitHub Project / Issues.

## 5. Definition of Done
- Code compiled, merged to `develop` via reviewed pull request.
- Unit tests pass; Selenium journey for the feature passes.
- Jenkins build is green.
- Acceptance criteria demonstrated.
- README/docs updated; no critical warnings.
- Deployable as WAR and Docker image.

## 6. DevOps Lifecycle Diagram
```
 PLAN ──► CODE ──► BUILD ──► TEST ──► RELEASE ──► DEPLOY ──► OPERATE ──► MONITOR
  │        │         │         │          │           │           │          │
 GitHub   Git/     Maven    Selenium   Git tag +   Tomcat /   Ansible    /actuator/
 Issues   branches (Jenkins) +JUnit    Docker Hub  Docker     playbook   health
 Kanban   + PRs    job       in Jenkins image      container  idempotent  + logs
   ▲                                                                        │
   └─────────────────────── feedback / new backlog items ◄─────────────────┘
```
Flow: commit -> GitHub -> Jenkins (checkout, build, test, package) -> Docker image -> registry -> Ansible deploys container -> health check -> rollback to previous image if failed.
