"""Pluggable page-fetching engines for job-link import.

Job boards fight scrapers, so no single fetcher is reliable. We walk a chain and
report which engine answered:

1. ``ats``         — the board's own JSON API when we recognise the board
                     (Greenhouse, Lever, Ashby, Workable, SmartRecruiters,
                     Recruitee, Personio, Workday): see services.ats_boards
2. ``scrapegraph`` — ScrapeGraphAI (hosted API or the OSS library, see sg_extract)
3. ``playwright``  — renders JavaScript-heavy pages in headless Chromium
4. ``reader``      — a markdown reader proxy, useful against bot walls
5. ``http``        — plain httpx, then parsed for JSON-LD / OG / visible text

Engines are skipped automatically when their dependency or key is missing, so an
absent extra never breaks the app. Order comes from ``SCRAPE_ENGINES``.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import httpx

from config import settings
from services.ats_boards import BOARDS_LABEL, fetch_ats
from services.sg_extract import fetch_scrapegraph

READER_BASE = "https://r.jina.ai"
BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 MyResumeBot/1.0"
)


@dataclass
class Attempt:
    engine: str
    ok: bool
    detail: str = ""


@dataclass
class Outcome:
    html: str | None = None
    markdown: str | None = None
    engine: str = ""
    attempts: list[Attempt] = field(default_factory=list)
    payload: object | None = None

    def trail(self) -> str:
        steps = " → ".join(f"{a.engine}:{'ok' if a.ok else 'no'}" for a in self.attempts)
        return f"{steps} (won: {self.engine})" if self.engine else f"{steps} (all failed)"


def fetch_playwright(
    url: str,
    timeout: float,
    client: httpx.Client | None = None,  # noqa: ARG001 - uniform engine signature
) -> tuple[str | None, str]:
    """Render the page in headless Chromium — required by JS-only job boards."""
    if not settings.scrape_playwright_enabled:
        return None, "disabled in config"
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception:  # noqa: BLE001
        return None, "playwright not installed (see requirements-scraper.txt)"
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page(user_agent=BROWSER_UA)
            page.goto(url, timeout=timeout * 1000, wait_until="domcontentloaded")
            # Boards paint their advert *after* first paint, so returning here
            # handed back an empty shell and the chain reported "no job text".
            # Wait for the network to settle and for real text to exist.
            try:
                page.wait_for_load_state("networkidle", timeout=min(timeout * 500, 12000))
                page.wait_for_function(
                    "() => (document.body && document.body.innerText || '').length > 800",
                    timeout=6000,
                )
            except Exception:  # noqa: BLE001 - a slow page still gets a chance
                pass
            html = page.content()
            browser.close()
            return (html, "headless chromium") if html else (None, "empty render")
    except Exception as exc:  # noqa: BLE001
        return None, f"playwright failed: {type(exc).__name__}"


def fetch_reader(
    url: str,
    timeout: float,
    client: httpx.Client | None = None,
) -> tuple[str | None, str]:
    """A markdown reader proxy — frequently gets through where a plain request cannot."""
    if not settings.scrape_reader_enabled:
        return None, "disabled in config"
    try:
        get = client.get if client is not None else httpx.get
        response = get(
            f"{READER_BASE}/{url}",
            timeout=timeout,
            headers={"Accept": "text/plain", "User-Agent": BROWSER_UA},
        )
        response.raise_for_status()
        text = response.text
        return (text, "reader proxy") if len(text) > 200 else (None, "reader returned too little")
    except Exception as exc:  # noqa: BLE001
        return None, f"reader proxy failed: {type(exc).__name__}"


def fetch_http(
    url: str,
    timeout: float,
    client: httpx.Client | None = None,
) -> tuple[str | None, str]:
    """Plain request — always available; the JSON-LD/meta parser works on this."""
    owned = client is None
    http = client or httpx.Client(timeout=timeout, follow_redirects=True)
    try:
        response = http.get(
            url, headers={"User-Agent": BROWSER_UA, "Accept-Language": "en;q=0.9"}
        )
        response.raise_for_status()
        return response.text, "direct request"
    except Exception as exc:  # noqa: BLE001
        return None, f"direct request failed: {type(exc).__name__}"
    finally:
        if owned:
            http.close()


ENGINES = {
    # The structured API first: it answers in one request, without a bot wall.
    "ats": fetch_ats,
    "scrapegraph": fetch_scrapegraph,
    "playwright": fetch_playwright,
    "reader": fetch_reader,
    "http": fetch_http,
}


def configured_order(engines: list[str] | None = None) -> list[str]:
    raw = engines or settings.scrape_engines.split(",")
    order = [name.strip().lower() for name in raw if name.strip()]
    return [name for name in order if name in ENGINES] or ["http"]


def scrape(
    url: str,
    timeout: float | None = None,
    client: httpx.Client | None = None,
    engines: list[str] | None = None,
    parse: "callable | None" = None,
) -> Outcome:
    """Try each configured engine in order and return the first *usable* result.

    ``parse(outcome) -> (usable, payload)`` lets the caller define what "usable"
    means — for job import that is "this page actually contains a job advert",
    so a bot wall or a listing page makes the chain move on to the next engine
    instead of being accepted. The best-effort outcome is returned if no engine
    produces something usable.
    """
    timeout = timeout or settings.scrape_timeout_seconds
    attempts: list[Attempt] = []
    best: Outcome | None = None

    for name in configured_order(engines):
        try:
            result, detail = ENGINES[name](url, timeout, client=client)
        except Exception as exc:  # noqa: BLE001 - one bad engine must not kill the chain
            attempts.append(Attempt(name, False, f"crashed: {type(exc).__name__}"))
            continue

        if not result:
            attempts.append(Attempt(name, False, detail))
            continue

        outcome = Outcome(engine=name)
        if name == "reader":
            outcome.markdown = result
        else:
            outcome.html = result

        usable, payload = True, None
        if parse is not None:
            try:
                usable, payload = parse(outcome)
            except Exception as exc:  # noqa: BLE001
                usable, payload, detail = False, None, f"parse failed: {type(exc).__name__}"
        outcome.payload = payload

        if usable:
            # Keep the whole trail so the caller can see every engine we tried.
            outcome.attempts = [*attempts, Attempt(name, True, detail)]
            return outcome

        # Fetched something, but it was not a job advert — try the next engine.
        attempts.append(Attempt(name, False, f"no job text ({detail})"))
        if best is None:
            best = outcome

    if best is not None:
        best.engine = ""  # nothing was usable
        best.attempts = attempts
    return best or Outcome(attempts=attempts)


def engines_status() -> list[dict]:
    """Which engines are usable right now (drives ``GET /api/jobs/engines``)."""
    enabled = set(configured_order())
    status: list[dict] = []

    for name in ("ats", "scrapegraph", "playwright", "reader", "http"):
        ready, detail = True, "built in"
        if name == "ats":
            detail = f"job boards: {BOARDS_LABEL}"
        elif name == "scrapegraph":
            if not settings.scrapegraph_enabled:
                ready, detail = False, "disabled in config"
            elif settings.scrapegraph_api_key:
                detail = "hosted API key set"
            else:
                try:
                    import scrapegraphai  # noqa: F401

                    detail = "oss library, needs a local LLM (Ollama)"
                except Exception:  # noqa: BLE001
                    ready = False
                    detail = "needs SGAI_API_KEY or: pip install scrapegraphai"
        elif name == "playwright":
            try:
                import playwright  # noqa: F401

                detail = "chromium available"
            except Exception:  # noqa: BLE001
                ready = False
                detail = "pip install playwright && playwright install chromium"

        status.append(
            {"engine": name, "ready": ready, "enabled": name in enabled, "detail": detail}
        )

    return status
