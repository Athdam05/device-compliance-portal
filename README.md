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
1. [Problem definition & scope](docs/01-problem-definition-and-scope.md)
2. [Agile planning & DevOps workflow](docs/02-agile-planning-and-devops-workflow.md)
3. [Requirements, architecture & setup](docs/03-requirements-architecture-setup.md)
