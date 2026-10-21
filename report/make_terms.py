"""Renders captured command output / log text files (report/txt/*.txt) as terminal-style PNG images.
The text is the real output saved from the commands and Jenkins/Ansible logs; nothing is rewritten."""
import glob
import os
import re

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "txt")
OUT = os.path.join(HERE, "shots")
FONT = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 17)
BOLD = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", 17)
BG, FG, BAR = (30, 30, 30), (220, 220, 220), (60, 60, 60)
GREEN, RED, YELLOW, BLUE, GREY = (110, 220, 120), (255, 110, 110), (240, 210, 90), (120, 180, 255), (150, 150, 150)
LINE_H, PAD, WIDTH_CH, PAGE_LINES = 24, 18, 118, 46

TITLES = {
    "s03_local_build": "Windows PowerShell / Git Bash - local build and tests",
    "s04_branches_tags": "Git Bash - branches and tags",
    "s04_initial_commits": "Git Bash - initial commits",
    "s05_feature_git": "Git Bash - feature branch commits, pull/merge activity, remote",
    "s10_defect_diff": "Git Bash - the deliberate defect and its correction",
    "s06_conflict_merge": "Git Bash - merge history and conflict-resolution commit",
    "s07_install": "Jenkins - installation and configuration facts (from the machine)",
    "s08_tomcat_config": "Tomcat - deployment target and configuration written by the pipeline",
    "s07_jenkins_ci": "Jenkins - job dcmp-ci console / artefact (from build log)",
    "s07_polling": "Jenkins - dcmp-ci Git polling log",
    "s08_pipeline_run": "Jenkins - dcmp-pipeline build #1 (console log excerpt)",
    "s09_selenium_local": "Maven - Selenium suite run locally",
    "s10_fail_then_fix": "Jenkins - dcmp-pipeline: failed build #3, fixed build #4",
    "s11_image_details": "Docker - image details",
    "s11_lifecycle_log": "Docker - container lifecycle command log",
    "s12_docker_cd": "Jenkins - dcmp-pipeline Docker CD builds",
    "s12_registry": "Docker - registry and running container",
    "s13_first_run": "Ansible - first execution (step 13)",
    "s13_second_run": "Ansible - second execution (idempotency preview)",
    "s14_0_clean": "Docker / shell - clean managed node before provisioning",
    "s14_1-provision-1.0.6": "Ansible - provision clean node with release 1.0.6",
    "s14_2-idempotency-rerun": "Ansible - re-run on configured node (idempotency)",
    "s14_3-upgrade-1.0.7": "Ansible - upgrade to release 1.0.7",
    "s14_4-bad-release-auto-rollback": "Ansible - bad release 1.0.8 -> automatic rollback",
    "s14_5-manual-rollback-1.0.6": "Ansible - manual rollback to 1.0.6",
    "s14_6_recovery": "Docker - crash and reboot recovery",
    "s14_7-final-1.0.7": "Ansible - promote latest stable release 1.0.7",
}


def colour(line):
    s = line.strip()
    if re.search(r"fatal:|FAILED|FAILURE|ERROR\]|AssertionFailed|Failures: [1-9]|failed=[1-9]|Exited \(143\)|skipped due to|ROLLBACK", s):
        return RED
    if re.search(r"^changed:|changed=[1-9]|^\$ |^== ", s):
        return YELLOW if s.startswith("changed") or "changed=" in s else BLUE
    if re.search(r"SUCCESS|BUILD SUCCESS|\"status\":\"UP\"|\bUP\b|healthy|^ok:|Failures: 0|PASS|changed=0|failed=0|pong|rolled back", s):
        return GREEN
    if s.startswith("TASK") or s.startswith("PLAY"):
        return GREY
    return FG


def wrap(line):
    line = line.expandtabs(4)
    if len(line) <= WIDTH_CH:
        return [line]
    return [line[i:i + WIDTH_CH] for i in range(0, len(line), WIDTH_CH)]


def render(name, lines, title, page=None, pages=None):
    rows = []
    for l in lines:
        for w in wrap(l.rstrip("\n")):
            rows.append((w, colour(l)))
    w = PAD * 2 + int(FONT.getlength("M") * WIDTH_CH)
    h = 38 + PAD * 2 + LINE_H * max(len(rows), 1)
    img = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w, 32], fill=BAR)
    for i, c in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))):
        d.ellipse([12 + i * 22, 9, 24 + i * 22, 21], fill=c)
    cap = title + (f"   [{page}/{pages}]" if pages and pages > 1 else "")
    d.text((90, 6), cap, font=BOLD, fill=(235, 235, 235))
    y = 38 + PAD
    for text, col in rows:
        d.text((PAD, y), text, font=FONT, fill=col)
        y += LINE_H
    suffix = f"_p{page}" if pages and pages > 1 else ""
    path = os.path.join(OUT, f"term_{name}{suffix}.png")
    img.save(path)
    return path


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in sorted(glob.glob(os.path.join(SRC, "*.txt"))):
        name = os.path.splitext(os.path.basename(f))[0]
        lines = open(f, encoding="utf-8", errors="replace").read().split("\n")
        while lines and not lines[-1].strip():
            lines.pop()
        chunks = [lines[i:i + PAGE_LINES] for i in range(0, len(lines), PAGE_LINES)] or [[""]]
        for n, chunk in enumerate(chunks, 1):
            p = render(name, chunk, TITLES.get(name, name), n, len(chunks))
            print("saved", os.path.basename(p))


if __name__ == "__main__":
    main()
