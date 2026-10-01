"""Scraper engine-chain tests: order, fall-through, crash containment, reporting."""

from __future__ import annotations

from models import JobPosting
from services import scrapers
from services.job_import import _parse_outcome, fetch_job
from services.scrapers import Attempt, Outcome, configured_order, engines_status, scrape

MARKDOWN_JOB = (
    "# Senior Data Analyst\n\n"
    "We are hiring a Senior Data Analyst to own experimentation and reporting. "
    "You will use SQL, Python, dbt and Airflow daily, partner with product on A/B "
    "testing, build Tableau dashboards for finance, and mentor two analysts. "
    "Stakeholder management and forecasting experience required.\n"
)


def stub_scrape(*, html: str = "", markdown: str = "", engine: str = "http"):
    """Replace the engine chain with a single canned result (already parsed)."""
    def fake(*args, **kwargs):
        outcome = Outcome(html=html or None, markdown=markdown or None, engine=engine)
        outcome.payload = _parse_outcome(outcome, "https://board.example/jobs/1", "board.example")
        return outcome

    return fake


def test_default_engine_order():
    # The structured ATS API is tried before any scraping engine.
    assert configured_order() == ["ats", "scrapegraph", "playwright", "reader", "http"]


def test_first_usable_engine_wins(monkeypatch):
    monkeypatch.setitem(scrapers.ENGINES, "scrapegraph", lambda url, t, client=None: (None, "needs key"))
    monkeypatch.setitem(scrapers.ENGINES, "playwright", lambda url, t, client=None: ("<html>ok</html>", "chromium"))
    monkeypatch.setitem(scrapers.ENGINES, "http", lambda url, t, client=None: ("should not run", "unused"))

    outcome = scrape("https://x.test", timeout=1, engines=["scrapegraph", "playwright", "http"])
    assert outcome.engine == "playwright"
    assert outcome.html == "<html>ok</html>"
    assert [a.ok for a in outcome.attempts] == [False, True]


def test_falls_through_when_earlier_engines_fail(monkeypatch):
    monkeypatch.setitem(scrapers.ENGINES, "ats", lambda url, t, client=None: (None, "not a supported job board"))
    monkeypatch.setitem(scrapers.ENGINES, "scrapegraph", lambda url, t, client=None: (None, "no api key"))
    monkeypatch.setitem(scrapers.ENGINES, "playwright", lambda url, t, client=None: (None, "not installed"))
    monkeypatch.setitem(scrapers.ENGINES, "reader", lambda url, t, client=None: (None, "blocked"))
    monkeypatch.setitem(scrapers.ENGINES, "http", lambda url, t, client=None: ("<html>plain</html>", "direct request"))

    outcome = scrape("https://x.test", timeout=1)
    assert outcome.engine == "http"
    assert len(outcome.attempts) == 5
    assert "won: http" in outcome.trail()


def test_reader_engine_returns_markdown(monkeypatch):
    monkeypatch.setitem(scrapers.ENGINES, "reader", lambda url, t, client=None: (MARKDOWN_JOB, "reader proxy"))
    outcome = scrape("https://x.test", timeout=1, engines=["reader", "http"])
    assert outcome.engine == "reader"
    assert outcome.markdown == MARKDOWN_JOB
    assert outcome.html is None


def test_all_engines_failing_is_reported(monkeypatch):
    for name in ("ats", "scrapegraph", "playwright", "reader", "http"):
        monkeypatch.setitem(scrapers.ENGINES, name, lambda url, t, client=None: (None, "blocked"))
    outcome = scrape("https://x.test", timeout=1)
    assert outcome.engine == ""
    assert len(outcome.attempts) == 5
    assert "all failed" in outcome.trail()


def test_engine_crash_does_not_break_the_chain(monkeypatch):
    def boom(url, timeout, client=None):
        raise RuntimeError("engine exploded")

    monkeypatch.setitem(scrapers.ENGINES, "scrapegraph", boom)
    monkeypatch.setitem(scrapers.ENGINES, "http", lambda url, t, client=None: ("<html>ok</html>", "direct"))
    outcome = scrape("https://x.test", timeout=1, engines=["scrapegraph", "http"])
    assert outcome.engine == "http"
    assert "crashed" in outcome.attempts[0].detail


def test_engines_status_lists_all_five():
    rows = engines_status()
    assert [row["engine"] for row in rows] == ["ats", "scrapegraph", "playwright", "reader", "http"]
    assert next(r for r in rows if r["engine"] == "http")["ready"] is True
    assert next(r for r in rows if r["engine"] == "ats")["ready"] is True


def test_engines_endpoint(client):
    body = client.get("/api/jobs/engines").json()
    assert body["order"][-1] == "http"
    assert body["order"][0] == "ats"
    assert len(body["engines"]) == 5
    assert "SGAI_API_KEY" in body["note"]


def test_fetch_job_reports_the_engine_that_won(monkeypatch):
    html = "<html><head><title>Data Analyst | Acme</title></head><body><p>" + (
        "SQL Python dbt Airflow dashboards A/B testing forecasting stakeholder management " * 6
    ) + "</p></body></html>"
    monkeypatch.setattr(
        "services.job_import.scrape",
        stub_scrape(html=html, engine="playwright"),
    )
    job = fetch_job("https://boards.example/job/1")
    assert job.ok is True
    assert job.engine == "playwright"
    assert job.title == "Data Analyst"


def test_fetch_job_parses_a_markdown_result(monkeypatch):
    monkeypatch.setattr(
        "services.job_import.scrape", stub_scrape(markdown=MARKDOWN_JOB, engine="reader")
    )
    job = fetch_job("https://boards.example/job/2")
    assert job.ok is True
    assert job.source == "markdown"
    assert job.title == "Senior Data Analyst"
    assert "Airflow" in job.description
    assert "sql" in job.keywords


def test_listing_page_is_rejected_not_tailored(monkeypatch):
    """A search-results page must not be mistaken for a single advert."""
    links = "".join(f'<a href="/remote-jobs/data-analyst-{i}">job {i}</a>' for i in range(30))
    html = (
        "<html><head><title>Remote jobs</title></head><body>" + links + "<p>"
        + "Browse thousands of remote data analyst jobs. " * 20
        + "</p></body></html>"
    )
    monkeypatch.setattr("services.job_import.scrape", stub_scrape(html=html, engine="playwright"))
    job = fetch_job("https://board.example/jobs")
    assert job.ok is False
    assert "lists many jobs" in job.message


def test_single_job_page_with_links_is_still_accepted(monkeypatch):
    """A real advert often links out; only link-heavy pages *without* JSON-LD are rejected."""
    links = "".join(f'<a href="/related-job-{i}">read more</a>' for i in range(30))
    html = (
        '<html><head><script type="application/ld+json">'
        '{"@type":"JobPosting","title":"Data Analyst","hiringOrganization":{"name":"Acme"},'
        '"description":"'
        + "SQL Python dbt dashboards forecasting experiments " * 12
        + '"}'
        "</script></head><body>" + links + "</body></html>"
    )
    monkeypatch.setattr("services.job_import.scrape", stub_scrape(html=html, engine="http"))
    job = fetch_job("https://board.example/jobs/123")
    assert job.ok is True
    assert job.title == "Data Analyst"


def test_empty_shell_page_is_reported_as_unusable(monkeypatch):
    """A cookie/bot-wall page fetches fine but has no advert — say so clearly."""
    monkeypatch.setattr(
        "services.job_import.scrape",
        stub_scrape(html="<html><body>Checking your browser…</body></html>", engine="playwright"),
    )
    job = fetch_job("https://board.example/jobs/999")
    assert job.ok is False
    assert "could not find a readable job description" in job.message.lower()


def test_chain_keeps_trying_until_the_page_is_usable(monkeypatch):
    """An engine that fetches a useless page must not end the chain."""
    good = "<html><body><p>" + ("SQL Python dbt dashboards forecasting " * 20) + "</p></body></html>"
    monkeypatch.setitem(
        scrapers.ENGINES, "playwright", lambda url, t, client=None: ("<html>Checking your browser…</html>", "chromium")
    )
    monkeypatch.setitem(
        scrapers.ENGINES, "reader", lambda url, t, client=None: (MARKDOWN_JOB, "reader proxy")
    )
    monkeypatch.setitem(
        scrapers.ENGINES, "http", lambda url, t, client=None: (good, "direct request")
    )
    job = fetch_job("https://board.example/jobs/1", engines=["playwright", "reader", "http"])
    assert job.ok is True
    assert job.engine == "reader"
    # the whole trail is preserved, including the page that had no job text
    assert any("no job text" in line for line in job.attempts)
    assert any(line.startswith("reader:") for line in job.attempts)


def test_unknown_engine_names_fall_back_to_http():
    assert configured_order(["nope", "also-nope"]) == ["http"]


def test_empty_engine_list_uses_the_configured_default():
    # An empty override means "no override", so the default chain is used.
    assert configured_order([]) == configured_order()
