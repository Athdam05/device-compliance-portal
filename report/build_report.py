"""Builds the step-by-step evidence report (HTML -> PDF) for the DevOps mini project.
All screenshots in report/shots, all terminal text in report/txt are real captures; this script only lays them out."""
import html
import os
import re
import subprocess
import sys

import markdown
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SHOTS = os.path.join(HERE, "shots")
PENDING = []

SHEET = r"C:\Users\damal\Downloads\CMPN-C.xlsx"
COLS = "EFGHIJKLMNOPQR"


# ----------------------------------------------------------------------------- helpers
def esc(t):
    return html.escape(t)


def img(name, caption, width=None):
    path = os.path.join(SHOTS, name + ".png")
    if not os.path.exists(path):
        PENDING.append(name)
        return f'<div class="pending">SCREENSHOT PENDING: {esc(name)}<br>{esc(caption)}</div>'
    style = f' style="max-width:{width}"' if width else ""
    return (f'<figure><img src="shots/{name}.png"{style}><figcaption>{esc(caption)}</figcaption></figure>')


def term(name, caption):
    """terminal render; handles multi-page renders (_p1, _p2 ...)"""
    out, i = "", 1
    if os.path.exists(os.path.join(SHOTS, f"term_{name}.png")):
        return img(f"term_{name}", caption)
    while os.path.exists(os.path.join(SHOTS, f"term_{name}_p{i}.png")):
        out += img(f"term_{name}_p{i}", f"{caption} (part {i})")
        i += 1
    return out or img(f"term_{name}", caption)


def code(path, title, start=None, end=None, maxlines=None):
    full = os.path.join(ROOT, path)
    lines = open(full, encoding="utf-8").read().split("\n")
    if start or end:
        lines = lines[(start or 1) - 1:end]
    if maxlines:
        lines = lines[:maxlines]
    return f'<div class="codehead">{esc(title)}</div><pre class="code">{esc(chr(10).join(lines))}</pre>'


def md(path, drop_ascii=True, skip_h1=True, cut_after=None, cut_before=None):
    text = open(os.path.join(ROOT, path), encoding="utf-8").read().replace(">= ", "&ge; ")
    if skip_h1:
        text = re.sub(r"^# .*\n", "", text, count=1)
        text = re.sub(r"^\*\*(Project|Student)[^\n]*\n", "", text, flags=re.M)
    if drop_ascii:
        text = re.sub(r"```\n[^`]*?[│►┬▲┴┌└─├]+[^`]*?```\n?", "", text)
    if cut_before and cut_before in text:
        text = text[text.index(cut_before):]
    if cut_after and cut_after in text:
        text = text[:text.index(cut_after)]
    text = re.sub(r"^## ", "#### ", text, flags=re.M)
    return markdown.markdown(text, extensions=["tables", "fenced_code"])


def checklist(rows):
    body = "".join(f"<tr><td>{esc(a)}</td><td>{b}</td></tr>" for a, b in rows)
    return ('<table class="check"><tr><th>Deliverable required by the sheet</th><th>Shown in this report</th></tr>'
            + body + "</table>")


def step(num, title, task, deliverable, intro, deliverables_rows, evidence):
    return f"""
<section class="step">
<div class="stephead"><span class="num">STEP {num}</span><h2>{esc(title)}</h2></div>
<div class="task"><b>Task given:</b> {esc(task)}</div>
<div class="deliv"><b>Deliverable required:</b> {esc(deliverable)}</div>
<p>{intro}</p>
{checklist(deliverables_rows)}
{evidence}
</section>"""


def load_sheet():
    ws = openpyxl.load_workbook(SHEET)["BE CMPN C"]
    out = []
    for c in COLS:
        raw = ws[f"{c}7"].value
        head, _, rest = raw.partition("\nDeliverable:")
        title, _, task = head.partition(":")
        out.append((title.strip(), task.strip(), rest.strip()))
    return out


def h(text):
    return f"<h3>{esc(text)}</h3>"


# ----------------------------------------------------------------------------- report body
def build():
    S = load_sheet()
    parts = []

    # ---- step 1
    parts.append(step(
        1, S[0][0], S[0][1], S[0][2],
        "Document written for the Device Compliance Management Portal: problem, users, objectives, constraints and the frozen 15-task MVP. "
        "Source: <code>docs/01-problem-definition-and-scope.md</code> in the repository.",
        [("Problem statement", "Section 1 below"), ("Stakeholder list", "Section 2 table"),
         ("Objectives", "Section 4"), ("Constraints", "Section 5 (and success criteria, section 6)"),
         ("Approved MVP scope", "Section 7 - 15 tasks, out-of-scope list")],
        md("docs/01-problem-definition-and-scope.md").replace("(pending sign-off)", "(see sign-off box below)")
        + '<table class="check"><tr><th colspan="3">Approval of the frozen 15-task MVP scope</th></tr>'
          '<tr><td style="height:46px">Course teacher (name / signature)</td><td>&nbsp;</td><td>Date: &nbsp; ____ / ____ / ______</td></tr></table>'
          '<p style="font-size:9pt">The sheet asks for an <i>approved</i> MVP scope; approval can only be given by the course teacher, so this box is left for sign-off.</p>'))

    # ---- step 2
    parts.append(step(
        2, S[1][0], S[1][1], S[1][2],
        "Agile artefacts for the portal. The Kanban board and backlog are maintained as tables in the repository "
        "(<code>docs/02-agile-planning-and-devops-workflow.md</code>); the final state of the backlog is in step 6.",
        [("Backlog", "10 user stories with acceptance criteria + prioritised 15-task backlog"),
         ("Task board", "Figures 2.2-2.3: Kanban board at sprint-1 start and at the end of sprint 3"),
         ("Sprint plan", "3 sprints with goals"), ("Definition of Done", "Section 5"),
         ("DevOps workflow diagram", "Figure: DevOps lifecycle")],
        md("docs/02-agile-planning-and-devops-workflow.md", cut_after="## 6. DevOps")
        + img("diagram_lifecycle", "Figure 2.1 - DevOps lifecycle from development to operations (as implemented in this project)")
        + img("diagram_kanban_start", "Figure 2.2 - Kanban board at the start of sprint 1 (task states from the plan; WIP limit: In Progress <= 2)")
        + img("diagram_kanban_end", "Figure 2.3 - Kanban board at the end of sprint 3: all 15 MVP tasks in Done (delivery evidence: step 6)")))

    # ---- step 3
    parts.append(step(
        3, S[2][0], S[2][1], S[2][2],
        "Architecture and technology choices, plus a working local setup (build, tests, run). "
        "Source: <code>docs/03-requirements-architecture-setup.md</code>.",
        [("SRS summary", "Section 1"), ("Use-case diagram", "Figure 3.1"), ("Architecture diagram", "Figure 3.2"),
         ("Data model / API list", "Sections 5 and 6"),
         ("Working local setup", "Figures 3.3-3.4: build output and running application")],
        md("docs/03-requirements-architecture-setup.md", cut_before="## 1. SRS", cut_after="## 3. Use-Case")
        + img("diagram_usecase", "Figure 3.1 - Use-case diagram")
        + img("diagram_architecture", "Figure 3.2 - Architecture diagram")
        + md("docs/03-requirements-architecture-setup.md", cut_before="## 5. Data Model", cut_after="## 7. Local")
        + term("s03_local_build", "Figure 3.3 - Local setup: JDK, Maven, `mvn clean package` (11 tests pass, WAR produced)")
        + img("app_01_home_tomcat", "Figure 3.4 - Application running (home page) and health endpoint below", "70%")
        + img("app_02_health_tomcat", "Figure 3.5 - /actuator/health returns UP", "55%")))

    # ---- step 4
    parts.append(step(
        4, S[3][0], S[3][1], S[3][2],
        "Public repository: <a href='https://github.com/Athdam05/device-compliance-portal'>github.com/Athdam05/device-compliance-portal</a>.",
        [("Repository URL", "above and Figure 4.1"), ("README", "Figure 4.2 and text below"),
         ("Initial commits", "Figures 4.3-4.4"), ("Issues", "Figures 4.5-4.6 (issue templates and created issues)"),
         ("Branch policy", "README section below, Figure 4.7 (branches)")],
        img("gh_repo_home", "Figure 4.1 - GitHub repository (files, branches, README)")
        + img("gh_readme", "Figure 4.2 - README rendered on GitHub")
        + term("s04_initial_commits", "Figure 4.3 - Initial commits with meaningful messages")
        + img("gh_commits_main", "Figure 4.4 - Commit history on GitHub")
        + h("Issue templates (.github/ISSUE_TEMPLATE)")
        + code(".github/ISSUE_TEMPLATE/feature_request.md", "feature_request.md")
        + code(".github/ISSUE_TEMPLATE/bug_report.md", "bug_report.md")
        + img("gh_issues", "Figure 4.5 - Issues created from the user stories")
        + img("gh_issue_detail", "Figure 4.6 - Example issue with acceptance criteria")
        + h("Branch naming and policy (from README)")
        + md("README.md", skip_h1=True, cut_before="## Branch policy", cut_after="## Documentation")
        + term("s04_branches_tags", "Figure 4.7 - Branches and tag in the repository")))

    # ---- step 5
    parts.append(step(
        5, S[4][0], S[4][1], S[4][2],
        "Feature 1 (Device entity, create, list and details) was built on branch <code>feature/1-device-create-list-view</code>, "
        "reviewed and merged through pull requests.",
        [("Working feature 1", "Figures 5.1-5.4 (screens of the running feature)"),
         ("Feature branch", "Figure 5.5 (git log / branch), 4 commits"),
         ("Pull request", "Figures 5.6-5.7 (PR #1 into develop/main, PR #2)"),
         ("Review comments", "Figure 5.8"), ("Merge evidence", "Figures 5.6-5.7 (Merged badge, merge commit)")],
        img("app_06_create_form", "Figure 5.1 - Create device form", "75%")
        + img("app_07_validation_errors", "Figure 5.2 - Validation errors on an empty form", "75%")
        + img("app_09_devices_list", "Figure 5.3 - Device list (4 devices; compliance computed from the 3 controls)", "75%")
        + img("app_08_device_details", "Figure 5.4 - Device details page", "75%")
        + term("s05_feature_git", "Figure 5.5 - Feature branch commits, pull/merge activity and remote")
        + img("gh_pr1", "Figure 5.6 - Pull request #1 (feature branch) - merged")
        + img("gh_pr2", "Figure 5.7 - Pull request #2 into develop - merged")
        + img("gh_pr1_review", "Figure 5.8 - Review comment on the feature-1 pull request")))

    # ---- step 6
    parts.append(step(
        6, S[5][0], S[5][1], S[5][2],
        "Remaining MVP functions were built on two further branches: <code>feature/2-update-search-dashboard</code> and "
        "<code>feature/3-roles-workflow</code>. A real merge conflict between them was created and resolved, "
        "and release <b>v1.0.0</b> was tagged.",
        [("Functional MVP", "Figures 6.1-6.8 (update, search, roles, workflow, history, dashboard)"),
         ("Second feature branch", "Figure 6.9 (PR #3 and PR #4)"),
         ("Resolved merge conflict", "Figures 6.10-6.11 (git log, resolution commit, PR #4)"),
         ("Tagged version", "Figures 6.12-6.13 (tag v1.0.0, release PR #5)"),
         ("Updated backlog", "Table below (docs/06)")],
        img("app_12_edit_form", "Figure 6.1 - Update device (edit form)", "70%")
        + img("app_10_search_lab", "Figure 6.2 - Search for 'lab' (name/owner/status filter)", "70%")
        + img("app_03_login", "Figure 6.3 - Login page (roles ADMIN / AUDITOR / TECHNICIAN)", "60%")
        + img("app_11_details_admin_view", "Figure 6.4 - Admin view of a device before any workflow action", "70%")
        + img("app_13_technician_moved_under_review", "Figure 6.5 - Technician moves REPORTED -> UNDER_REVIEW", "70%")
        + img("app_14_technician_remediated_history", "Figure 6.6 - Technician moves to REMEDIATED; history is recorded", "70%")
        + img("app_15_auditor_can_close", "Figure 6.7 - Auditor sees the only allowed action: close", "70%")
        + img("app_17_dashboard", "Figure 6.8 - Summary dashboard", "70%")
        + img("gh_pr3", "Figure 6.9a - PR #3 (feature/2) merged into develop")
        + img("gh_pr4", "Figure 6.9b - PR #4 (feature/3) merged after conflict resolution")
        + term("s06_conflict_merge", "Figure 6.10 - Merge history and the conflict-resolution commit bb8f57f")
        + h("The conflict")
        + "<p>Both branches edited the header line of <code>src/main/resources/templates/devices/list.html</code> "
          "(feature/2 added the Dashboard link and search form; feature/3 added the logged-in user and Logout). "
          "Merging <code>origin/develop</code> into feature/3 reported <code>CONFLICT (content): Merge conflict in "
          "src/main/resources/templates/devices/list.html</code>; the resolution kept both changes and the feature/2 tests were updated "
          "to log in. 11 tests passed afterwards.</p>"
        + img("gh_commit_conflict", "Figure 6.11 - Resolution commit on GitHub")
        + img("gh_tags", "Figure 6.12 - Tag v1.0.0")
        + img("gh_pr5", "Figure 6.13 - Release PR #5 into main")
        + h("Updated backlog (end of sprint 3)")
        + md("docs/06-mvp-completion-and-git-collaboration.md", cut_before="## 1. Updated Backlog", cut_after="## 3. Git collaboration")))

    # ---- step 7
    parts.append(step(
        7, S[6][0], S[6][1], S[6][2],
        "Jenkins 2.580 (LTS) runs from the WAR on port 9090 using JDK 21; the project itself is built with JDK 11 and Maven 3.9.9. "
        "Freestyle job <code>dcmp-ci</code> polls the repository (<code>H/2 * * * *</code>) and builds on every change.",
        [("Jenkins installed and configured", "Figure 7.0 (JDK, WAR, start command, plugins, tools, job settings) and Figure 7.1"),
         ("Configured Jenkins job", "Figures 7.1-7.2"), ("Successful build log", "Figures 7.3-7.4"),
         ("Trigger evidence", "Figure 7.5: 'Started by an SCM change' + polling log"),
         ("Archived artefact", "Figure 7.6")],
        term("s07_install", "Figure 7.0 - Jenkins installation and configuration: JDK 21, jenkins.war, start command, plugins, tools, dcmp-ci settings")
        + img("jk_dashboard", "Figure 7.1 - Jenkins dashboard with the jobs")
        + img("jk_ci_job", "Figure 7.2 - Job dcmp-ci: status, last build, archived WAR, test result trend")
        + img("jk_ci_console", "Figure 7.3 - Console output of a successful build")
        + term("s07_jenkins_ci", "Figure 7.4 - Build log excerpt: SCM trigger, Git checkout, 11 tests, BUILD SUCCESS, archiving")
        + term("s07_polling", "Figure 7.5 - Git polling log (trigger evidence)")
        + img("jk_ci_artifacts", "Figure 7.6 - Archived build artefact (WAR)")
        + h("Job configuration (config.xml excerpt)")
        + '<pre class="code">Source: https://github.com/Athdam05/device-compliance-portal.git   branch: */develop\n'
          'Trigger: Poll SCM  H/2 * * * *\n'
          'Build step: set JAVA_HOME=JDK 11; mvn -B clean package\n'
          'Post-build: archive target/*.war ; publish JUnit results target/surefire-reports/*.xml</pre>'))

    # ---- step 8
    parts.append(step(
        8, S[7][0], S[7][1], S[7][2],
        "<code>Jenkinsfile</code> in the repository root defines the pipeline. Apache Tomcat 9.0.98 (port 8081) is the deployment target. "
        "The environment is parameterised: Jenkins parameter <code>DEPLOY_ENV</code> (dev / qa) selects the Spring profile "
        "(<code>application-dev.properties</code>, <code>application-qa.properties</code>), and <code>APP_CONTEXT</code> sets the context path.",
        [("Jenkinsfile", "Listing below (current version; stages Checkout, Build, Package, Deploy, Verify)"),
         ("Successful pipeline run", "Figures 8.1-8.2"),
         ("Deployed application URL/screenshot", "Figures 8.3-8.4 (and Tomcat evidence, Figure 8.6)"),
         ("Configuration evidence (parameter)", "Figure 8.5 and the application-dev.properties listing; Tomcat setenv.bat in Figure 8.6")],
        code("Jenkinsfile", "Jenkinsfile (repository root)")
        + img("jk_pipe_overview", "Figure 8.1 - Job page of dcmp-pipeline: last successful build, archived WAR, test result trend")
        + term("s08_pipeline_run", "Figure 8.2 - Console excerpt of pipeline build #1: all stages passed, deployed to Tomcat")
        + img("app_01_home_tomcat", "Figure 8.3 - Deployed application at http://localhost:8081/dcmp/ (Environment = DEV)", "70%")
        + img("app_02_health_tomcat", "Figure 8.4 - Health check of the Tomcat deployment", "55%")
        + img("jk_pipe_params", "Figure 8.5 - Parameters used by a pipeline run (DEPLOY_ENV = dev, APP_CONTEXT = dcmp) - the parameterised environment setting")
        + term("s08_tomcat_config", "Figure 8.6 - Tomcat 9 target: port 8081, setenv.bat written by the pipeline from DEPLOY_ENV, deployed dcmp.war, live check")
        + code("src/main/resources/application-dev.properties", "application-dev.properties  (qa profile sets app.environment=QA)")))

    # ---- step 9
    parts.append(step(
        9, S[8][0], S[8][1], S[8][2],
        "Five critical user journeys (six tests) are automated with Selenium WebDriver 4.21 in Microsoft Edge, run through Maven Failsafe "
        "(<code>mvn verify -Pselenium</code>). Detailed plan: <code>docs/09-selenium-test-plan.md</code>.",
        [("Test plan", "Tables below"), ("Selenium scripts", "Listings below"),
         ("Local test report", "Figure 9.1"), ("Failure screenshot mechanism", "Listing + Figure 9.2 (real failure screenshot)")],
        md("docs/09-selenium-test-plan.md", cut_before="## 1. Critical", cut_after="## 5. How to run")
        + code("src/test/java/com/dcmp/portal/selenium/UserJourneysIT.java", "UserJourneysIT.java - the test cases")
        + code("src/test/java/com/dcmp/portal/selenium/BaseSeleniumIT.java", "BaseSeleniumIT.java - browser setup, waits and failure screenshot", maxlines=75)
        + term("s09_selenium_local", "Figure 9.1 - Local execution through Maven: 6 tests, 0 failures, plus per-test results")
        + img("selenium_failure_j2", "Figure 9.2 - Screenshot saved automatically by the framework when a test failed (J2, during step 10)", "70%")))

    # ---- step 10
    parts.append(step(
        10, S[9][0], S[9][1], S[9][2],
        "The Selenium suite runs inside the pipeline between Package and Deploy: the build is started on port 8082 with a throw-away database, "
        "the tests run against it, results and failure screenshots are published, and a failure stops the pipeline so <b>Deploy is skipped</b>. "
        "A defect was introduced on purpose (compliance rule changed from AND to OR); it passes all unit tests, and only Selenium catches it.",
        [("Jenkins test report", "Figures 10.1, 10.4"), ("Failed pipeline evidence", "Figures 10.1b, 10.2, 10.3, 10.6"),
         ("Defect correction commit", "Figure 10.5 (diff of both commits)"), ("Successful rerun", "Figures 10.3 (log), 10.7-10.8 (build #4)")],
        img("jk_pipe_stageview", "Figure 10.1 - Stage view of all pipeline runs. #3 is the deliberate defect (fails at Selenium); #2 was an earlier unplanned failure from a flaky test wait that was fixed; #4 and later are green")
        + img("jk_pipe_b3_stages", "Figure 10.1b - Build #3 stages: red at Selenium Tests, Deploy and Verify skipped")
        + img("jk_pipe_b3_console", "Figure 10.2 - Console of failed build #3: the AssertionFailedError (expected NON_COMPLIANT but was COMPLIANT)")
        + term("s10_fail_then_fix", "Figure 10.3 - Failed build #3 and successful rerun #4 (log excerpts)")
        + img("jk_pipe_b3_tests", "Figure 10.4 - Jenkins test report of the failed build: 1 failure (j2_registerDeviceWithMissingControls...)")
        + term("s10_defect_diff", "Figure 10.5 - Defect commit 9cc7492 and the correction commit a1cfb33")
        + img("selenium_failure_j2", "Figure 10.6 - Failure screenshot archived by Jenkins for build #3", "70%")
        + img("jk_pipe_b4", "Figure 10.7 - Build #4 after the fix: all stages green, 6/6 Selenium tests passed")
        + img("jk_pipe_b4_status", "Figure 10.8 - Build #4 status page (commit a1cfb33, test result: no failures)")
        + md("docs/10-continuous-testing-in-jenkins.md", cut_before="## 3. Other findings", cut_after="## 4. Evidence")))

    # ---- step 11
    parts.append(step(
        11, S[10][0], S[10][1], S[10][2],
        "Multi-stage <code>Dockerfile</code> (Maven build stage, then Eclipse Temurin 11 JRE runtime stage, non-root user, health check). "
        "Image tagged <code>device-compliance-portal:1.0.0</code> and <code>:latest</code>.",
        [("Dockerfile", "Listing below"), ("Image details", "Figure 11.1"),
         ("Docker command log (run, port map, logs, stop/restart/remove)", "Figure 11.2"),
         ("Running container evidence", "Figures 11.3-11.4"), ("Documented lifecycle", "Table below")],
        code("Dockerfile", "Dockerfile")
        + term("s11_image_details", "Figure 11.1 - Image details (id, size, user, exposed port, layers)")
        + term("s11_lifecycle_log", "Figure 11.2 - Complete container lifecycle: run, health, inspect, logs, stop, start, restart, remove")
        + img("app_18_home_docker_container", "Figure 11.3 - Application served from the container (host port mapped to container 8080)", "70%")
        + img("app_19_health_docker_container", "Figure 11.4 - Container health endpoint", "55%")
        + md("docs/11-docker-image-and-container-lifecycle.md", cut_before="## 3. Container lifecycle", cut_after="## 4. Notes")))

    # ---- step 12
    parts.append(step(
        12, S[11][0], S[11][1], S[11][2],
        "Three Docker stages were added to the pipeline: <b>Docker Build</b> (tag 1.0.&lt;build number&gt;), <b>Docker Push</b> to a local registry "
        "(<code>registry:2</code> on localhost:5000) and <b>Docker Deploy</b> (stop old container, pull the new image back from the registry, run a fresh container on port 8092, health check). "
        "They run only after tests and Tomcat deployment passed.",
        [("Versioned image", "Figures 12.1-12.2 (tags 1.0.6, 1.0.7)"),
         ("Registry evidence", "Figure 12.2 (catalog and tag list from the registry API)"),
         ("End-to-end commit-to-container pipeline", "Figures 12.3-12.5 (build #7 was started by a Git commit, no manual click)")],
        code("Jenkinsfile", "Jenkinsfile - Docker stages", start=118, end=190)
        + term("s12_registry", "Figure 12.1/12.2 - Registry catalog, tags, running container and the git.commit label on the image")
        + term("s12_docker_cd", "Figure 12.3 - Build #6 (manual) and build #7 (automatic, started by commit 386d8d0): stages and image tags")
        + img("jk_pipe_stageview_docker", "Figure 12.4 - Build #7 stages including Docker Build / Push / Deploy")
        + img("jk_pipe_b7", "Figure 12.4b - Build #7 status page: 'Started by an SCM change' (automatic commit-to-container run)")
        + img("app_18_home_docker_container", "Figure 12.5 - Application running in the freshly deployed container", "70%")))

    # ---- step 13
    parts.append(step(
        13, S[12][0], S[12][1], S[12][2],
        "Ansible (ansible-core 2.17, run from a container) configures a fresh Ubuntu 22.04 node reached over SSH. "
        "Source: <code>docs/13-configuration-management.md</code>, folder <code>ansible/</code>.",
        [("Configuration specification", "Table below (packages, user, folders, files, ports, services)"),
         ("Ansible playbook + inventory", "Listings below"), ("First execution log", "Figure 13.1 and raw log in repo")],
        md("docs/13-configuration-management.md", cut_before="## 1. Configuration", cut_after="## 2. Files")
        + code("ansible/inventory/hosts.ini", "ansible/inventory/hosts.ini")
        + code("ansible/group_vars/all.yml", "ansible/group_vars/all.yml (variables)")
        + code("ansible/templates/dcmp.conf.j2", "ansible/templates/dcmp.conf.j2 (service definition)")
        + code("ansible/playbook.yml", "ansible/playbook.yml (current version, includes the step-14 rollback logic)")
        + img("diagram_ansible", "Figure 13.0 - Lab topology")
        + term("s13_first_run", "Figure 13.1 - First execution: ok=14 changed=8 failed=0")
        + term("s13_second_run", "Figure 13.2 - Second execution: changed=0")))

    # ---- step 14
    parts.append(step(
        14, S[13][0], S[13][1], S[13][2],
        "A brand-new node was provisioned, the playbook was re-run to prove idempotency, health was checked, and several recovery scenarios were exercised. "
        "A bug found during this step (rollback restored the code but left the failed release's label) was fixed and re-tested. "
        "Source: <code>docs/14-provisioning-and-reliability.md</code>.",
        [("Provisioned node", "Figures 14.1-14.2"), ("Idempotency evidence", "Figure 14.3 (changed=0)"),
         ("Health-check result", "Figures 14.2, 14.4, 14.7"),
         ("Rollback / recovery demonstration", "Figures 14.6-14.9 (14.5 and 14.10 show the node afterwards)")],
        term("s14_0_clean", "Figure 14.1 - Clean node before provisioning: no Java, no dcmp user, no /opt/dcmp")
        + term("s14_1-provision-1.0.6", "Figure 14.2 - Provisioning release 1.0.6: ok=17 changed=8 failed=0, health UP")
        + term("s14_2-idempotency-rerun", "Figure 14.3 - Re-run: ok=16 changed=0 (idempotent)")
        + term("s14_3-upgrade-1.0.7", "Figure 14.4 - Upgrade to release 1.0.7 (active release 1.0.6 -> 1.0.7), health UP")
        + img("app_20_home_ansible_node", "Figure 14.5 - Provisioned node: home page shows Release 1.0.7", "70%")
        + term("s14_4-bad-release-auto-rollback", "Figure 14.6 - Bad release 1.0.8: health check fails -> automatic rollback to 1.0.7")
        + term("s14_5-manual-rollback-1.0.6", "Figure 14.7 - Manual rollback to the earlier stable release 1.0.6")
        + term("s14_6_recovery", "Figure 14.8 - Process crash (kill -9) and node reboot: service recovers by itself")
        + term("s14_7-final-1.0.7", "Figure 14.9 - Final promotion of the latest stable release 1.0.7")
        + img("app_21_health_ansible_node", "Figure 14.10 - Health endpoint of the provisioned node (via published port 8093)", "55%")
        + md("docs/14-provisioning-and-reliability.md", cut_before="## 6. Problem found", cut_after="## 7. How it works")))

    return S, parts


CSS = """
@page { size: A4; margin: 14mm 12mm; }
body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 10.5pt; color: #111; line-height: 1.35; }
h1 { font-size: 26pt; margin: 0 0 6px; } h2 { font-size: 16pt; margin: 0; } h3 { font-size: 12pt; margin: 14px 0 4px; }
h4 { font-size: 11.5pt; margin: 12px 0 4px; border-bottom: 1px solid #ccc; padding-bottom: 2px; }
.cover { text-align: center; padding-top: 70mm; page-break-after: always; }
.cover .sub { font-size: 14pt; color: #333; margin: 6px 0; }
.stephead { background: #1f3a68; color: #fff; padding: 8px 12px; border-radius: 6px; margin-top: 4px; }
.stephead .num { font-size: 9pt; letter-spacing: 1px; opacity: .85; }
section.step { page-break-before: always; }
.task, .deliv { background: #f4f6fa; border-left: 4px solid #3b6fd4; padding: 6px 10px; margin: 8px 0; font-size: 9.5pt; }
.deliv { border-left-color: #2e9b4e; background: #f1f9f3; }
table { border-collapse: collapse; width: 100%; margin: 6px 0; font-size: 9pt; page-break-inside: auto; }
th, td { border: 1px solid #bbb; padding: 3px 6px; vertical-align: top; text-align: left; }
th { background: #eef1f6; } tr { page-break-inside: avoid; }
table.check th { background: #dff0e3; }
figure { margin: 10px 0; text-align: center; page-break-inside: avoid; } figure img { max-width: 100%; border: 1px solid #ccc; }
figcaption { font-size: 8.5pt; color: #333; margin-top: 3px; font-style: italic; }
pre.code { background: #f6f8fa; border: 1px solid #ddd; padding: 6px; font-size: 7pt; line-height: 1.25; white-space: pre-wrap; word-break: break-all; }
.codehead { font-size: 8.5pt; font-weight: 700; background: #e8ebf0; padding: 3px 6px; margin-top: 8px; border: 1px solid #ddd; border-bottom: 0; }
code { background: #f1f1f1; padding: 0 3px; font-size: 9pt; }
.pending { border: 2px dashed #d33; color: #b00; padding: 12px; margin: 8px 0; font-weight: 700; }
ul { margin: 4px 0 4px 18px; padding: 0; } p { margin: 5px 0; }
.toc td, .toc th { font-size: 9.5pt; }
"""


def main():
    S, parts = build()
    toc = "".join(
        f"<tr><td>{i}</td><td>{esc(S[i-1][0])}</td></tr>" for i in range(1, 15))
    cover = f"""
<div class="cover">
<h1>Automated Device Compliance Management Portal</h1>
<div class="sub">DevOps Mini Project - Step-by-step Deliverables and Outputs</div>
<div class="sub" style="margin-top:30px"><b>Atharva Anand Damale</b> &nbsp;|&nbsp; Roll/ID 23102C0004</div>
<div class="sub">Department of Computer Engineering - BE CMPN C</div>
<div class="sub">Academic Year 2026-27 (ODD Semester)</div>
<div class="sub" style="margin-top:30px">Repository: github.com/Athdam05/device-compliance-portal</div>
</div>
<section><h2>How to read this report</h2>
<p>The report follows the 14 steps given on the course sheet. Each step starts with the task and the deliverable exactly as given,
then a checklist that points to where every deliverable is shown, followed by the evidence: screenshots of the running application,
Jenkins and GitHub, rendered command/log output, code listings and tables. Terminal and log figures are rendered from the real command output and Jenkins/Ansible logs saved during the work;
long logs are shown as excerpts (lines were selected, never altered). The complete source, scripts and raw logs are in the repository.</p>
<table class="toc"><tr><th>Step</th><th>Title</th></tr>{toc}</table>
<h4>Technology used</h4>
<p>Java 11, Spring Boot 2.7, Thymeleaf, H2 | Maven 3.9.9 | Git/GitHub | Jenkins 2.580 (JDK 21) | Apache Tomcat 9.0.98 |
Selenium 4.21 + Microsoft Edge 155 | Docker 29 + local registry (registry:2) | Ansible core 2.17 (control node in a container), Ubuntu 22.04 managed node.</p>
</section>"""
    body = cover + "".join(parts)
    page = f"<!doctype html><html><head><meta charset='utf-8'><title>DevOps Mini Project Report</title><style>{CSS}</style></head><body>{body}</body></html>"
    out_html = os.path.join(HERE, "DCMP_DevOps_Report.html")
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(page)
    print("HTML written:", out_html)
    if PENDING:
        print("PENDING images (%d):" % len(PENDING), ", ".join(sorted(set(PENDING))))
    else:
        print("all images present")


if __name__ == "__main__":
    main()
