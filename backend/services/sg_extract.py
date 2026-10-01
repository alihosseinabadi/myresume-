"""ScrapeGraphAI adapter for job-link import.

Supports both flavours of ScrapeGraphAI, because they solve different problems:

* **Hosted API** (``SGAI_API_KEY``) — managed JS rendering and anti-bot, billed per
  credit. We call the HTTP API directly, so no extra library is required.
* **OSS library** (``pip install scrapegraphai``) — MIT, runs against a local LLM
  (Ollama) or any key you already have. Free, self-hosted, your data stays local.

Whichever is configured is used; both are optional, and a failure here never
breaks the import because the engine chain falls through to the next one.
"""

from __future__ import annotations

import httpx

from config import settings

SCRAPEGRAPH_API = "https://api.scrapegraphai.com"

JOB_SCHEMA: dict = {
    "job_posting": {
        "title": "string — the job title",
        "company": "string — hiring company",
        "location": "string — city, country or remote",
        "employment_type": "string",
        "salary": "string",
        "description": "string — the full job description as plain text",
        "requirements": ["string — one requirement per item"],
        "responsibilities": ["string — one responsibility per item"],
    }
}

EXTRACTION_PROMPT = (
    "Extract the job posting on this page. Return the title, company, location, "
    "employment type, salary, the full description as plain text, and the "
    "requirements and responsibilities as separate lists."
)


def harvest(payload) -> str:
    """Pull readable job text out of whatever shape the engine returned."""
    if payload is None:
        return ""
    if isinstance(payload, str):
        return payload
    if not isinstance(payload, dict):
        return ""

    for key in ("content", "markdown", "description", "text"):
        value = payload.get(key)
        if isinstance(value, str) and len(value) > 200:
            return value

    posting = payload.get("job_posting")
    if isinstance(posting, dict):
        parts = [str(posting.get("description") or "")]
        for key in ("requirements", "responsibilities"):
            for item in posting.get(key) or []:
                parts.append(f"- {item}")
        return "\n".join(part for part in parts if part)

    data = payload.get("data")
    if data and data is not payload:
        return harvest(data)
    return ""


def _hosted(url: str, timeout: float) -> tuple[str | None, str]:
    """Try both API generations; v1 is /v1/smartscraper, v2 is /v1/extract."""
    routes = (
        (
            "/v1/smartscraper",
            {
                "user_prompt": EXTRACTION_PROMPT,
                "website_url": url,
                "is_dynamic": True,
                "only_description": False,
            },
        ),
        (
            "/v1/extract",
            {"prompt": EXTRACTION_PROMPT, "urls": [url], "is_dynamic": True},
        ),
    )
    last = "hosted api not tried"
    for path, body in routes:
        try:
            response = httpx.post(
                f"{SCRAPEGRAPH_API}{path}",
                headers={"SGAI_API_KEY": settings.scrapegraph_api_key},
                json=body,
                timeout=timeout,
            )
            if response.status_code == 404:
                last = f"no {path} route"
                continue
            response.raise_for_status()
            text = harvest(response.json())
            if text:
                return text, f"hosted api {path}"
            last = f"{path} returned no job text"
        except Exception as exc:  # noqa: BLE001
            last = f"hosted api {path} failed: {type(exc).__name__}"
    return None, last


def _library(url: str) -> tuple[str | None, str]:
    """OSS library against a local Ollama model (or any configured LLM)."""
    try:
        from scrapegraphai import SmartScraper  # type: ignore
    except Exception:  # noqa: BLE001
        return None, "scrapegraphai not installed (see requirements-scraper.txt)"

    try:
        model = settings.scrapegraph_llm_model or "ollama/llama3"
        if model.startswith("ollama/") or not settings.openai_api_key:
            from scrapegraphai import OllamaConfig  # type: ignore

            llm = OllamaConfig(
                model=model,
                base_url=settings.ollama_base_url,
                model_type="chat",
            )
        else:
            from scrapegraphai import OpenAI  # type: ignore

            llm = OpenAI(model=model, api_key=settings.openai_api_key)

        scraper = SmartScraper(
            llm_model=llm,
            url=url,
            prompt=EXTRACTION_PROMPT,
            schema=JOB_SCHEMA,
        )
        return harvest(scraper.run()), "oss library"
    except Exception as exc:  # noqa: BLE001
        return None, f"oss library failed: {type(exc).__name__}: {exc}"[:180]


def fetch_scrapegraph(
    url: str,
    timeout: float,
    client: httpx.Client | None = None,  # noqa: ARG001 - uniform engine signature
) -> tuple[str | None, str]:
    """Return ``(job_text, detail)`` using whichever ScrapeGraphAI flavour is available."""
    if not settings.scrapegraph_enabled:
        return None, "disabled in config"
    if settings.scrapegraph_api_key:
        text, detail = _hosted(url, timeout)
        if text:
            return text, detail
        library = _library(url) if settings.scrapegraph_fallback_to_library else (None, detail)
        return library
    return _library(url)
