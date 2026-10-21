"""Draws the report diagrams as SVG pages (report/diagrams/*.html) and renders them to PNG with headless Edge."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "diagrams")
os.makedirs(BASE, exist_ok=True)

CSS = """<style>body{margin:0;background:#fff;font-family:Segoe UI,Arial,sans-serif}
.box{fill:#eaf2ff;stroke:#3b6fd4;stroke-width:2}.green{fill:#e6f6ea;stroke:#2e9b4e;stroke-width:2}.orange{fill:#fff1e0;stroke:#d9822b;stroke-width:2}
.grey{fill:#f2f2f2;stroke:#777;stroke-width:2}.t{font-size:15px;fill:#111;text-anchor:middle}.s{font-size:12px;fill:#444;text-anchor:middle}
.h{font-size:20px;font-weight:700;fill:#111}.a{stroke:#555;stroke-width:2;fill:none;marker-end:url(#ar)}</style>
<defs><marker id="ar" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 z" fill="#555"/></marker></defs>"""


def page(name, w, h, body):
    html = ('<!doctype html><html><head><meta charset="utf-8">%s</head><body>'
            '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">%s</svg></body></html>'
            % (CSS, w, h, w, h, body))
    with open(os.path.join(BASE, name + ".html"), "w", encoding="utf-8") as f:
        f.write(html)


def node(x, y, w, h, title, sub="", cls="box"):
    s = '<rect class="%s" x="%s" y="%s" width="%s" height="%s" rx="10"/>' % (cls, x, y, w, h)
    s += '<text class="t" x="%s" y="%s">%s</text>' % (x + w / 2, y + h / 2 - (4 if sub else -5), title)
    if sub:
        s += '<text class="s" x="%s" y="%s">%s</text>' % (x + w / 2, y + h / 2 + 16, sub)
    return s


def arrow(x1, y1, x2, y2):
    return '<path class="a" d="M%s,%s L%s,%s"/>' % (x1, y1, x2, y2)


def lifecycle():
    b = '<text class="h" x="20" y="32">DevOps lifecycle - Device Compliance Management Portal</text>'
    stages = [("PLAN", "GitHub Issues / Kanban"), ("CODE", "Git branches + PRs"), ("BUILD", "Maven (Jenkins)"),
              ("TEST", "JUnit + Selenium"), ("RELEASE", "Git tag, Docker image"), ("DEPLOY", "Tomcat / Docker"),
              ("OPERATE", "Ansible playbook"), ("MONITOR", "/actuator/health")]
    for i, (t, s) in enumerate(stages):
        x = 20 + i * 148
        b += node(x, 70, 128, 70, t, s, "box" if i < 4 else "green")
        if i < 7:
            b += arrow(x + 128, 105, x + 148, 105)
    b += '<path class="a" d="M1140,140 L1140,200 L84,200 L84,142" stroke-dasharray="6 5"/>'
    b += '<text class="s" x="610" y="222">feedback: failed tests, health alerts and new requirements go back to the backlog</text>'
    b += node(20, 255, 1170, 70, "Pipeline: commit - GitHub - Jenkins (checkout, build, unit tests, Selenium, package) - Docker image - registry - container / Tomcat - health check - rollback on failure", "", "grey")
    page("lifecycle", 1210, 350, b)


def actor(x, y, name):
    return ('<circle cx="%d" cy="%d" r="14" fill="#fff" stroke="#333" stroke-width="2"/>'
            '<path d="M%d,%d v36 M%d,%d h48 M%d,%d l-18,30 M%d,%d l18,30" stroke="#333" stroke-width="2" fill="none"/>'
            '<text class="t" x="%d" y="%d" style="font-weight:700">%s</text>'
            % (x, y, x, y + 14, x - 24, y + 28, x, y + 50, x, y + 50, x, y + 100, name))


def usecase():
    b = '<text class="h" x="20" y="30">Use-case diagram</text>'
    b += '<rect x="300" y="45" width="520" height="440" rx="14" fill="#fafafa" stroke="#999" stroke-width="2"/>'
    b += '<text class="t" x="560" y="72" style="font-weight:700">Device Compliance Portal</text>'
    ucs = ["Login", "Register device", "View / search devices", "Update device", "Evaluate compliance",
           "Move status (role-based)", "View status history", "View dashboard"]
    ys = [110 + i * 45 for i in range(8)]
    for t, y in zip(ucs, ys):
        b += ('<ellipse cx="560" cy="%d" rx="130" ry="18" fill="#eaf2ff" stroke="#3b6fd4" stroke-width="1.8"/>'
              '<text class="t" x="560" y="%d" style="font-size:14px">%s</text>' % (y, y + 5, t))
    b += actor(120, 130, "Admin") + actor(120, 300, "Technician") + actor(1000, 210, "Auditor")
    for y in ys:
        b += '<path d="M150,160 L430,%d" stroke="#bbb" stroke-width="1.2" fill="none"/>' % y
    for y in (ys[0], ys[2], ys[3], ys[5], ys[6]):
        b += '<path d="M150,330 L430,%d" stroke="#d9822b" stroke-width="1.2" fill="none"/>' % y
    for y in (ys[0], ys[2], ys[5], ys[6], ys[7]):
        b += '<path d="M970,240 L690,%d" stroke="#2e9b4e" stroke-width="1.2" fill="none"/>' % y
    b += '<text class="s" x="20" y="440" style="text-anchor:start">Admin: all use cases</text>'
    b += '<text class="s" x="20" y="460" style="text-anchor:start">Technician: Reported - Under review - Remediated</text>'
    b += '<text class="s" x="20" y="480" style="text-anchor:start">Auditor: Remediated - Closed / reopen; dashboard</text>'
    page("usecase", 1180, 500, b)


def architecture():
    b = '<text class="h" x="20" y="30">Application architecture</text>'
    b += node(20, 80, 140, 80, "Browser", "HTML / Thymeleaf pages") + arrow(160, 120, 215, 120)
    b += node(215, 60, 190, 120, "Controllers", "Spring MVC") + arrow(405, 120, 460, 120)
    b += '<text class="s" x="310" y="150">Device / Login / Dashboard / Workflow</text>'
    b += node(460, 60, 190, 120, "Services", "compliance rule + workflow", "green") + arrow(650, 120, 705, 120)
    b += '<text class="s" x="555" y="150">role checks, history</text>'
    b += node(705, 60, 170, 120, "Repositories", "Spring Data JPA") + arrow(875, 120, 930, 120)
    b += node(930, 80, 150, 80, "H2 database", "Device, AppUser, StatusHistory", "orange")
    b += node(215, 230, 190, 60, "Auth interceptor", "session login, BCrypt", "grey") + arrow(310, 230, 310, 182)
    b += node(460, 230, 190, 60, "Actuator", "/actuator/health", "grey") + arrow(555, 230, 555, 182)
    b += node(20, 340, 1060, 70, "Packaged as one Spring Boot WAR: Tomcat 9 (WAR)  |  Docker image  |  Ansible-provisioned server", "", "green")
    page("architecture", 1100, 430, b)


def pipeline():
    b = '<text class="h" x="20" y="30">CI/CD pipeline implemented in Jenkins (Jenkinsfile)</text>'
    st = [("Checkout", "git clone"), ("Build", "mvn package + unit tests"), ("Package", "WAR archived"),
          ("Selenium", "6 browser tests :8082"), ("Deploy", "Tomcat :8081/dcmp"), ("Verify", "/actuator/health"),
          ("Docker Build", "dcmp:1.0.N"), ("Docker Push", "registry :5000"), ("Docker Deploy", "container :8092")]
    for i, (t, s) in enumerate(st):
        x = 15 + i * 128
        b += node(x, 70, 114, 80, t, s, "box" if i < 4 else ("green" if i < 6 else "orange"))
        if i < 8:
            b += arrow(x + 114, 110, x + 128, 110)
    b += '<text class="s" x="580" y="190">A failing stage stops the pipeline - later stages are skipped ("skipped due to earlier failure")</text>'
    b += node(15, 215, 1130, 50, "Triggers: SCM polling (H/2 * * * *)  or  Build with Parameters (DEPLOY_ENV, APP_CONTEXT)", "", "grey")
    page("pipeline", 1170, 290, b)


TASKS = {1: "Project skeleton", 2: "Device entity + repo", 3: "Create device form", 4: "List devices",
         5: "Device details", 6: "Update device", 7: "Search / filter", 8: "Compliance rules",
         9: "Roles + login", 10: "Status workflow", 11: "Status history", 12: "Dashboard",
         13: "Validation + errors", 14: "Health endpoint", 15: "README + docs"}


def board(title, y0, columns):
    """columns: list of (name, [task numbers]) - draws one Kanban board starting at vertical offset y0."""
    b = '<text class="h" x="20" y="%d">%s</text>' % (y0 + 6, title)
    colw = 224
    for ci, (name, ids) in enumerate(columns):
        x = 20 + ci * (colw + 8)
        h = 40 + max(len(ids), 1) * 30 + 14
        b += '<rect x="%d" y="%d" width="%d" height="%d" rx="8" fill="#f4f6fa" stroke="#9aa5b8" stroke-width="1.5"/>' % (x, y0 + 20, colw, h)
        b += '<text class="t" x="%d" y="%d" style="font-weight:700">%s (%d)</text>' % (x + colw / 2, y0 + 44, name, len(ids))
        for k, tid in enumerate(ids):
            fill = {"Done": "#e6f6ea", "In Progress": "#fff1e0", "Review": "#fff7d6"}.get(name, "#ffffff")
            yy = y0 + 56 + k * 30
            b += '<rect x="%d" y="%d" width="%d" height="24" rx="5" fill="%s" stroke="#7d8aa3"/>' % (x + 8, yy, colw - 16, fill)
            b += '<text class="s" x="%d" y="%d" style="text-anchor:start">#%d %s</text>' % (x + 14, yy + 16, tid, TASKS[tid])
    return b


def kanban():
    cols_start = [("Backlog", list(range(6, 16))), ("To Do", [2, 3, 4, 5]), ("In Progress", [1]), ("Review", []), ("Done", [])]
    cols_end = [("Backlog", []), ("To Do", []), ("In Progress", []), ("Review", []), ("Done", list(range(1, 16)))]
    page("kanban_start", 1200, 430, board("Kanban board - start of Sprint 1 (planning, step 2)", 24, cols_start))
    page("kanban_end", 1200, 600, board("Kanban board - end of Sprint 3 (all 15 MVP tasks done, step 6)", 24, cols_end))


def ansible():
    b = '<text class="h" x="20" y="30">Ansible provisioning lab (steps 13-14)</text>'
    # control node
    b += '<rect class="box" x="20" y="70" width="230" height="130" rx="10"/>'
    b += '<text class="t" x="135" y="98" style="font-weight:700">Control node</text>'
    b += '<text class="s" x="135" y="122">container dcmp-ansible</text>'
    b += '<text class="s" x="135" y="150">ansible-core 2.17</text>'
    b += '<text class="s" x="135" y="170">playbook.yml, rollback.yml</text>'
    b += '<path class="a" d="M250,135 L420,135"/><text class="s" x="335" y="122">SSH (key)</text>'
    # managed node
    b += '<rect class="green" x="420" y="60" width="330" height="260" rx="10"/>'
    b += '<text class="t" x="585" y="90" style="font-weight:700">Managed node: fresh Ubuntu 22.04</text>'
    b += '<text class="s" x="585" y="112">container dcmp-node</text>'
    for i, t in enumerate(["sshd + supervisord", "Java 11, user dcmp", "/opt/dcmp/releases/1.0.6, 1.0.7 ...",
                           "/opt/dcmp/current -> active release", "service dcmp on port 8080"]):
        b += '<text class="s" x="585" y="%d">%s</text>' % (150 + i * 28, t)
    b += arrow(750, 190, 830, 190) + '<rect class="orange" x="830" y="150" width="200" height="80" rx="10"/>'
    b += '<text class="t" x="930" y="183" style="font-weight:700">Health check</text><text class="s" x="930" y="205">GET /actuator/health = UP</text>'
    b += '<text class="s" x="585" y="350">failed health check: current -> previous release, restart, verify (automatic rollback)</text>'
    page("ansible", 1060, 370, b)


if __name__ == "__main__":
    kanban()
    lifecycle(); usecase(); architecture(); pipeline(); ansible()
    names = ["kanban_start", "kanban_end", "lifecycle", "usecase", "architecture", "pipeline", "ansible"]
    args = ["diagram_%s=file:///%s/%s.html" % (n, BASE.replace("\\", "/"), n) for n in names]
    subprocess.run([sys.executable, os.path.join(HERE, "capture_web.py")] + args, check=True)
    from PIL import Image, ImageChops
    for n in names:
        f = os.path.join(HERE, "shots", "diagram_%s.png" % n)
        im = Image.open(f).convert("RGB")
        bb = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
        if bb:
            l, t, r, b = bb
            im.crop((max(l - 15, 0), max(t - 15, 0), min(r + 15, im.width), min(b + 15, im.height))).save(f)
