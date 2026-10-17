# Step 3 – Requirements, Architecture and Technology Setup
**Student:** Atharva Anand Damale (23102C0004)

## 1. SRS Summary
**Functional:** FR1 create device · FR2 view list/details · FR3 update · FR4 search (name/owner/status) ·
FR5 compliance evaluation · FR6 login with roles · FR7 role-based status workflow · FR8 status history · FR9 dashboard · FR10 health endpoint.
**Non-functional:** NFR1 page response < 2 s · NFR2 passwords hashed · NFR3 deployable as WAR (Tomcat) and Docker image ·
NFR4 automated build/test/deploy · NFR5 idempotent provisioning.

## 2. Technology Stack
| Layer | Choice |
|---|---|
| Language / Framework | Java 11, Spring Boot 2.7 (MVC, Data JPA, Validation, Actuator) |
| UI | Thymeleaf server-side templates |
| Build tool | Apache Maven 3.9.9 |
| Database | H2 (file mode) |
| Deployment target | Apache Tomcat 9 (WAR) and Docker container |
| CI/CD | Git/GitHub, Jenkins, Docker Hub |
| Testing | JUnit 5, Selenium WebDriver |
| Config management | Ansible |

## 3. Use-Case Diagram
```
 Admin ───────┬─ Register device ──┐
              ├─ Update device     │
 Technician ──┼─ Search devices    ├──► [Device Compliance Portal]
              ├─ Move status       │
 Auditor ─────┼─ Approve / close   │
              └─ View dashboard ───┘
 (all roles) ── Login
```
Admin: all use cases. Technician: search, view, update, Reported→Under Review→Remediated. Auditor: view, dashboard, Remediated→Closed / reopen.

## 4. Architecture Diagram
```
 Browser ─HTTP─► Controller (Spring MVC) ─► Service (rules, workflow) ─► Repository (JPA) ─► H2 DB
                       │                                                     
                  Thymeleaf views            Actuator /actuator/health
 Packaged as WAR ──► Tomcat   |   Docker image ──► container
```

## 5. Data Model
**Device**(id, name, owner, serialNo, os, osVersion, antivirusEnabled, diskEncrypted, firewallEnabled, complianceState, workflowStatus, createdAt, updatedAt)
**AppUser**(id, username, passwordHash, role)
**StatusHistory**(id, deviceId, fromStatus, toStatus, changedBy, changedAt)
Relations: Device 1—* StatusHistory.

## 6. API / Route List
| Method | Path | Purpose |
|---|---|---|
| GET | /login | login page |
| GET | /devices | list + search (`?q=&status=`) |
| GET | /devices/new · POST /devices | create |
| GET | /devices/{id} | details |
| GET | /devices/{id}/edit · POST /devices/{id} | update |
| POST | /devices/{id}/status | workflow transition |
| GET | /dashboard | summary |
| GET | /actuator/health | health check |

## 7. Local Development Setup (verified)
Prerequisites: JDK 11, Maven 3.9.9, Git.
```
mvn clean package        # builds target/device-compliance-portal-0.1.0-SNAPSHOT.war, runs tests
mvn spring-boot:run      # starts on http://localhost:8080
curl http://localhost:8080/actuator/health   # {"status":"UP"}
```
