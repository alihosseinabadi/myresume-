"""Import a job posting from a URL.

The engine chain (:mod:`services.scrapers`) is walked with a *usability* check:
a page only counts as a win if it actually contains a job advert. A bot wall, a
cookie banner, a search-results page or an empty shell therefore makes the chain
move on to the next engine instead of producing a garbage CV.
"""

from __future__ import annotations

import re
from urllib.parse import urlparse

import httpx

from ai.keywords import extract_keywords, normalize
from config import settings
from models import JobPosting
from services.html_extract import HtmlProbe, first_string, json_ld_jobs, strip_html
from services.scrapers import Outcome, scrape

MAX_DESCRIPTION = 9000
MIN_USABLE_CHARS = 200

# Pages that are long enough to pass a length check but are not an advert: bot
# walls, verification puzzles and error pages. One of these once became a CV for
# a role called "Human Verification", so they are named and rejected outright.
_WALLED_RE = re.compile(
    r"human verification|verif(?:y|ication) (?:that )?you are (?:a )?human|"
    r"checking your browser|just a moment|attention required|captcha|"
    r"please enable javascript|enable javascript and cookies|"
    r"solve a puzzle|access denied|request blocked|unusual traffic",
    re.IGNORECASE,
)

# Titles that belong to an error page, never to a CV. "Not found" was once
# written into a summary ("Results-driven Not found …").
_ERROR_TITLE_RE = re.compile(
    r"^(?:not\s+found|40[0-9]|50[0-9]|error|page\s+not\s+found|access\s+denied|"
    r"human\s+verification|just\s+a\s+moment|something\s+went\s+wrong|"
    r"forbidden|unavailable|temporarily\s+unavailable)\s*[.:|-]?\s*$",
    re.IGNORECASE,
)

# Hosts that are the platform, never the employer. Taking the first label gave
# "Boards" for boards.greenhouse.io and "Jobs" for jobs.lever.co.
_PLATFORM_DOMAINS = {
    "greenhouse.io", "lever.co", "ashbyhq.com", "workable.com", "smartrecruiters.com",
    "recruitee.com", "personio.de", "personio.com", "myworkdayjobs.com", "icims.com",
    "linkedin.com", "indeed.com", "glassdoor.com", "bamboohr.com", "teamtailor.com",
}
_PLATFORM_PREFIXES = {"boards", "jobs", "job", "apply", "careers", "staff", "www"}


def company_from_host(host: str) -> str:
    """A company name we can stand behind — or '' when the host does not say.

    A careers subdomain (``careers.acme.com``) names the employer; the board
    hosts above name the platform, and guessing there put wrong companies on
    people's CVs.
    """
    labels = [label for label in (host or "").lower().split(".") if label and label != "www"]
    if not labels:
        return ""
    if ".".join(labels[-2:]) in _PLATFORM_DOMAINS:
        return ""
    if labels[0] in _PLATFORM_PREFIXES and len(labels) > 2:
        labels = labels[1:]
    return normalize(labels[0].capitalize())


def _page_problem(title: str, description: str) -> str:
    """Why this page must not become a CV — or '' when it is a real advert."""
    if _ERROR_TITLE_RE.match(title.strip()):
        return "That page is an error page, not a job advert."
    if _WALLED_RE.search(f"{title}\n{description}"):
        return (
            "The site put up a verification page instead of the advert "
            "(it may block automated reads). Paste the advert text instead."
        )
    return ""


def _clean_title(raw: str) -> str:
    """Trim site suffixes like '| Acme Careers' from the page title."""
    title = normalize(raw)
    return re.split(r"\s[|\-–—·]\s", title)[0].strip() or title


def _from_markdown(markdown: str) -> tuple[str, str]:
    """Pull a title and body out of a reader-proxy / ScrapeGraphAI markdown dump."""
    heading = ""
    for line in markdown.splitlines():
        if line.lstrip().startswith("#"):
            heading = _clean_title(line.lstrip("# ").strip())
            break
    body = re.sub(r"^#+\s.*$", "", markdown, flags=re.MULTILINE)
    body = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", body)
    body = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", body)
    return heading, normalize(body)[:MAX_DESCRIPTION]


def _from_html(html: str, url: str) -> tuple[str, str, str, str, str, bool]:
    """Return ``(title, company, location, description, source, looks_like_listing)``."""
    probe = HtmlProbe()
    try:
        probe.feed(html)
    except Exception:  # noqa: BLE001
        pass

    jobs = json_ld_jobs(probe.json_ld)
    posting = jobs[0] if jobs else {}

    title = _clean_title(
        first_string(posting.get("title"))
        or probe.meta.get("og:title", "")
        or probe.meta.get("twitter:title", "")
        or probe.title
    )
    host = urlparse(url).netloc.replace("www.", "")
    company = normalize(
        first_string(posting.get("hiringOrganization"))
        or probe.meta.get("og:site_name", "")
        or company_from_host(host)
    )
    location = normalize(first_string(posting.get("jobLocation")))

    body = strip_html(first_string(posting.get("description")) or "")
    source = "json-ld"
    if len(body) < 400:
        fallback = f"{probe.meta.get('description', '')}\n{probe.text}"
        if len(fallback) > len(body):
            body = fallback
            source = "meta" if probe.meta.get("description") else "html"

    # A page full of job links is a search-results page, not one advert.
    job_links = [href for href in probe.links if "job" in href.lower()]
    looks_like_listing = not jobs and len(job_links) >= 20

    return title, company, location, body[:MAX_DESCRIPTION], source, looks_like_listing


def _parse_outcome(outcome: Outcome, url: str, host: str) -> JobPosting:
    """Turn one engine's result into a JobPosting (usable or not)."""
    if outcome.html:
        title, company, location, description, source, listing = _from_html(outcome.html, url)
    elif outcome.markdown:
        title, description = _from_markdown(outcome.markdown)
        company, location, source, listing = host.split(".")[0].title(), "", "markdown", False
    else:
        return JobPosting(url=url, ok=False, company=host, message="The engine returned no page.")

    listing_note = (
        "That page lists many jobs rather than one advert. Open the specific job page "
        "(or paste the job description) and we will build the CV from it."
        if listing
        else ""
    )
    # A page can be long and still not be an advert: bot walls and error pages
    # read as "content" to a length check, so they are checked by content too.
    problem_note = (
        _page_problem(title, description) if len(description) >= MIN_USABLE_CHARS else ""
    )
    ok = len(description) >= MIN_USABLE_CHARS and not listing and not problem_note
    if _ERROR_TITLE_RE.match(title.strip()):
        title = ""  # an error page must never name the CV
    empty_note = (
        ""
        if ok
        else "We could not find a readable job description on that page (it may be a bot "
        "wall, an empty shell, or it may need JavaScript). Paste the advert text instead."
    )

    return JobPosting(
        url=url,
        ok=ok,
        title=title,
        company=company,
        location=location,
        description=description,
        keywords=extract_keywords(description, limit=25) if description else [],
        source=source,
        engine=outcome.engine,
        message=listing_note or problem_note or empty_note,
    )


def fetch_job(
    url: str,
    client: httpx.Client | None = None,
    timeout: float | None = None,
    engines: list[str] | None = None,
) -> JobPosting:
    """Fetch ``url`` and return the best job posting we could actually read.

    ``engines`` overrides ``SCRAPE_ENGINES`` for this call (tests use ``["http"]``).
    """
    target = (url or "").strip()
    if not target:
        return JobPosting(ok=False, message="Paste the link to the job advert first.")
    if not target.lower().startswith(("http://", "https://")):
        target = f"https://{target}"

    parsed = urlparse(target)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return JobPosting(url=target, ok=False, message="That does not look like a valid URL.")

    host = parsed.netloc.replace("www.", "")

    def parse(outcome: Outcome) -> tuple[bool, JobPosting]:
        job = _parse_outcome(outcome, target, host)
        return job.ok, job

    outcome = scrape(
        target,
        timeout=timeout or settings.scrape_timeout_seconds,
        client=client,
        engines=engines,
        parse=parse,
    )
    attempts = [f"{a.engine}: {a.detail}" for a in outcome.attempts]

    if outcome.engine and isinstance(outcome.payload, JobPosting):
        return outcome.payload.model_copy(
            update={"attempts": attempts, "engine": outcome.engine}
        )

    best = outcome.payload if isinstance(outcome.payload, JobPosting) else None
    return JobPosting(
        url=target,
        ok=False,
        title=best.title if best else "",
        company=best.company if best else host,
        source=best.source if best else "",
        attempts=attempts,
        message=(best.message if best else "")
        or "Every fetch engine failed ("
        + "; ".join(attempts)
        + "). Paste the advert text instead and we will tailor the CV from it.",
    )
