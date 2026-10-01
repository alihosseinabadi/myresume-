"""AI features: writing assistance (summary, bullets, skills, rewrite, letters)."""

from __future__ import annotations

from ai import local_engine, prompts, prompts_letters
from ai.keywords import normalize, to_bullet_case
from ai.runtime import OFFLINE_MODEL, list_from, llm_json, text_from
from models import (
    AiListResponse,
    AiTextResponse,
    BulletsRequest,
    CoverLetterRequest,
    DraftResumeRequest,
    ExperienceItem,
    PersonalInfo,
    ProfileContext,
    Resume,
    SkillGroup,
    SkillsRequest,
    SummaryRequest,
)


def generate_summary(req: SummaryRequest) -> AiTextResponse:
    """Recruiter-style professional summary (55-90 words)."""
    data, provider, model, latency = llm_json(
        prompts.summary_messages(req), "summary", req.model_dump()
    )
    text = text_from(data, "summary", "text")
    if text:
        return AiTextResponse(text=text, provider=provider, model=model, latency_ms=latency)
    return AiTextResponse(
        text=local_engine.generate_summary(req),
        provider="local", model=OFFLINE_MODEL, fallback=True,
    )


def generate_bullets(req: BulletsRequest) -> AiListResponse:
    """Achievement bullets for one role."""
    data, provider, model, latency = llm_json(
        prompts.bullets_messages(req), "bullets", req.model_dump()
    )
    items = list_from(data, "bullets", "items")
    if items:
        return AiListResponse(items=items, provider=provider, model=model, latency_ms=latency)
    return AiListResponse(
        items=local_engine.generate_bullets(req),
        provider="local", model=OFFLINE_MODEL, fallback=True,
    )


def suggest_skills(req: SkillsRequest) -> AiListResponse:
    """ATS search terms for the target job title."""
    data, provider, model, latency = llm_json(
        prompts.skills_messages(req), "skills", req.model_dump()
    )
    items = list_from(data, "skills", "items")
    if items:
        return AiListResponse(items=items, provider=provider, model=model, latency_ms=latency)
    return AiListResponse(
        items=local_engine.suggest_skills(req),
        provider="local", model=OFFLINE_MODEL, fallback=True,
    )


def rewrite(
    text: str,
    instruction: str = "make it more impactful",
    ctx: ProfileContext | None = None,
) -> AiTextResponse:
    """Rewrite a snippet of CV content without changing any facts."""
    data, provider, model, latency = llm_json(
        prompts.rewrite_messages(text, instruction, ctx), "rewrite",
        {"text": text, "instruction": instruction},
    )
    rewritten = text_from(data, "text", "rewritten")
    if rewritten:
        return AiTextResponse(text=rewritten, provider=provider, model=model, latency_ms=latency)
    return AiTextResponse(
        text=local_engine.rewrite_text(text, instruction),
        provider="local", model=OFFLINE_MODEL, fallback=True,
    )


def generate_cover_letter(req: CoverLetterRequest) -> AiTextResponse:
    """Matching cover letter, tailored to the job ad when one is supplied."""
    data, provider, model, latency = llm_json(
        prompts_letters.cover_letter_messages(req), "cover_letter",
        {"job_title": req.job_title, "company": req.company, "jd": req.job_description[:400]},
    )
    letter = text_from(data, "letter", "text")
    if letter:
        return AiTextResponse(text=letter, provider=provider, model=model, latency_ms=latency)
    return AiTextResponse(
        text=local_engine.generate_cover_letter(req),
        provider="local", model=OFFLINE_MODEL, fallback=True,
    )


def draft_resume(req: DraftResumeRequest) -> Resume:
    """Turn a one-line brief into an editable CV skeleton."""
    data, provider, model, latency = llm_json(
        prompts_letters.draft_resume_messages(req.prompt, req.locale), "draft_resume",
        req.model_dump(),
    )
    if isinstance(data, dict) and (data.get("summary") or data.get("experience")):
        resume = Resume(
            title=str(data.get("title") or "Drafted resume")[:120],
            template=req.template,
            locale=req.locale,
            personal=PersonalInfo.model_validate(data.get("personal") or {}),
            summary=normalize(str(data.get("summary") or "")),
        )
        for item in data.get("experience") or []:
            if not isinstance(item, dict):
                continue
            resume.experience.append(
                ExperienceItem(
                    role=str(item.get("role") or ""),
                    company=str(item.get("company") or ""),
                    location=str(item.get("location") or ""),
                    start_date=str(item.get("start_date") or ""),
                    end_date=str(item.get("end_date") or ""),
                    current=str(item.get("end_date") or "").lower().startswith("present"),
                    bullets=[to_bullet_case(str(b)) for b in (item.get("bullets") or [])],
                )
            )
        for group in data.get("skills") or []:
            if isinstance(group, dict) and group.get("skills"):
                resume.skills.append(
                    SkillGroup(
                        name=str(group.get("name") or "Skills"),
                        skills=[str(s) for s in group["skills"]],
                    )
                )
        return resume

    return local_engine.draft_resume(req)


def translate_sections(target_locale: str, headings: list[str] | None = None) -> dict[str, str]:
    """Localised section headings — no LLM needed, instant and always available."""
    from ai.translations import translate_headings

    return translate_headings(target_locale, headings)
