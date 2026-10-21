"""Captures real browser screenshots of the running Device Compliance Portal (Edge, via Selenium).
Only talks to the user's own local instances using the seeded demo accounts."""
import os
import sys
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shots")
DRIVER = r"C:\Users\damal\tools\edgedriver\msedgedriver.exe"
TOMCAT = "http://localhost:8081/dcmp"
DOCKER = "http://localhost:8092"
NODE = "http://localhost:8093"
MAIN = DOCKER  # clean database (fresh volume) -> uncluttered demo data


def make_driver(width=1100, height=720):
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument(f"--window-size={width},{height}")
    opts.add_argument("--remote-allow-origins=*")
    d = webdriver.Edge(service=Service(DRIVER), options=opts)
    d.implicitly_wait(10)
    return d


def shot(d, name):
    path = os.path.join(OUT, name + ".png")
    d.save_screenshot(path)
    print("saved", name)


def click_wait(d, by, value):
    el = d.find_element(by, value)
    el.click()
    WebDriverWait(d, 10).until(EC.staleness_of(el))


def login(d, base, user, pw):
    d.get(base + "/login")
    d.find_element(By.ID, "username").send_keys(user)
    d.find_element(By.ID, "password").send_keys(pw)
    click_wait(d, By.ID, "login")


def logout(d, base):
    d.get(base + "/devices")
    click_wait(d, By.ID, "logout")


def add_device(d, base, name, owner, serial, os_name, av, enc, fw):
    d.get(base + "/devices/new")
    d.find_element(By.ID, "name").send_keys(name)
    d.find_element(By.ID, "owner").send_keys(owner)
    d.find_element(By.ID, "serialNo").send_keys(serial)
    d.find_element(By.ID, "os").send_keys(os_name)
    for flag, cid in ((av, "antivirusEnabled1"), (enc, "diskEncrypted1"), (fw, "firewallEnabled1")):
        if flag:
            d.find_element(By.ID, cid).click()
    click_wait(d, By.ID, "save")


def main():
    os.makedirs(OUT, exist_ok=True)
    d = make_driver()
    try:
        # ---- step 3 / 8: deployed on Tomcat -------------------------------------------------
        d.get(TOMCAT + "/")
        shot(d, "app_01_home_tomcat")
        d.get(TOMCAT + "/actuator/health")
        shot(d, "app_02_health_tomcat")
        d.get(MAIN + "/login")
        shot(d, "app_03_login")
        # wrong password
        d.find_element(By.ID, "username").send_keys("admin")
        d.find_element(By.ID, "password").send_keys("wrong")
        click_wait(d, By.ID, "login")
        shot(d, "app_04_login_rejected")

        login(d, MAIN, "admin", "admin123")
        shot(d, "app_05_devices_empty_or_list")

        stamp = str(int(time.time()))[-5:]
        seeds = [
            ("Lab-PC-01", "Asha Mehta", "SN-A" + stamp, "Windows 11", True, True, True),
            ("Lab-PC-02", "Ravi Kulkarni", "SN-B" + stamp, "Windows 10", True, False, False),
            ("Faculty-Laptop-07", "Prof. Sharma", "SN-C" + stamp, "Ubuntu 22.04", True, True, False),
            ("Server-DB-01", "IT Dept", "SN-D" + stamp, "Ubuntu 22.04", False, True, True),
        ]
        d.get(MAIN + "/devices/new")
        shot(d, "app_06_create_form")
        # validation error: submit empty
        click_wait(d, By.ID, "save")
        shot(d, "app_07_validation_errors")
        for s in seeds:
            add_device(d, MAIN, *s)
        shot(d, "app_08_device_details")  # last created (non compliant) details
        d.get(MAIN + "/devices")
        shot(d, "app_09_devices_list")

        # search
        d.find_element(By.ID, "q").send_keys("lab")
        click_wait(d, By.ID, "search")
        shot(d, "app_10_search_lab")

        # details + workflow as technician
        d.get(MAIN + "/devices")
        d.find_element(By.PARTIAL_LINK_TEXT, "Lab-PC-02").click()
        shot(d, "app_11_details_admin_view")
        detail_url = d.current_url
        # update (edit) form
        d.get(detail_url + "/edit")
        shot(d, "app_12_edit_form")
        d.get(detail_url)
        logout(d, MAIN)

        login(d, MAIN, "tech", "tech123")
        d.get(detail_url)
        click_wait(d, By.ID, "to-UNDER_REVIEW")
        shot(d, "app_13_technician_moved_under_review")
        click_wait(d, By.ID, "to-REMEDIATED")
        shot(d, "app_14_technician_remediated_history")
        logout(d, MAIN)

        login(d, MAIN, "auditor", "auditor123")
        d.get(detail_url)
        shot(d, "app_15_auditor_can_close")
        click_wait(d, By.ID, "to-CLOSED")
        shot(d, "app_16_closed_with_history")
        d.get(MAIN + "/dashboard")
        shot(d, "app_17_dashboard")

        # ---- step 12: docker container ------------------------------------------------------
        d.get(DOCKER + "/")
        shot(d, "app_18_home_docker_container")
        d.get(DOCKER + "/actuator/health")
        shot(d, "app_19_health_docker_container")

        # ---- step 14: ansible-provisioned node ---------------------------------------------
        d.get(NODE + "/")
        shot(d, "app_20_home_ansible_node")
        d.get(NODE + "/actuator/health")
        shot(d, "app_21_health_ansible_node")
    finally:
        d.quit()


if __name__ == "__main__":
    sys.exit(main())
