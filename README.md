# Automated Device Compliance Management Portal

DevOps mini project – **Atharva Anand Damale (23102C0004)**, BE CMPN C, Academic Year 2026-27.

A web portal to register devices, evaluate them against compliance rules (OS, antivirus,
disk encryption, firewall), and manage remediation through a role-based status workflow
with a summary dashboard.

## Tech stack
Java 11 · Spring Boot 2.7 · Thymeleaf · H2 · Maven · Tomcat/Docker · Jenkins · Selenium · Ansible

## Run locally
```bash
mvn clean package
mvn spring-boot:run
# http://localhost:8080  |  health: /actuator/health
```

## Repository structure
```
src/main/java      application code
src/main/resources templates + config
src/test           unit / Selenium tests
docs/              step-wise project documentation
.github/           issue templates
```

## Branch policy
| Branch | Purpose |
|---|---|
| `main` | stable, tagged releases only |
| `develop` | integration branch; PRs merge here |
| `feature/<issue#>-<short-name>` | new features (e.g. `feature/3-create-device`) |
| `bugfix/<issue#>-<short-name>` | bug fixes |
| `hotfix/<short-name>` | urgent fixes from `main` |

Rules: no direct pushes to `main`/`develop`; every change via pull request with review;
commit messages follow `type: summary` (`feat`, `fix`, `docs`, `test`, `chore`, `ci`).

## Documentation
Step-by-step documentation (one file per step where a written deliverable exists):

1. [Problem definition & scope](docs/01-problem-definition-and-scope.md)
2. [Agile planning & DevOps workflow](docs/02-agile-planning-and-devops-workflow.md)
3. [Requirements, architecture & setup](docs/03-requirements-architecture-setup.md)
6. [MVP completion & Git collaboration](docs/06-mvp-completion-and-git-collaboration.md)
9. [Selenium test plan](docs/09-selenium-test-plan.md)
10. [Continuous testing in Jenkins](docs/10-continuous-testing-in-jenkins.md)
11. [Docker image & container lifecycle](docs/11-docker-image-and-container-lifecycle.md)
12. [Jenkins-Docker continuous deployment](docs/12-jenkins-docker-continuous-deployment.md)
13. [Configuration management (Ansible)](docs/13-configuration-management.md)
14. [Provisioning, idempotency and rollback](docs/14-provisioning-and-reliability.md)

Steps 4, 5, 7 and 8 (repository, feature branch, Jenkins job, pipeline) are evidenced by the repository itself (README, issues, pull requests,
`Jenkinsfile`) and in the final report: [report/DCMP_DevOps_Report.pdf](report/DCMP_DevOps_Report.pdf) - all 14 steps with screenshots and outputs.
