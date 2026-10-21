"""docs/15-demo-guide.md -> report/DCMP_Demo_Guide.pdf (via headless Edge)."""
import base64
import os

import markdown
from selenium import webdriver
from selenium.webdriver.common.print_page_options import PrintOptions
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSS = """
body{font-family:'Segoe UI',Arial,sans-serif;font-size:10.5pt;line-height:1.38;color:#111}
h1{font-size:21pt;margin:0 0 4px;color:#1f3a68} h2{font-size:14pt;margin:18px 0 6px;padding:5px 9px;background:#1f3a68;color:#fff;border-radius:5px}
h2,h3{page-break-after:avoid} h3{font-size:11.5pt;margin:14px 0 4px;color:#1f3a68;border-bottom:1px solid #c9d2e3}
table{border-collapse:collapse;width:100%;margin:6px 0;font-size:9.5pt} th,td{border:1px solid #b9c2d3;padding:4px 7px;vertical-align:top;text-align:left}
th{background:#e8edf6} tr{page-break-inside:avoid}
pre{background:#f3f5f9;border:1px solid #d5dbe8;border-left:4px solid #3b6fd4;padding:7px 9px;font-size:9pt;white-space:pre-wrap;word-break:break-all;page-break-inside:avoid}
code{background:#eef1f6;padding:0 3px;font-size:9.2pt} pre code{background:none;padding:0}
blockquote{margin:8px 0;padding:6px 12px;background:#fff7e0;border-left:4px solid #e0a800;font-style:italic}
ul{margin:4px 0 4px 18px;padding:0} li{margin:2px 0}
"""
text = open(os.path.join(ROOT, "docs", "15-demo-guide.md"), encoding="utf-8").read()
body = markdown.markdown(text, extensions=["tables", "fenced_code"])
html = f"<!doctype html><html><head><meta charset='utf-8'><title>Demo Guide</title><style>{CSS}</style></head><body>{body}</body></html>"
src = os.path.join(HERE, "_guide.html")
open(src, "w", encoding="utf-8").write(html)

opts = Options()
opts.add_argument("--headless=new")
opts.add_argument("--remote-allow-origins=*")
d = webdriver.Edge(service=Service(r"C:\Users\damal\tools\edgedriver\msedgedriver.exe"), options=opts)
try:
    d.get("file:///" + src.replace("\\", "/"))
    po = PrintOptions()
    po.page_width, po.page_height = 21.0, 29.7
    po.margin_top = po.margin_bottom = 1.3
    po.margin_left = po.margin_right = 1.4
    po.background = True
    pdf = d.print_page(po)
    out = os.path.join(HERE, "DCMP_Demo_Guide.pdf")
    open(out, "wb").write(base64.b64decode(pdf))
    print("PDF written", os.path.getsize(out) // 1024, "KB")
finally:
    d.quit()
    os.remove(src)
