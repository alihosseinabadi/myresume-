"""
End-to-end smoke test: drive the Studio in a real browser so the landing page ->
FastAPI backend wiring (localhost:8010 + CORS) is exercised, not just rendered.
"""

import os
import time

from playwright.sync_api import sync_playwright

OUT = r"C:\Users\ali hosseinabadi\myresume\screenshots\live"
URL = "http://localhost:3000/#studio"
os.makedirs(OUT, exist_ok=True)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1536, "height": 900})

        api_calls = []
        page.on(
            "response",
            lambda r: api_calls.append((r.status, r.url)) if "8010" in r.url else None,
        )
        errors = []
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)

        page.goto(URL, wait_until="networkidle", timeout=90_000)

        # Fill the form with the bundled sample advert, then generate.
        page.get_by_role("button", name="Sample advert").click()
        time.sleep(0.8)
        page.get_by_role("button", name="Build my CV").click()

        # Wait for the backend round-trip to land in the DOM.
        page.wait_for_timeout(12_000)

        shot = os.path.join(OUT, "06-studio-generated.png")
        page.screenshot(path=shot)
        print(f"wrote : {shot}")

        print(f"\nbackend calls ({len(api_calls)}):")
        for status, url in api_calls:
            print(f"  {status}  {url}")

        print(f"\nconsole errors: {len(errors)}")
        for e in errors:
            print(f"  {e[:200]}")

        browser.close()


if __name__ == "__main__":
    main()
