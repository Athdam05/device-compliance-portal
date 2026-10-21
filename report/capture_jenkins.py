"""Full-resolution screenshots of Jenkins pages (headless Edge) - used while Jenkins allows anonymous read access.
mode: full (whole page, capped), top (first viewport), bottom (last viewport),
      find:<text> (plain-text log: scroll so the first line containing <text> is near the top)."""
import os
import sys
import time

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shots")
DRIVER = r"C:\Users\damal\tools\edgedriver\msedgedriver.exe"
J = "http://localhost:9090"

PAGES = [
    ("jk_dashboard", "/", "top", 5),
    ("jk_ci_job", "/job/dcmp-ci/", "full", 6),
    ("jk_ci_artifacts", "/job/dcmp-ci/1/", "full", 4),
    ("jk_ci_console", "/job/dcmp-ci/1/console", "bottom", 5),
    ("jk_pipe_overview", "/job/dcmp-pipeline/", "full", 6),
    ("jk_pipe_params", "/job/dcmp-pipeline/4/parameters/", "full", 4),
    ("jk_pipe_stageview", "/job/dcmp-pipeline/multi-pipeline-graph", "full", 8),
    ("jk_pipe_b3_stages", "/job/dcmp-pipeline/3/stages", "full", 8),
    ("jk_pipe_b3_console", "/job/dcmp-pipeline/3/consoleText", "find:AssertionFailedError", 4),
    ("jk_pipe_b3_tests", "/job/dcmp-pipeline/3/testReport/", "full", 5),
    ("jk_pipe_b4", "/job/dcmp-pipeline/4/stages", "full", 8),
    ("jk_pipe_b4_status", "/job/dcmp-pipeline/4/", "full", 4),
    ("jk_pipe_b7", "/job/dcmp-pipeline/7/", "full", 4),
    ("jk_pipe_stageview_docker", "/job/dcmp-pipeline/7/stages", "full", 8),
]


def main(only):
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1300,900")
    opts.add_argument("--remote-allow-origins=*")
    opts.add_argument("--hide-scrollbars")
    d = webdriver.Edge(service=Service(DRIVER), options=opts)
    d.set_page_load_timeout(60)
    try:
        for name, path, mode, wait in PAGES:
            if only and name not in only:
                continue
            d.set_window_size(1300, 900)
            d.get(J + path)
            time.sleep(wait)
            if mode == "full":
                h = d.execute_script("return Math.min(document.documentElement.scrollHeight, 1800)")
                d.set_window_size(1300, max(h + 20, 600))
                time.sleep(1)
            elif mode.startswith("find:"):
                lines = d.execute_script("return document.body.innerText").split("\n")
                idx = next((i for i, l in enumerate(lines) if mode[5:] in l), 0)
                total = d.execute_script("return document.documentElement.scrollHeight")
                line_h = total / max(len(lines), 1)
                d.execute_script("window.scrollTo(0, arguments[0])", max(0, idx * line_h - 150))
                print("  line", idx, "of", len(lines))
                time.sleep(1)
            elif mode == "bottom":
                d.execute_script("window.scrollTo(0, document.documentElement.scrollHeight)")
                time.sleep(1.5)
            d.save_screenshot(os.path.join(OUT, name + ".png"))
            print("saved", name)
    finally:
        d.quit()


if __name__ == "__main__":
    main(set(sys.argv[1:]))
