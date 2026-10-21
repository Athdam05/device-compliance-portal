"""Full-page screenshots of public web pages (GitHub) using headless Edge via Selenium.
Usage: python capture_web.py name=url [name=url ...]   -> report/shots/<name>.png"""
import os
import sys
import time

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shots")
DRIVER = r"C:\Users\damal\tools\edgedriver\msedgedriver.exe"


def main(pairs):
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1280,900")
    opts.add_argument("--remote-allow-origins=*")
    opts.add_argument("--hide-scrollbars")
    d = webdriver.Edge(service=Service(DRIVER), options=opts)
    d.set_page_load_timeout(60)
    try:
        for pair in pairs:
            name, url = pair.split("=", 1)
            try:
                d.get(url)
            except Exception as e:  # page-load timeout: still take what is rendered
                print("warn", name, str(e)[:60])
            time.sleep(3)
            # include the whole page (cap the height)
            h = d.execute_script("return Math.min(document.documentElement.scrollHeight, 2600)")
            d.set_window_size(1280, max(h + 40, 700))
            time.sleep(1)
            d.save_screenshot(os.path.join(OUT, name + ".png"))
            d.set_window_size(1280, 900)
            print("saved", name, h)
    finally:
        d.quit()


if __name__ == "__main__":
    main(sys.argv[1:])
