"""HTML -> PDF with headless Edge (Chromium print engine)."""
import base64
import os
import sys

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.print_page_options import PrintOptions

HERE = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(HERE, "DCMP_DevOps_Report.html")
out = os.path.join(HERE, "DCMP_DevOps_Report.pdf")
opts = Options()
opts.add_argument("--headless=new")
opts.add_argument("--remote-allow-origins=*")
d = webdriver.Edge(service=Service(r"C:\Users\damal\tools\edgedriver\msedgedriver.exe"), options=opts)
d.set_page_load_timeout(180)
try:
    d.get("file:///" + src.replace("\\", "/"))
    po = PrintOptions()
    po.page_width, po.page_height = 21.0, 29.7
    po.margin_top = po.margin_bottom = 1.2
    po.margin_left = po.margin_right = 1.1
    po.background = True
    po.shrink_to_fit = True
    pdf = d.print_page(po)
    with open(out, "wb") as f:
        f.write(base64.b64decode(pdf))
    print("PDF written", os.path.getsize(out) // 1024, "KB")
finally:
    d.quit()
