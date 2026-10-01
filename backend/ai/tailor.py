"""Tailor a CV to a specific job advert.

This is the product's headline flow: give us a job link (or paste the advert, or
just name the role) and you get back a full CV — summary, achievement bullets and
a skills block written against that advert — plus the ATS score for it. It uses
the same AI provider chain and falls back to the offline engine, so it always
returns something usable.
"""

from __future__ import annotations

import re

from ai import engine
from ai.keywords import KNOWN_PHRASES, extract_keywords, normalize
from ai.skills import (
    KNOWN_SKILL_TERMS,
    SKILL_DISPLAY,
    family_for_role,
    family_label,
)
from ai.translations import translate_heading
from models import (
    BulletsRequest,
    ExperienceItem,
    JobPosting,
    PersonalInfo,
    ProfileContext,
    Resume,
    SkillGroup,
    SkillsRequest,
    SummaryRequest,
    TailorRequest,
    TailorResponse,
)
from services.ats import score_resume
from services.job_import import fetch_job

# Words that end a job title phrase but carry no meaning.
_TITLE_TAIL_WORDS = {
    "wanted", "needed", "required", "role", "position", "job", "opening",
    "opportunity", "vacancy", "candidate", "candidates", "applicants", "hire",
}
_TITLE_LEAD_WORDS = {
    "we", "we're", "our", "the", "a", "an", "join", "about", "careers", "job",
    "jobs", "now", "hiring", "seeking", "looking", "for", "of", "to", "be", "is",
    "are", "who", "with", "and", "in", "at", "this", "role", "position",
}
_TITLE_RE = re.compile(
    r"(?:hiring|looking for|seeking)\s+(?:an?\s+|one\s+)?"
    r"([A-Z][\w/+#.\-]*(?:\s+[A-Z][\w/+#.\-]*){0,4})"
)


def infer_title(text: str) -> str:
    """Guess the job title from advert text (used when no title or URL title)."""
    cleaned = normalize(text)
    if not cleaned:
        return ""

    match = _TITLE_RE.search(cleaned)
    if match:
        return _trim_title(match.group(1))

    # Otherwise take the opening phrase and strip filler words from both ends.
    opening = re.split(r"[.\n]", cleaned)[0]
    words = opening.split()[:6]
    while words and words[0].lower().strip(",:;") in _TITLE_LEAD_WORDS:
        words.pop(0)
    while words and words[-1].lower().strip(",:;") in _TITLE_TAIL_WORDS:
        words.pop()
    return _trim_title(" ".join(words))


def _trim_title(phrase: str) -> str:
    words = phrase.split()
    while words and words[-1].lower().strip(",:;") in _TITLE_TAIL_WORDS:
        words.pop()
    return " ".join(words).strip(" ,;:.") if words else ""



# Page titles arrive as adverts, not as roles: "Вакансия Data Engineer
# (команда B2C-SQL) в г Москва", "Job: Nurse - Careers". Strip the board
# boilerplate so the CV only ever names the *role*.
_ROLE_LEAD_NOISE_RE = re.compile(
    r"^(?:\W*)(?:вакансия|вакансии|vacancy|vacancies|job|jobs|position|opening"
    r"|hiring|we are hiring)(?:\W+|$)",
    re.IGNORECASE,
)
_ROLE_PARENS_RE = re.compile(r"\s*\([^)]*\)")
_ROLE_LOCATION_RES = (
    re.compile(r"\s+[вВ]\s+г\s+[А-ЯЁA-Z].*$"),          # в г Москва
    re.compile(r"\s+[гГ]\.\s+[А-ЯЁA-Z].*$"),            # г. Москва
    re.compile(r"\s+[вВ]\s+[А-ЯЁ][а-яё]+.*$"),          # в Москве
    re.compile(r"\s+[iI]n\s+[A-Z][a-z]+.*$"),           # in Moscow
)


def clean_role_title(raw: str) -> str:
    """Reduce a scraped page title to the role a CV should be headed with.

    Returns "" only when the input was empty; an over-stripped title falls
    back to the original so a weird advert never erases the role name.
    """
    title = normalize(raw)
    if not title:
        return ""
    title = re.sub(r"^\W+", "", title)                  # emoji / bullets
    title = re.sub(r"\s[|\-–—·]\s.*$", "", title)       # " | Careers Board"
    title = _ROLE_LEAD_NOISE_RE.sub("", title)          # "Вакансия "
    title = _ROLE_PARENS_RE.sub(" ", title)             # "(команда B2C-SQL)"
    for location in _ROLE_LOCATION_RES:
        title = location.sub("", title)                 # " в г Москва"
    title = normalize(title).strip(" -:–—|·,.")
    return title or normalize(raw)


def resolve_job(req: TailorRequest) -> JobPosting:
    """A job posting from a URL, from pasted text, or bare from the job title."""
    if req.url.strip():
        job = fetch_job(req.url)
        if job.ok:
            return job
        # An unreadable link must not swallow an advert the user also pasted.
        pasted = normalize(req.job_description)
        if not pasted:
            return job
        return JobPosting(
            url=req.url,
            ok=True,
            title=req.job_title,
            description=pasted,
            keywords=extract_keywords(pasted, limit=25),
            source="paste",
            message=f"{job.message} The CV was written from the advert you pasted instead.",
        )

    text = normalize(req.job_description)
    if text:
        return JobPosting(
            ok=True,
            title=req.job_title,
            description=text,
            keywords=extract_keywords(text, limit=25),
            source="paste",
        )

    return JobPosting(ok=True, title=req.job_title, source="title")


def _unique(items: list[str], limit: int | None = None) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        cleaned = normalize(item)
        key = cleaned.lower()
        if cleaned and key not in seen:
            seen.add(key)
            out.append(cleaned)
    return out[:limit] if limit else out


def _advert_skills(keywords: list[str], limit: int = 8) -> list[str]:
    """Advert keywords the ontology recognises as skills, properly cased.

    Scraped adverts leak page furniture into their text (cookie banners,
    team codes, "quality-"/"integration-" hyphen debris). Only terms we can
    actually stand behind become CV skills — SQL, Spark, dbt, "Stakeholder
    management" — never "Cookies" or "Www.Sberbank.Ru". Concrete tools come
    first so a headline reads "Spark, ClickHouse, Kubernetes", not "Code
    review, Data Engineering". When the advert yields nothing recognisable
    we return [] and the role-ontology suggestions fill the skills block.
    """
    tools: list[str] = []
    phrases: list[str] = []
    for word in keywords:
        key = word.lower()
        if key not in KNOWN_SKILL_TERMS and key not in KNOWN_PHRASES:
            continue
        display = SKILL_DISPLAY.get(key, word.title())
        # A concrete tool (Spark, SQL) beats a practice phrase (Code review)
        # when both compete for the first slot of a headline.
        (phrases if " " in key else tools).append(display)
    return _unique(tools + phrases, limit)


def tailor_resume(req: TailorRequest) -> TailorResponse:
    job = resolve_job(req)
    advert = job.description
    jd_keywords = job.keywords or extract_keywords(advert, limit=25)

    # A link we could not read must not become a CV. In that case job.title
    # belongs to an error page or a bot wall — "Not found" once became a summary
    # reading "Results-driven Not found …". Hand back what the user already has
    # and say plainly what went wrong: the studio shows job.message and keeps
    # their input, so pasting the advert is one step away.
    if req.url.strip() and not job.ok:
        resume = (
            req.base_resume.model_copy(deep=True)
            if req.base_resume is not None
            else Resume(
                title=f"{req.job_title.strip() or 'New CV'} — tailored",
                template=req.template,
                locale=req.locale,
                personal=PersonalInfo(
                    full_name=req.full_name,
                    email=req.email,
                    phone=req.phone,
                    location=req.location,
                ),
            )
        )
        resume.template = req.template
        resume.locale = req.locale
        return TailorResponse(
            resume=resume,
            score=score_resume(resume, ""),
            job=job.model_copy(update={"title": "", "description": "", "keywords": []}),
            notes=[
                job.message
                or "We could not read that link. Paste the advert text and press build again."
            ],
        )

    title = clean_role_title(
        req.job_title.strip()
        or job.title.strip()
        or infer_title(advert)
        or (jd_keywords[0].title() if jd_keywords else "Professional")
    )
    family = family_for_role(title)

    # Everything we generate is seeded with the advert's own vocabulary.
    ctx = ProfileContext(
        job_title=title,
        company=job.company,
        industry=family_label(family),
        seniority=req.seniority,
        years_experience=req.years_experience,
        skills=req.skills or _advert_skills(jd_keywords, 8),
        achievements=req.achievements,
        tone=req.tone,
        locale=req.locale,
    )

    if req.base_resume is not None:
        resume = req.base_resume.model_copy(deep=True)
    else:
        resume = Resume(
            title=f"{title} — tailored",
            template=req.template,
            locale=req.locale,
            personal=PersonalInfo(
                full_name=req.full_name,
                email=req.email,
                phone=req.phone,
                location=req.location,
            ),
        )

    resume.template = req.template
    resume.locale = req.locale
    if not resume.personal.headline:
        resume.personal.headline = f"{title} | {', '.join(_unique(ctx.skills, 3))}" if ctx.skills else title

    # 1 ── summary written against the advert
    provider, latency = "local", 0
    summary = engine.generate_summary(
        SummaryRequest(**ctx.model_dump(), existing_text=resume.summary)
    )
    if summary.text:
        resume.summary = summary.text
    provider, latency = summary.provider, summary.latency_ms

    # 2 ── achievement bullets for the target role
    bullets = engine.generate_bullets(BulletsRequest(**ctx.model_dump(), role=title, count=4))
    if bullets.items:
        if resume.experience:
            resume.experience[0].bullets = bullets.items
        else:
            resume.experience = [
                ExperienceItem(
                    role=title,
                    # The advert's company is who you are applying *to*, never
                    # your employer — it must not land in the CV's history.
                    company="[Company]",
                    location=resume.personal.location or "[Location]",
                    start_date="[YYYY-MM]",
                    end_date="Present",
                    current=True,
                    bullets=bullets.items,
                )
            ]

    # 3 ── skills: the advert's own tools first, then role-ontology suggestions
    existing = [skill for group in resume.skills for skill in group.skills]
    suggested = engine.suggest_skills(
        SkillsRequest(**ctx.model_dump(), existing_skills=existing, limit=12)
    )
    from_advert = _advert_skills(jd_keywords, 10)
    merged = _unique(req.skills + from_advert + suggested.items, 16)
    if merged:
        resume.skills = [SkillGroup(name=translate_heading(req.locale, "Skills"), skills=merged)]
    added_count = len([s for s in from_advert if s.lower() not in {e.lower() for e in existing + req.skills}])

    # 4 ── score the finished CV against the advert it was written for
    score = score_resume(resume, advert)

    # 5 ── tell the truth about what happened
    notes: list[str] = []
    if job.message:
        notes.append(job.message)
    if not advert:
        notes.append(
            "No advert text was available, so the CV was written from the job title alone. "
            "Paste the advert text for a much sharper match."
        )
    # Keyword coverage is deliberately NOT repeated as prose here. The response
    # already carries `matched_keywords` and `missing_keywords` as data, and the
    # studio lists them under plain labels ("in your CV" / "worth adding, if
    # true"). A sentence like "Covered 14 of 24 advert keywords" reads as a mark
    # out of 100 — the one thing someone writing a CV should not be scored on.
    if added_count:
        notes.append(
            f"Carried {added_count} skill{'s' if added_count != 1 else ''} across from the "
            "advert — delete any that are not true for you."
        )

    return TailorResponse(
        resume=resume,
        score=score,
        job=job,
        matched_keywords=score.matched_keywords,
        missing_keywords=score.missing_keywords,
        provider=provider,
        latency_ms=latency,
        notes=notes,
    )
