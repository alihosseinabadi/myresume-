"""
Capture the MyResume landing page for visual verification.

Renders http://localhost:3000 at a desktop viewport, scrolls the whole page so
the IntersectionObserver reveals fire, then writes a full-page shot plus
per-section shots into screenshots/live/.
"""

import os
import time

from playwright.sync_api import sync_playwright

OUT = r"C:\Users\ali hosseinabadi\myresume\screenshots\live"
URL = "http://localhost:3000/"
VIEWPORT = {"width": 1536, "height": 864}

SECTIONS = [
    ("01-hero", "#top"),
    ("02-studio", "#studio"),
    ("03-templates", "#templates"),
    ("04-pricing", "#pricing"),
    ("05-faq", "#faq"),
]


def settle_reveals(page):
    """Scroll to the bottom in steps so every [data-reveal] enters the viewport."""
    height = page.evaluate("document.body.scrollHeight")
    y = 0
    while y < height:
        page.mouse.wheel(0, 500)
        y += 500
        time.sleep(0.12)
        height = page.evaluate("document.body.scrollHeight")
    page.evaluate("window.scrollTo(0, 0)")
    # Reveal.tsx keeps a 5s failsafe timer; wait past it so nothing stays faded.
    time.sleep(5.5)
    return height


def main():
    os.makedirs(OUT, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport=VIEWPORT, device_scale_factor=1)
        page.goto(URL, wait_until="networkidle", timeout=90_000)

        title = page.title()
        height = settle_reveals(page)
        print(f"title   : {title}")
        print(f"height  : {height}px")

        full = os.path.join(OUT, "00-full-page.png")
        page.screenshot(path=full, full_page=True)
        print(f"wrote   : {full}")

        for name, selector in SECTIONS:
            el = page.query_selector(selector)
            if el is None:
                print(f"missing : {selector}")
                continue
            path = os.path.join(OUT, f"{name}.png")
            el.screenshot(path=path)
            box = el.bounding_box()
            size = f"{int(box['width'])}x{int(box['height'])}" if box else "?"
            print(f"wrote   : {path}  ({size})")

        # Any browser console errors are worth surfacing.
        browser.close()


if __name__ == "__main__":
    main()
