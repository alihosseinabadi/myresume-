"""Structured job-board APIs — the reliable way to read a real advert.

Boards fight scrapers, but the same boards publish every advert as JSON for
their own widgets. Where we recognise the board we ask that API first: no bot
wall, no JavaScript, no HTML guesswork — and the company and location come back
as real fields instead of being guessed from a hostname.

Every provider is reduced to the same ``(token, job_id)`` pair plus a fetch, so
adding a board is a few lines. The result is handed to the normal parse path as
a synthetic JSON-LD document (:func:`posting_as_html`), so all engines are
parsed by identical, already-tested code.
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html import escape, unescape
from urllib.parse import parse_qs, urlparse

import httpx

from ai.keywords import normalize
from services.html_extract import strip_html

JSON_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 MyResumeBot/1.0"
    ),
}


@dataclass(frozen=True)
class BoardRef:
    """A job link we can read through the board's own JSON API."""

    board: str      # greenhouse | lever | ashby | workable | smartrecruiters…
    token: str      # the board's company slug, e.g. "figma"
    job_id: str     # the posting id inside that board
    url: str        # the link the user pasted
    host: str = ""  # the board host that answered, kept for the API base
    slug: str = ""  # human slug from the URL, used when the id is not the job id


@dataclass
class Posting:
    """One advert, normalised across every provider."""

    title: str = ""
    company: str = ""
    location: str = ""
    description: str = ""
    board: str = ""


def _parts(parsed) -> list[str]:
    return [p for p in parsed.path.split("/") if p]


def _humanize(slug: str) -> str:
    """A board slug as a company name: ``steer-health`` → ``Steer Health``."""
    words = [w for w in slug.replace("_", "-").replace(".", "-").split("-") if w]
    if not words:
        return ""
    # Keep existing camel case ("eBay", "iCIMS") but title-case plain slugs.
    return " ".join(w if any(c.isupper() for c in w) else w.capitalize() for w in words)


def _ref(board: str, token: str, job_id: str, parsed, **extra) -> BoardRef | None:
    """A ref only when we have both halves of the pair — otherwise not our link."""
    if not token or not job_id:
        return None
    return BoardRef(
        board=board,
        token=token.strip().lower(),
        job_id=job_id.strip(),
        url=parsed.geturl(),
        host=parsed.netloc,
        **extra,
    )


def _greenhouse(parsed) -> BoardRef | None:
    """``boards.greenhouse.io/{token}/jobs/{id}`` and the classic embed form."""
    if not parsed.netloc.endswith("greenhouse.io"):
        return None
    parts = _parts(parsed)
    query = parse_qs(parsed.query)
    token = job = ""
    if "job_app" in parts:
        token = (query.get("for") or [""])[0]
        job = (query.get("token") or query.get("gh_jid") or [""])[0]
    elif "jobs" in parts:
        index = parts.index("jobs")
        if index >= 1 and len(parts) > index + 1:
            token, job = parts[index - 1], parts[index + 1]
    elif len(parts) >= 2:
        token, job = parts[0], parts[1]
    return _ref("greenhouse", token, job, parsed)


def _lever(parsed) -> BoardRef | None:
    """``jobs.lever.co/{token}/{uuid}`` (the ``/apply`` tail is dropped)."""
    if not parsed.netloc.endswith("lever.co"):
        return None
    parts = [p for p in _parts(parsed) if p not in {"apply", "thanks"}]
    if len(parts) < 2:
        return None
    return _ref("lever", parts[0], parts[1], parsed)


def _ashby(parsed) -> BoardRef | None:
    """``jobs.ashbyhq.com/{token}/{uuid}``."""
    if not parsed.netloc.endswith("ashbyhq.com"):
        return None
    parts = _parts(parsed)
    query = parse_qs(parsed.query)
    if len(parts) >= 2:
        return _ref("ashby", parts[0], parts[1], parsed)
    if query.get("jobId"):
        return _ref("ashby", parts[0] if parts else "", query["jobId"][0], parsed)
    return None


def _workable(parsed) -> BoardRef | None:
    """``apply.workable.com/{token}/j/{code}`` and the shared ``view`` links.

    A ``view`` link carries a board-view code, not the posting's own code, so the
    company is recovered from the slug (``…-at-steer-health``) and the advert is
    then matched on its title.
    """
    if not parsed.netloc.endswith("workable.com"):
        return None
    parts = _parts(parsed)
    if not parts:
        return None
    if len(parts) >= 3 and parts[1] in {"j", "jobs"}:
        return _ref("workable", parts[0], parts[2], parsed)
    if parts[0] == "view" and len(parts) >= 2:
        slug = parts[2] if len(parts) > 2 else ""
        marker = slug.rfind("-at-")
        token = slug[marker + 4 :] if marker >= 0 else ""
        return _ref("workable", token, parts[1], parsed, slug=slug)
    if parts[-2] in {"j", "jobs"}:  # {token}.workable.com/j/{code}
        return _ref("workable", parts[0], parts[-1], parsed)
    return None


def _smartrecruiters(parsed) -> BoardRef | None:
    """``jobs.smartrecruiters.com/{token}/{id}-{slug}``."""
    if not parsed.netloc.endswith("smartrecruiters.com"):
        return None
    parts = _parts(parsed)
    if len(parts) < 2:
        return None
    return _ref("smartrecruiters", parts[0], parts[1].split("-")[0], parsed)


def _recruitee(parsed) -> BoardRef | None:
    """``{token}.recruitee.com/o/{slug}-{id}``."""
    if not parsed.netloc.endswith("recruitee.com"):
        return None
    parts = _parts(parsed)
    if len(parts) < 2:
        return None
    digits = "".join(c for c in parts[1] if c.isdigit())
    return _ref("recruitee", parsed.netloc.split(".")[0], digits, parsed)


def _personio(parsed) -> BoardRef | None:
    """``{token}.jobs.personio.de/job/{id}`` (the feed is XML)."""
    if not parsed.netloc.endswith(("jobs.personio.de", "jobs.personio.com")):
        return None
    parts = _parts(parsed)
    digits = next((p for p in parts if p.isdigit()), "")
    return _ref("personio", parsed.netloc.split(".")[0], digits, parsed)


def _workday(parsed) -> BoardRef | None:
    """``{tenant}.wd{n}.myworkdayjobs.com/{lang}/{site}/job/{path}``.

    Workday has no per-job GET: the advert lives behind a POST to its ``/wday/cxs``
    endpoint, and the ref keeps ``tenant`` and ``site`` (the pair that addresses it).
    """
    if "myworkdayjobs.com" not in parsed.netloc:
        return None
    parts = _parts(parsed)
    if len(parts) < 3 or "job" not in parts:
        return None
    index = parts.index("job")
    site = parts[index - 1] if index >= 1 else ""
    job_id = "/".join(parts[index + 1 :])
    tenant = parsed.netloc.split(".")[0]
    return _ref("workday", f"{tenant}|{site}", job_id, parsed)


DETECTORS = (
    _greenhouse,
    _lever,
    _ashby,
    _workable,
    _smartrecruiters,
    _recruitee,
    _personio,
    _workday,
)


def detect(url: str) -> BoardRef | None:
    """Recognise a job link that can be read through a structured board API."""
    try:
        parsed = urlparse(url)
    except ValueError:
        return None
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    for detector in DETECTORS:
        try:
            ref = detector(parsed)
        except Exception:  # noqa: BLE001 - a malformed link is not a crash
            continue
        if ref is not None:
            return ref
    return None


# ── fetching ──────────────────────────────────────────────


def _json(ref: BoardRef, api_url: str, timeout: float, client, **kwargs):
    """One JSON request through the chain's client (so tests can fake it)."""
    call = client.request if client is not None else httpx.request
    response = call(kwargs.pop("method", "GET"), api_url, timeout=timeout,
                    headers=JSON_HEADERS, follow_redirects=True, **kwargs)
    response.raise_for_status()
    return response.json()


def _text(raw: str) -> str:
    """Advert text out of whatever the board gave us: HTML, escaped HTML or plain."""
    value = unescape(raw or "")
    if "<" in value and ">" in value:
        value = strip_html(value)
    return normalize(value)


def _where(*parts) -> str:
    """A readable location from the fragments boards return."""
    seen, words = set(), []
    for part in parts:
        if isinstance(part, (list, tuple)):
            part = ", ".join(str(item) for item in part)
        cleaned = normalize(str(part or ""))
        if cleaned and cleaned.lower() not in seen:
            seen.add(cleaned.lower())
            words.append(cleaned)
    return ", ".join(words)


def _greenhouse_posting(ref: BoardRef, timeout: float, client) -> Posting | None:
    data = _json(
        ref,
        f"https://boards-api.greenhouse.io/v1/boards/{ref.token}/jobs/{ref.job_id}"
        "?questions=false",
        timeout,
        client,
    )
    if not isinstance(data, dict):
        return None
    return Posting(
        title=normalize(data.get("title") or ""),
        company=normalize(data.get("company_name") or "") or _humanize(ref.token),
        location=_where((data.get("location") or {}).get("name", "")),
        description=_text(data.get("content") or ""),
        board=ref.board,
    )


def _lever_posting(ref: BoardRef, timeout: float, client) -> Posting | None:
    host = "api.eu.lever.co" if ".eu." in ref.host else "api.lever.co"
    data = _json(
        ref, f"https://{host}/v0/postings/{ref.token}/{ref.job_id}", timeout, client
    )
    if not isinstance(data, dict):
        return None

    categories = data.get("categories") or {}
    lists = data.get("lists") or []
    body = " ".join(
        part for part in (
            _text(data.get("descriptionBodyPlain") or data.get("descriptionPlain") or ""),
            _text(data.get("additionalPlain") or ""),
            " ".join(_text(f"{item.get('text', '')} {item.get('content', '')}") for item in lists),
        ) if part
    )
    return Posting(
        title=normalize(data.get("text") or ""),
        # Lever's API has no company field; the token is the company slug.
        company=_humanize(ref.token),
        location=_where(categories.get("location", ""), data.get("workplaceType", "")),
        description=normalize(body),
        board=ref.board,
    )


def _ashby_posting(ref: BoardRef, timeout: float, client) -> Posting | None:
    data = _json(
        ref,
        f"https://api.ashbyhq.com/posting-api/job-board/{ref.token}",
        timeout,
        client,
    )
    jobs = (data or {}).get("jobs") if isinstance(data, dict) else None
    if not isinstance(jobs, list):
        return None

    match = next(
        (
            job for job in jobs
            if isinstance(job, dict)
            and (
                str(job.get("id", "")) == ref.job_id
                or str(job.get("jobUrl", "")).rstrip("/").endswith(ref.job_id)
            )
        ),
        None,
    )
    if match is None:
        return None
    return Posting(
        title=normalize(match.get("title") or ""),
        company=_humanize(ref.token),
        location=_where(match.get("location", ""), match.get("workplaceType", "")),
        description=_text(match.get("descriptionPlain") or match.get("descriptionHtml") or ""),
        board=ref.board,
    )


def _workable_posting(ref: BoardRef, timeout: float, client) -> Posting | None:
    data = _json(
        ref,
        f"https://apply.workable.com/api/v1/widget/accounts/{ref.token}?details=true",
        timeout,
        client,
    )
    if not isinstance(data, dict):
        return None
    jobs = data.get("jobs") or []
    match = next(
        (job for job in jobs if str(job.get("shortcode", "")).lower() == ref.job_id.lower()),
        None,
    )
    if match is None and ref.slug:
        # A `view` link carries a board code, so match the advert by its title.
        wanted = ref.slug
        marker = wanted.rfind("-at-")
        if marker >= 0:
            wanted = wanted[:marker]
        wanted = wanted.replace("-", " ").lower()
        match = next(
            (job for job in jobs if normalize(str(job.get("title", ""))).lower() in wanted),
            None,
        )
    if match is None:
        return None
    return Posting(
        title=normalize(match.get("title") or ""),
        company=normalize(data.get("name") or "") or _humanize(ref.token),
        location=_where(match.get("city", ""), match.get("country", ""), match.get("region", "")),
        description=_text(match.get("description") or ""),
        board=ref.board,
    )


def _smartrecruiters_posting(ref: BoardRef, timeout: float, client) -> Posting | None:
    data = _json(
        ref,
        f"https://api.smartrecruiters.com/v1/companies/{ref.token}/postings/{ref.job_id}",
        timeout,
        client,
    )
    if not isinstance(data, dict):
        return None
    advert = ((data.get("jobAd") or {}).get("sections") or {}).get("jobDescription") or {}
    location = data.get("location") or {}
    return Posting(
        title=normalize(data.get("name") or ""),
        company=normalize((data.get("company") or {}).get("name", "")) or _humanize(ref.token),
        location=_where(location.get("city", ""), location.get("region", ""), location.get("country", "")),
        description=_text(advert.get("text") or ""),
        board=ref.board,
    )


def _recruitee_posting(ref: BoardRef, timeout: float, client) -> Posting | None:
    data = _json(ref, f"https://{ref.host}/api/offers/{ref.job_id}", timeout, client)
    offer = (data or {}).get("offer") if isinstance(data, dict) else None
    if not isinstance(offer, dict):
        return None
    return Posting(
        title=normalize(offer.get("title") or ""),
        company=_humanize(ref.token),
        location=_where(offer.get("city", ""), offer.get("country_name", "")),
        description=_text(offer.get("description") or ""),
        board=ref.board,
    )


def _personio_posting(ref: BoardRef, timeout: float, client) -> Posting | None:
    """Personio publishes an XML feed; the posting id in the URL selects one."""
    call = client.request if client is not None else httpx.request
    response = call(
        "GET", f"https://{ref.host}/xml?language=en", timeout=timeout,
        headers=JSON_HEADERS, follow_redirects=True,
    )
    response.raise_for_status()
    root = ET.fromstring(response.content)

    def text_of(node, tag: str) -> str:
        for child in node.iter():
            if child.tag.split("}")[-1] == tag and child.text:
                return normalize(child.text)
        return ""

    for position in root.iter():
        if position.tag.split("}")[-1] not in {"workstelle", "position"}:
            continue
        if text_of(position, "id") != ref.job_id:
            continue
        body = " ".join(
            value
            for value in (
                text_of(section, "value")
                for section in position.iter()
                if section.tag.split("}")[-1] in {"jobDescription", "requirement"}
            )
            if value
        )
        return Posting(
            title=text_of(position, "name"),
            company=_humanize(ref.token),
            location=text_of(position, "office"),
            description=body,
            board=ref.board,
        )
    return None


def _workday_posting(ref: BoardRef, timeout: float, client) -> Posting | None:
    tenant, _, site = ref.token.partition("|")
    data = _json(
        ref,
        f"https://{ref.host}/wday/cxs/{tenant}/{site}/job/{ref.job_id}",
        timeout,
        client,
        method="POST",
        json={},
    )
    info = (data or {}).get("jobPostingInfo") if isinstance(data, dict) else None
    if not isinstance(info, dict) or not info.get("title"):
        return None
    organisation = (data.get("hiringOrganization") or {}).get("name", "")
    return Posting(
        title=normalize(info.get("title") or ""),
        company=normalize(organisation) or _humanize(tenant),
        location=_where(info.get("location", ""), info.get("additionalLocations", "")),
        description=_text(info.get("jobDescription") or ""),
        board=ref.board,
    )


FETCHERS = {
    "greenhouse": _greenhouse_posting,
    "lever": _lever_posting,
    "ashby": _ashby_posting,
    "workable": _workable_posting,
    "smartrecruiters": _smartrecruiters_posting,
    "recruitee": _recruitee_posting,
    "personio": _personio_posting,
    "workday": _workday_posting,
}

BOARDS_LABEL = "greenhouse, lever, ashby, workable, smartrecruiters, workday"


def posting_as_html(posting: Posting) -> str:
    """Hand a structured advert to the normal parse path as JSON-LD.

    One parser for every engine: the HTML import path already knows how to pull
    title, company, location and body out of a JobPosting node, so the board API
    feeds it instead of duplicating that logic.
    """
    block = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "JobPosting",
            "title": posting.title,
            "hiringOrganization": {"@type": "Organization", "name": posting.company},
            "jobLocation": {"@type": "Place", "address": {"addressLocality": posting.location}},
            "description": posting.description,
        },
        ensure_ascii=False,
    ).replace("</", "<\\/")

    return (
        "<!doctype html><html><head><title>"
        + escape(posting.title)
        + "</title><meta name=\"description\" content=\""
        + escape(posting.description[:4000], quote=True)
        + "\"><meta property=\"og:site_name\" content=\""
        + escape(posting.company, quote=True)
        + "\"></head><body><script type=\"application/ld+json\">"
        + block
        + "</script></body></html>"
    )


def fetch_ats(url: str, timeout: float, client=None) -> tuple[str | None, str]:
    """Engine entry point: read a known job board through its own JSON API.

    The signature matches the other engines in :mod:`services.scrapers`, so it
    drops into the chain without special-casing. Returning ``None`` means "this
    engine did not help" and the chain simply continues to the next one.
    """
    ref = detect(url)
    if ref is None:
        return None, "not a supported job board"
    fetch = FETCHERS.get(ref.board)
    if fetch is None:
        return None, f"{ref.board}: no reader configured"
    try:
        posting = fetch(ref, timeout, client)
    except httpx.HTTPStatusError as exc:
        return None, f"{ref.board} api: HTTP {exc.response.status_code}"
    except httpx.HTTPError as exc:
        return None, f"{ref.board} api: {type(exc).__name__}"
    except Exception as exc:  # noqa: BLE001 - one bad board must not kill the chain
        return None, f"{ref.board} api: {type(exc).__name__}"

    if posting is None or not normalize(posting.description):
        return None, f"{ref.board} api: no advert text"
    return posting_as_html(posting), f"{ref.board} api"


