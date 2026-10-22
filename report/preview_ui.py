"""Captures every page of a running instance (default http://localhost:8082) into report/_ui for a visual review."""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import capture_app as ca  # noqa: E402
from selenium.webdriver.common.by import By  # noqa: E402

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8082"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_ui")
os.makedirs(OUT, exist_ok=True)
ca.OUT = OUT

d = ca.make_driver(1200, 800)
try:
    d.get(BASE + "/"); ca.shot(d, "ui_01_home")
    d.get(BASE + "/login"); ca.shot(d, "ui_02_login")
    d.find_element(By.ID, "username").send_keys("admin")
    d.find_element(By.ID, "password").send_keys("wrong")
    ca.click_wait(d, By.ID, "login"); ca.shot(d, "ui_03_login_error")
    ca.login(d, BASE, "admin", "admin123")
    stamp = str(int(time.time()))[-5:]
    for s in [("Lab-PC-01", "Asha Mehta", "UI-A" + stamp, "Windows 11", True, True, True),
              ("Lab-PC-02", "Ravi Kulkarni", "UI-B" + stamp, "Windows 10", True, False, False),
              ("Faculty-Laptop-07", "Prof. Sharma", "UI-C" + stamp, "Ubuntu 22.04", True, True, False)]:
        ca.add_device(d, BASE, *s)
    d.get(BASE + "/devices/new"); ca.shot(d, "ui_04_form")
    ca.click_wait(d, By.ID, "save"); ca.shot(d, "ui_05_form_errors")
    d.get(BASE + "/devices"); ca.shot(d, "ui_06_list")
    d.find_element(By.PARTIAL_LINK_TEXT, "Lab-PC-02").click(); ca.shot(d, "ui_07_details")
    url = d.current_url
    ca.logout(d, BASE)
    ca.login(d, BASE, "tech", "tech123")
    d.get(url); ca.click_wait(d, By.ID, "to-UNDER_REVIEW"); ca.click_wait(d, By.ID, "to-REMEDIATED"); ca.shot(d, "ui_08_details_remediated")
    ca.logout(d, BASE)
    ca.login(d, BASE, "auditor", "auditor123")
    d.get(url); ca.shot(d, "ui_09_auditor_options")
    d.get(BASE + "/dashboard"); ca.shot(d, "ui_10_dashboard")
    d.get(BASE + "/devices/99999"); ca.shot(d, "ui_11_error_404")
finally:
    d.quit()
