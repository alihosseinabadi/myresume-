"""Recruiter-grade prompt templates (core writer features).

Every prompt asks for strict JSON so responses can be parsed and validated;
``engine._coerce_json`` repairs the common ways models wrap JSON.
"""

from __future__ import annotations

from models import BulletsRequest, ProfileContext, SkillsRequest, SummaryRequest

RECRUITER_SYSTEM = (
    "You are a senior technical recruiter and certified CV writer with 15 years "
    "of experience hiring across tech, finance, healthcare and the public sector. "
    "You write CV content that passes ATS keyword scans and reads like a human "
    "wrote it: specific, quantified, achievement-first, never fluffy. "
    "Never invent employers, dates, degrees or metrics you were not given. "
    "Always answer with valid JSON only, no markdown fences, no commentary."
)

TONE_GUIDE = {
    "professional": "neutral corporate register, plain and precise",
    "confident": "assertive ownership language, first-word verbs, no hedging",
    "friendly": "warm and human while staying businesslike",
    "concise": "shortest possible sentences, maximum information density",
    "executive": "strategic, board-level framing focused on impact and scale",
}


def _profile_block(ctx: ProfileContext) -> str:
    lines = [
        f"Target job title: {ctx.job_title or 'not specified'}",
        f"Seniority: {ctx.seniority}",
        f"Years of experience: {ctx.years_experience}",
        f"Industry: {ctx.industry or 'not specified'}",
        f"Key skills: {', '.join(ctx.skills) if ctx.skills else 'not specified'}",
        f"Raw achievements: {'; '.join(ctx.achievements) if ctx.achievements else 'not specified'}",
        f"Output language: {ctx.language} (locale {ctx.locale})",
        f"Tone: {ctx.tone} — {TONE_GUIDE.get(ctx.tone, TONE_GUIDE['professional'])}",
    ]
    return "\n".join(lines)


def summary_messages(req: SummaryRequest) -> list[dict[str, str]]:
    schema = '{"summary": "3 to 4 sentence professional summary"}'
    existing = (
        f"\nImprove this draft instead of starting over:\n{req.existing_text}\n"
        if req.existing_text
        else ""
    )
    user = (
        f"{_profile_block(req)}\n{existing}\n"
        "Write a CV professional summary of 55-90 words: who they are "
        "professionally, years and domain, two measurable strengths drawn from the "
        "achievements given, and the role they target next.\n"
        "Rules: no first-person pronouns, no clichés ('hard worker', 'team player'), "
        "no markdown, no placeholders like [X]. If a number is unknown, describe "
        "scope instead (team size, budget, volume, geography).\n"
        f"Return JSON exactly: {schema}"
    )
    return [
        {"role": "system", "content": RECRUITER_SYSTEM},
        {"role": "user", "content": user},
    ]


def bullets_messages(req: BulletsRequest) -> list[dict[str, str]]:
    count = max(2, min(req.count, 8))
    schema = '{"bullets": ["bullet 1", "bullet 2"]}'
    user = (
        f"{_profile_block(req)}\nRole: {req.role or req.job_title or 'not specified'}\n\n"
        f"Write {count} CV achievement bullets for this role.\n"
        "Each bullet: starts with a strong simple past-tense action verb, 12-28 words, "
        "follows 'Action + what + how + measurable outcome'. Where the given "
        "achievements lack numbers, express scale qualitatively (e.g. 'across three "
        "markets', 'for a 40-person team'). Never use 'Responsible for'. Vary the "
        "opening verbs across bullets.\n"
        f"Return JSON exactly: {schema}"
    )
    return [
        {"role": "system", "content": RECRUITER_SYSTEM},
        {"role": "user", "content": user},
    ]


def skills_messages(req: SkillsRequest) -> list[dict[str, str]]:
    limit = max(4, min(req.limit, 24))
    schema = '{"skills": ["skill 1", "skill 2"]}'
    user = (
        f"{_profile_block(req)}\n"
        f"Already listed: {', '.join(req.existing_skills) if req.existing_skills else 'none'}\n\n"
        f"List up to {limit} hard skills, tools and methodologies a recruiter would "
        "search for on this kind of CV, ordered by how often they appear in job ads "
        "for this title. Each entry: 1-4 words, no soft skills, no duplicates of the "
        "already listed ones.\n"
        f"Return JSON exactly: {schema}"
    )
    return [
        {"role": "system", "content": RECRUITER_SYSTEM},
        {"role": "user", "content": user},
    ]


def rewrite_messages(text: str, instruction: str, ctx: ProfileContext | None = None) -> list[dict[str, str]]:
    context = f"\nContext:\n{_profile_block(ctx)}" if ctx else ""
    user = (
        f"Rewrite the CV content below.\nInstruction: {instruction}\n{context}\n"
        f"Text:\n{text}\n\n"
        "Keep every factual claim, change only wording and structure for impact.\n"
        'Return JSON exactly: {"text": "rewritten text"}'
    )
    return [
        {"role": "system", "content": RECRUITER_SYSTEM},
        {"role": "user", "content": user},
    ]
