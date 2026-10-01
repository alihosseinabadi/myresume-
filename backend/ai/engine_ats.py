"""AI features: ATS re-scoring narrative and the freeform CV assistant."""

from __future__ import annotations

from ai import prompts_letters
from ai.keywords import has_number, normalize, starts_with_action_verb, word_count
from ai.runtime import OFFLINE_MODEL, list_from, llm_json, text_from
from models import AiTextResponse, AtsScoreRequest, AtsScoreResponse
from services.ats import local_suggestions, score_resume


def score_ats(req: AtsScoreRequest) -> AtsScoreResponse:
    """Rule-based ATS score, optionally enriched with LLM-written fixes."""
    result = score_resume(req.resume, req.job_description)

    if not result.missing_keywords and not result.suggestions:
        return result

    data, provider, model, latency = llm_json(
        prompts_letters.ats_suggestions_messages(
            result.score, result.missing_keywords, req.resume.personal.headline
        ),
        "ats_suggestions",
        {"score": result.score, "missing": result.missing_keywords[:10]},
    )
    llm_fixes = list_from(data, "suggestions", "items")
    if llm_fixes:
        return result.model_copy(update={"suggestions": llm_fixes})

    return result.model_copy(update={"suggestions": local_suggestions(result.checks, result.missing_keywords)})


def offline_advice(cv_text: str) -> str:
    """Deterministic CV feedback used when no provider is reachable."""
    text = normalize(cv_text)
    words = word_count(text)
    bullets = [line.strip(" -•*") for line in (cv_text or "").splitlines() if line.strip().startswith(("-", "•", "*"))]
    quantified = [b for b in bullets if has_number(b)]
    verb_first = [b for b in bullets if starts_with_action_verb(b)]

    notes: list[str] = []
    if words < 250:
        notes.append("The document looks short — aim for 350-600 words for a one-page CV.")
    elif words > 900:
        notes.append("The document is long — trim to one page unless you have 10+ years of experience.")
    if bullets and len(quantified) / len(bullets) < 0.4:
        notes.append(
            f"Only {len(quantified)} of {len(bullets)} bullets contain a number. "
            "Add %, currency, time saved or volume to at least 40% of them."
        )
    if bullets and len(verb_first) / len(bullets) < 0.6:
        notes.append("Start each bullet with a past-tense action verb (Delivered, Reduced, Led).")
    if "@" not in text:
        notes.append("No email address detected — ATS software cannot route your application without one.")
    if "responsible for" in text.lower():
        notes.append("Replace 'Responsible for' with what you achieved, not what you were assigned.")
    if not notes:
        notes.append("Structure looks solid: add job-ad keywords into the summary and top bullets.")
    return " ".join(notes)


def chat(question: str, cv_text: str = "") -> AiTextResponse:
    """Freeform CV question answered in recruiter voice."""
    data, provider, model, latency = llm_json(
        prompts_letters.chat_messages(cv_text, {"question": question}), "chat",
        {"question": question, "cv": cv_text[:500]},
    )
    answer = text_from(data, "answer", "text")
    if answer:
        return AiTextResponse(text=answer, provider=provider, model=model, latency_ms=latency)

    return AiTextResponse(
        text=offline_advice(cv_text or question),
        provider="local", model=OFFLINE_MODEL, fallback=True,
    )
