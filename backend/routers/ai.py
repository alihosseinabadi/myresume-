"""AI endpoints: writing assistance, ATS scoring, translation, drafting, chat."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel

from ai import engine, engine_ats, letters, providers
from db import ai_usage, list_cover_letters, save_cover_letter
from models import (
    AiListResponse,
    AiTextResponse,
    AtsScoreRequest,
    AtsScoreResponse,
    BulletsRequest,
    CoverLetterRequest,
    DraftResumeRequest,
    ProfileContext,
    ResignationRequest,
    ResignationResponse,
    Resume,
    SkillsRequest,
    SummaryRequest,
    TranslateRequest,
)

router = APIRouter(prefix="/api/ai", tags=["ai"])


class RewriteRequest(BaseModel):
    text: str
    instruction: str = "make it more impactful"
    context: ProfileContext | None = None


class ChatRequest(BaseModel):
    question: str
    cv_text: str = ""


class TranslateResponse(BaseModel):
    locale: str
    headings: dict[str, str]


@router.get("/providers")
def get_providers() -> dict:
    """Which providers are configured, and which one will answer next."""
    return {
        "providers": providers.catalog(),
        "active": providers.active_provider_name(),
        "offline_capable": True,
    }


@router.post("/summary", response_model=AiTextResponse)
def post_summary(req: SummaryRequest) -> AiTextResponse:
    return engine.generate_summary(req)


@router.post("/bullets", response_model=AiListResponse)
def post_bullets(req: BulletsRequest) -> AiListResponse:
    return engine.generate_bullets(req)


@router.post("/skills", response_model=AiListResponse)
def post_skills(req: SkillsRequest) -> AiListResponse:
    return engine.suggest_skills(req)


@router.post("/rewrite", response_model=AiTextResponse)
def post_rewrite(req: RewriteRequest) -> AiTextResponse:
    return engine.rewrite(req.text, req.instruction, req.context)


@router.post("/cover-letter", response_model=AiTextResponse)
def post_cover_letter(req: CoverLetterRequest, save: bool = False) -> AiTextResponse:
    result = engine.generate_cover_letter(req)
    if save:
        save_cover_letter(
            letter_id=uuid4().hex[:12],
            body=result.text,
            company=req.company,
            job_title=req.job_title,
            provider=result.provider,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
    return result


@router.get("/cover-letters")
def get_cover_letters(limit: int = 20) -> dict:
    letters = list_cover_letters(limit)
    return {"letters": letters, "count": len(letters)}


@router.post("/ats-score", response_model=AtsScoreResponse)
def post_ats_score(req: AtsScoreRequest) -> AtsScoreResponse:
    return engine_ats.score_ats(req)


@router.post("/translate", response_model=TranslateResponse)
def post_translate(req: TranslateRequest) -> TranslateResponse:
    """Instant heading localisation across 24 locales — never needs a provider."""
    return TranslateResponse(
        locale=req.target_locale,
        headings=engine.translate_sections(req.target_locale, req.headings or None),
    )


@router.post("/draft", response_model=Resume)
def post_draft(req: DraftResumeRequest) -> Resume:
    """Turn a one-line brief into an editable CV skeleton."""
    return engine.draft_resume(req)


@router.post("/chat", response_model=AiTextResponse)
def post_chat(req: ChatRequest) -> AiTextResponse:
    return engine_ats.chat(req.question, req.cv_text)


@router.post("/resignation", response_model=ResignationResponse)
def post_resignation(req: ResignationRequest) -> ResignationResponse:
    """A short, warm, professional resignation letter — never invents a reason."""
    return letters.resignation_letter(req)


@router.get("/usage")
def get_usage(days: int = 7) -> dict:
    """Calls per feature/provider from the ai_events table."""
    rows = ai_usage(days)
    return {"days": days, "usage": rows, "total_calls": sum(r["calls"] for r in rows)}
