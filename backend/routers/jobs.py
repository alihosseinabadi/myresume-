"""Job-link endpoints: import an advert, then tailor a CV to it."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ai.tailor import tailor_resume
from models import JobImportRequest, JobPosting, TailorRequest, TailorResponse
from services.job_import import fetch_job
from services.scrapers import configured_order, engines_status

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("/import", response_model=JobPosting)
def post_import(req: JobImportRequest) -> JobPosting:
    """Fetch a job advert URL and return the posting we could read from it.

    The response reports which fetch engine won (``engine``) and what every other
    engine said (``attempts``), so a failure is diagnosable instead of silent.
    """
    job = fetch_job(req.url)
    if not job.url:
        raise HTTPException(status_code=422, detail=job.message or "Invalid URL")
    return job


@router.get("/engines")
def get_engines() -> dict:
    """Which fetch engines are configured and usable right now."""
    return {
        "order": configured_order(),
        "engines": engines_status(),
        "note": (
            "ScrapeGraphAI needs SGAI_API_KEY (hosted) or "
            "`pip install -r requirements-scraper.txt` (OSS, with a local LLM). "
            "Playwright needs `playwright install chromium`. The reader proxy and "
            "plain http need nothing."
        ),
    }


@router.post("/tailor", response_model=TailorResponse)
def post_tailor(req: TailorRequest) -> TailorResponse:
    """Job link (or advert text, or title) → a CV written for that job + its ATS score."""
    return tailor_resume(req)
