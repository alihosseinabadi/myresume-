"""
End-to-end test for shared "CV brief" links (`/c/<payload>`).

What it proves:
  1. The payload format is language-agnostic — a token built outside the browser
     (the way a link generator would) decodes and renders.
  2. The sender's flow really produces a working link: build a CV in the studio,
     open "Send as a link", and follow the URL the browser generated.
  3. The recipient gets their OWN CV: their name comes pre-filled, the job builds
     by itself on arrival, and the sender's greeting is in the server HTML (so
     crawlers and no-JS visitors see it too).
  4. A truncated link and a hostile payload are both handled gracefully.
"""

import base64
import json
import os
import urllib.request

from playwright.sync_api import sync_playwright

OUT = r"C:\Users\ali hosseinabadi\myresume\screenshots\live"
BASE = "http://localhost:3000"

failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}{f' — {detail}' if detail and not ok else ''}")
    if not ok:
        failures.append(label)


def make_token(payload: dict) -> str:
    """Mirror of encodeBrief() in landing/src/lib/share.ts."""
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def fetch(path: str) -> str:
    with urllib.request.urlopen(f"{BASE}{path}", timeout=30) as response:
        return response.read().decode("utf-8", "replace")


def main() -> None:
    os.makedirs(OUT, exist_ok=True)

    # ── 1. A token built outside the browser still renders ────────────────
    print("\n[1] cross-language payload")
    token = make_token(
        {
            "v": 1,
            "from": "Sara López",
            "to": "Ali",
            "role": "Registered Nurse",
            "template": "geneva",
            "locale": "de",
            "note": "This one is yours.",
        }
    )
    html = fetch(f"/c/{token}")
    check("sender name in server HTML", "Sara" in html)
    check("recipient greeted in server HTML", "Hi Ali" in html)
    check("role is in the server HTML", "Registered Nurse" in html)
    check("note is in the server HTML", "This one is yours." in html)
    check("template applied to the studio", "geneva" in html.lower())
    check("studio copy is server-rendered too", "Your CV, already briefed." in html)
    check("personal link is noindex", "noindex" in html)

    # ── 2. A hostile payload is escaped, not executed ─────────────────────
    print("\n[2] hostile payload")
    hostile = make_token({"v": 1, "role": '<img src=x onerror="alert(1)">'})
    hostile_html = fetch(f"/c/{hostile}")
    check("markup from the payload is escaped", "&lt;img" in hostile_html)
    check("no raw injected tag", "<img src=x" not in hostile_html)

    # ── 3. A truncated link explains itself ───────────────────────────────
    print("\n[3] truncated link")
    broken_html = fetch("/c/not-a-real-token")
    check("broken link is explained", "did not survive the trip" in broken_html)
    check("broken link is not indexed", "noindex" in broken_html)

    # ── 4. Sender builds a CV, shares it, recipient opens it ──────────────
    print("\n[4] browser round trip")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={"width": 1536, "height": 950},
            permissions=["clipboard-read", "clipboard-write"],
        )

        # sender: build a CV from the sample advert, then share it
        sender = context.new_page()
        sender_errors: list[str] = []
        sender.on(
            "console",
            lambda m: sender_errors.append(m.text) if m.type == "error" else None,
        )
        sender.goto(f"{BASE}/#studio", wait_until="networkidle", timeout=90_000)
        sender.get_by_role("button", name="Sample advert").click()
        sender.get_by_role("button", name="Build my CV").click()
        sender.wait_for_selector("text=written for", timeout=60_000)

        # The result panel must read as help, never as a verdict on the person
        # using it: no score out of 100, no letter grade, and the CV's own text
        # must not be printed a second time next to the CV sheet.
        studio = sender.locator("#studio")
        panel = studio.inner_text()
        check("no score out of 100", "/100" not in panel)
        check("no letter grade", "grade" not in panel.lower())
        check("no 'missing' label", "missing" not in panel.lower())
        check("coverage is not repeated as prose", "advert keywords" not in panel.lower())
        check("result is announced as ready", "ready" in panel.lower())
        check("keywords are phrased plainly", "in your cv" in panel.lower())

        paper = " ".join(studio.locator("article").first.inner_text().split())
        flat = " ".join(panel.split())
        sentences = [s.strip() for s in paper.split(".") if len(s.strip()) > 40]
        check("found CV text to compare", bool(sentences))
        repeated = [s for s in sentences if flat.count(s[:60]) > 1]
        check("CV text is not printed twice", not repeated, f"{len(repeated)} sentence(s) repeated")

        # one set of download buttons, on the CV sheet — not two
        # (the accessible name is the DOM text, "pdf", not the CSS-uppercased "PDF")
        exports_found = sum(
            studio.get_by_role("button", name=fmt, exact=True).count()
            for fmt in ("pdf", "docx", "txt")
        )
        check("exactly one set of download buttons", exports_found == 3, f"found {exports_found}")
        sender.screenshot(path=os.path.join(OUT, "09-result-panel-simplified.png"))

        sender.get_by_role("button", name="Send as a link").click()
        sender.get_by_label("Your name", exact=True).fill("Sara")
        sender.get_by_label("Their name", exact=True).fill("Alireza")
        sender.get_by_label("One line for them", exact=True).fill("Made you a head start.")
        link = sender.get_by_label("Your shareable CV link").input_value()
        check("link points at the share route", link.startswith(f"{BASE}/c/"), link[:60])
        sender.screenshot(path=os.path.join(OUT, "07-send-as-a-link.png"))

        sender.get_by_role("button", name="Copy link").click()
        sender.wait_for_timeout(400)
        clipboard = sender.evaluate("() => navigator.clipboard.readText()")
        check("copy button puts the link on the clipboard", clipboard == link)

        # what the browser encoded must match the documented format
        payload = json.loads(base64.urlsafe_b64decode(link.split("/c/")[1] + "=="))
        check("payload carries the sender", payload.get("from") == "Sara")
        check("payload carries the recipient", payload.get("to") == "Alireza")
        check(
            "payload carries the advert text the studio used",
            payload.get("text", "").startswith("Senior Data Analyst"),
        )
        check(
            "payload carries the bare role, not a generated headline",
            payload.get("role") == "Senior Data Analyst",
            str(payload.get("role")),
        )
        check("payload version", payload.get("v") == 1)
        check("sender had no console errors", not sender_errors, str(sender_errors[:2]))

        # recipient: open the link the browser produced
        receiver = context.new_page()
        receiver_errors: list[str] = []
        receiver.on(
            "console",
            lambda m: receiver_errors.append(m.text) if m.type == "error" else None,
        )
        receiver.goto(link, wait_until="domcontentloaded", timeout=90_000)

        heading = receiver.locator("h1").first.inner_text()
        check("recipient sees the greeting", "Alireza" in heading and "Sara" in heading, heading)
        check("recipient sees the note", "Made you a head start." in receiver.content())

        # the CV builds itself, with the recipient's own name on it
        receiver.wait_for_function(
            """() => {
                const node = document.querySelector('article h3');
                return node && node.textContent.trim() === 'Alireza';
            }""",
            timeout=60_000,
        )
        check("recipient's own name is on the CV", True)

        receiver.wait_for_timeout(800)
        receiver.screenshot(path=os.path.join(OUT, "08-shared-cv-received.png"))
        check("recipient had no console errors", not receiver_errors, str(receiver_errors[:2]))
        check(
            "no hydration mismatch on the shared page",
            not any("hydrat" in error.lower() for error in receiver_errors),
            str(receiver_errors[:2]),
        )

        browser.close()

    print("\n" + "=" * 60)
    print("ALL CHECKS PASSED" if not failures else f"{len(failures)} FAILED: {failures}")
    print("=" * 60)


if __name__ == "__main__":
    main()
