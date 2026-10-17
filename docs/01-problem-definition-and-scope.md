# Step 1 – Problem Definition and Scope
**Project:** Automated Device Compliance Management Portal
**Student:** Atharva Anand Damale (23102C0004) – BE CMPN C, 2026-27 ODD Sem

## 1. Problem Statement
Organisations (college labs, small IT teams) track laptops, desktops and servers in
spreadsheets. Checks such as OS patch level, antivirus status, disk encryption and
firewall state are done manually, so non-compliant devices go unnoticed, audits are slow,
and there is no single place to see who is responsible for fixing what.

The portal centralises device records, evaluates each device against compliance rules,
and drives a role-based workflow (Reported -> Under Review -> Remediated -> Closed).

## 2. Target Users & Stakeholders
| Stakeholder | Role in system | Need |
|---|---|---|
| IT Administrator | ADMIN | Register devices, manage rules, close findings |
| Compliance Officer | AUDITOR | Review non-compliant devices, approve remediation |
| Technician | TECHNICIAN | Fix issues, update device status |
| Department Head / Management | Viewer (dashboard) | Summary of compliance posture |
| Course Teacher / Evaluator | External | Verify DevOps pipeline end to end |

## 3. Existing Pain Points
- Spreadsheet records are stale, duplicated and not searchable.
- No ownership/accountability trail for remediation.
- No instant summary (compliant vs non-compliant counts).
- Manual deployment of internal tools is error prone.

## 4. Objectives
1. Create, view, update and search device records.
2. Role-based status workflow for compliance findings.
3. Summary dashboard (total / compliant / non-compliant / under review).
4. Fully automated build, test, containerise and deploy pipeline (CI/CD).

## 5. Constraints
- Individual student project; one semester timeline.
- Java 11, Maven, Spring Boot, embedded H2 DB; Tomcat/Docker targets.
- Free tools only (GitHub, Jenkins, Docker Hub, Ansible).
- Runs on a single local node (Windows 11 + Docker).

## 6. Measurable Success Criteria
- All 15 MVP tasks done and demonstrable.
- >= 4 Selenium journeys pass automatically in Jenkins.
- Commit-to-running-container pipeline completes in < 10 min.
- Ansible re-run reports 0 changed tasks (idempotent); rollback < 2 min.

## 7. Frozen 15-Task MVP Scope
| # | Task |
|---|---|
| 1 | Project skeleton (Spring Boot, Maven) |
| 2 | Device entity & repository (H2) |
| 3 | Create device form |
| 4 | List/view devices |
| 5 | View device details |
| 6 | Update device |
| 7 | Search/filter by name, owner, status |
| 8 | Compliance rule evaluation (OS, AV, encryption, firewall) |
| 9 | User roles (ADMIN, AUDITOR, TECHNICIAN) & login |
| 10 | Status workflow transitions with role checks |
| 11 | Status history log |
| 12 | Summary dashboard |
| 13 | Input validation & error pages |
| 14 | Health endpoint |
| 15 | README & API documentation |

Out of scope: agent-based auto-scanning, email alerts, SSO, multi-tenant.

**Approved by:** Course teacher (pending sign-off)
