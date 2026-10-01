"""Collect browser console output + page errors from the landing page."""

from playwright.sync_api import sync_playwright

URL = "http://localhost:3000/"
messages = []

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1536, "height": 864})
    page.on("console", lambda m: messages.append((m.type, m.text)))
    page.on("pageerror", lambda e: messages.append(("pageerror", str(e))))
    page.goto(URL, wait_until="networkidle", timeout=90_000)
    page.wait_for_timeout(6000)
    browser.close()

print(f"captured {len(messages)} console messages")
for kind, text in messages:
    if kind in ("error", "warning", "pageerror") or "hydration" in text.lower():
        print(f"[{kind}] {text}")
