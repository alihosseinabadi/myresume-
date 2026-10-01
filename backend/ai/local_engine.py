"""Deterministic offline resume engine — the zero-API-key fallback.

It is rule-based, not stochastic: the same input always produces the same
output, which makes it testable and safe to serve when every LLM provider is
unreachable. Drafts intentionally contain bracketed metric slots such as
``[X%]`` because the product promise is "pre-written content you edit", and the
engine must never fabricate numbers it was not given.
"""

from __future__ import annotations

from ai.keywords import (
    extract_keywords,
    normalize,
    starts_with_action_verb,
    to_bullet_case,
    word_count,
)
from ai.lexicon import ACTION_VERBS
from ai.skills import family_for_role
from ai.translations import LOCALE_NAMES, translate_heading
from models import (
    BulletsRequest,
    CoverLetterRequest,
    DraftResumeRequest,
    ExperienceItem,
    LanguageItem,
    PersonalInfo,
    ProfileContext,
    Resume,
    SkillGroup,
    SkillsRequest,
    SummaryRequest,
)

VERB_CYCLE: list[str] = (
    ACTION_VERBS["delivery"] + ACTION_VERBS["improvement"] + ACTION_VERBS["building"]
    + ACTION_VERBS["leadership"] + ACTION_VERBS["collaboration"] + ACTION_VERBS["analysis"]
)

SENIORITY_LABEL = {
    "intern": "Early-career", "junior": "Motivated", "mid": "Results-driven",
    "senior": "Senior", "lead": "Lead", "manager": "Managerial",
    "director": "Director-level", "executive": "Executive",
}

SENIORITY_WORDS = (
    "intern", "junior", "mid", "senior", "lead", "head", "chief", "principal",
    "staff", "manager", "director", "vp", "president", "founder", "apprentice",
)


def _has_seniority_word(title: str) -> bool:
    """True when the title already carries a level, e.g. 'Senior Data Analyst'."""
    first = (title or "").strip().lower().split(" ")[0].rstrip(",")
    return first in SENIORITY_WORDS


TONE_OPENERS = {
    "professional": "{label} {title} with {years} in {industry}.",
    "confident": "{label} {title} with {years} turning {industry} complexity into measurable delivery.",
    "friendly": "{label} {title} with {years} solving {industry} problems alongside teams that ship.",
    "concise": "{label} {title}, {years} in {industry}, focused on {focus}.",
    "executive": "{label} {title} with {years} operating at {industry} leadership level.",
}


def _years_phrase(years: int) -> str:
    if years <= 0:
        return "hands-on project exposure"
    if years == 1:
        return "1 year of experience"
    return f"{years}+ years of experience"


def _industry(ctx: ProfileContext) -> str:
    return ctx.industry.strip() if ctx.industry.strip() else "the sector"


def _focus_terms(ctx: ProfileContext, limit: int = 3) -> list[str]:
    pool = [s.strip() for s in ctx.skills if s.strip()]
    if not pool:
        pool = ROLE_SKILLS_POOL(ctx)
    return pool[:limit] if pool else ["operational delivery"]


def ROLE_SKILLS_POOL(ctx: ProfileContext) -> list[str]:
    from ai.skills import ROLE_SKILLS

    family = family_for_role(ctx.job_title or ctx.industry)
    return list(ROLE_SKILLS.get(family, ROLE_SKILLS["operations"]))


def _join(terms: list[str]) -> str:
    terms = [t for t in terms if t]
    if not terms:
        return "core delivery"
    if len(terms) == 1:
        return terms[0]
    return f"{', '.join(terms[:-1])} and {terms[-1]}"


def _achievement_sentence(ctx: ProfileContext, opener: str = "Delivered") -> str:
    if ctx.achievements:
        first = to_bullet_case(ctx.achievements[0])
        if first:
            if starts_with_action_verb(first):
                return f"{first}."
            return f"{opener} {first[0].lower() + first[1:]}."
    focus = _join(_focus_terms(ctx, 2))
    return f"{opener} measurable, repeatable outcomes in {focus} across multi-team, multi-market programmes."


def _summary_strength_sentence(ctx: ProfileContext) -> str:
    focus = _focus_terms(ctx, 3)
    primary = focus[0] if focus else "core delivery"
    secondary = focus[1] if len(focus) > 1 else "hands-on"
    return (
        f"Combines {primary} depth with {secondary} delivery, turning requirements into "
        "shipped outcomes, from discovery through to post-launch measurement."
    )


def _summary_target_sentence(ctx: ProfileContext) -> str:
    role = ctx.job_title.strip() or "senior"
    return (
        f"Now targeting {role} roles where measurable impact, clean execution and "
        "evidence-based decisions matter."
    )


def _summary_known_for_sentence(ctx: ProfileContext) -> str:
    focus = _focus_terms(ctx, 3)
    strengths = _join(focus[1:3] or focus[:1])
    return (
        f"Known for {strengths} and for turning ambiguous problems into measurable, "
        "prioritised plans."
    )



def generate_summary(req: SummaryRequest) -> str:
    """Build a 55-90 word professional summary without any LLM."""
    title = req.job_title.strip() or "Professional"
    industry = _industry(req)
    focus = _focus_terms(req, 3)
    label = SENIORITY_LABEL.get(req.seniority, "Results-driven")
    if _has_seniority_word(title):
        label = ""  # avoid "Senior Senior Data Analyst"

    opener = TONE_OPENERS.get(req.tone, TONE_OPENERS["professional"]).format(
        label=label,
        title=title,
        years=_years_phrase(req.years_experience),
        industry=industry,
        focus=_join(focus),
    )
    parts = [opener]

    if req.existing_text.strip():
        draft = normalize(req.existing_text)
        parts.append(draft if draft.endswith(".") else f"{draft}.")

    parts.append(_achievement_sentence(req))
    parts.append(_summary_strength_sentence(req))
    parts.append(_summary_known_for_sentence(req))
    parts.append(_summary_target_sentence(req))

    # "concise" drops the closing target sentence so it stays shorter than the default.
    text = " ".join(parts[:4]) if req.tone == "concise" else " ".join(parts)
    return normalize(text).strip()


def generate_bullets(req: BulletsRequest) -> list[str]:
    """Produce achievement-first bullets, cycling recruiter verbs deterministically.

    The caller's skills (for a tailored CV: the advert's own tools) come first
    so bullets talk about Spark/Kafka/SQL *for that job*; the role-ontology
    pool fills the remaining slots.
    """
    count = max(2, min(req.count, 8))
    scope: list[str] = []
    for skill in [*req.skills, *ROLE_SKILLS_POOL(req)]:
        cleaned = skill.strip()
        if cleaned and cleaned.lower() not in {s.lower() for s in scope}:
            scope.append(cleaned)
    title = (req.role or req.job_title or "the role").strip()
    bullets: list[str] = []

    for raw in req.achievements:
        cleaned = to_bullet_case(raw)
        if cleaned:
            bullets.append(f"{cleaned}.")

    for index in range(len(bullets), count):
        verb = VERB_CYCLE[index % len(VERB_CYCLE)]
        skill_a = scope[index % len(scope)]
        skill_b = scope[(index + 1) % len(scope)] if len(scope) > 1 else scope[0]
        templates = [
            f"{verb} {skill_a} and {skill_b} workstreams for {title} initiatives, "
            f"improving [key metric] by [X%].",
            f"{verb} {skill_a} improvements adopted by [N] teams, cutting [process] "
            f"time by [X%].",
            f"{verb} {skill_b} delivery across [N] concurrent projects for a "
            f"[team size]-person organisation.",
            f"{verb} reporting on {skill_a} that informed [decision] and reduced "
            f"[cost/metric] by [X%].",
        ]
        bullets.append(templates[index % len(templates)])

    return bullets[:count]


def suggest_skills(req: SkillsRequest) -> list[str]:
    limit = max(4, min(req.limit, 24))
    existing = {s.strip().lower() for s in req.existing_skills if s.strip()}
    pool = ROLE_SKILLS_POOL(req)

    from ai.skills import ROLE_SKILLS

    secondary = ROLE_SKILLS["data" if family_for_role(req.job_title) != "data" else "product"]
    ranked: list[str] = []
    for skill in pool + secondary:
        if skill.lower() in existing or skill in ranked:
            continue
        ranked.append(skill)

    for skill in req.skills:
        cleaned = skill.strip()
        if cleaned and cleaned.lower() not in existing and cleaned not in ranked:
            ranked.insert(0, cleaned)

    return ranked[:limit]


def generate_cover_letter(req: CoverLetterRequest) -> str:
    """Four-paragraph cover letter (200-320 words) built from the profile context."""
    title = req.job_title.strip() or "the advertised role"
    company = req.company.strip() or "your company"
    industry = _industry(req)
    years = _years_phrase(req.years_experience)
    label = SENIORITY_LABEL.get(req.seniority, "Experienced")
    focus = _join(_focus_terms(req, 3))
    greeting = (
        f"Dear {req.hiring_manager.strip()}," if req.hiring_manager.strip()
        else "Dear Hiring Manager,"
    )

    proof_points = [to_bullet_case(a) for a in (req.highlights or req.achievements) if a.strip()]
    if not proof_points:
        proof_points = [
            f"{years} across {industry}, with hands-on ownership of {focus}"
        ]

    jd_keywords = extract_keywords(req.job_description, limit=6) if req.job_description else []
    if jd_keywords:
        keyword_line = (
            f"The advert emphasises {_join(jd_keywords[:3])}, which is precisely the work "
            "I do day to day rather than something I would need to learn."
        )
    else:
        keyword_line = (
            f"My background lines up closely with the requirements you listed for {title}."
        )

    paragraphs = [
        greeting,
        (
            f"I am applying for the {title} position at {company}. {label} professional with "
            f"{years}, I have spent my career turning {industry} problems into delivered "
            "outcomes, and I would like to bring that same focus to your team. I ship work "
            "end to end: discovery, build, measurement, and the follow-up that keeps it alive."
        ),
        " ".join([f"- {point}." for point in proof_points[:3]]) + " " + keyword_line,
        (
            f"What attracts me to {company} specifically is the chance to apply "
            f"{_join(_focus_terms(req, 2))} to problems at your scale, with a team that "
            "measures results rather than activity. I work best where ownership is explicit, "
            "feedback is direct and the roadmap is grounded in evidence. I would rather own "
            "one area deeply than spread thin across ten of them."
        ),
        (
            f"I would welcome the chance to talk through how these results would translate to "
            f"{company}'s roadmap. My CV sets out further detail on each of the outcomes above, "
            "and I am happy to walk through any of them. Thank you for your time and "
            "consideration - I am available for an interview at your convenience.\n\n"
            "Sincerely,\n[Your name]"
        ),
    ]
    return "\n\n".join(paragraphs)


def rewrite_text(text: str, instruction: str = "make it more impactful") -> str:
    """Light-touch rewrite: de-cliché, tighten and re-verb the content."""
    from ai.lexicon import CLICHES

    cleaned = normalize(text)
    for cliche in CLICHES:
        cleaned = cleaned.replace(cliche, "")
        cleaned = cleaned.replace(cliche.title(), "")
    for pronoun in ("I ", "my ", "We ", "our "):
        cleaned = cleaned.replace(pronoun, "")

    parts = [to_bullet_case(p) for p in cleaned.split(". ") if p.strip()]
    if not parts:
        return normalize(text)

    verbs = VERB_CYCLE
    rebuilt = []
    for index, sentence in enumerate(parts):
        if sentence and not sentence[0].isupper():
            sentence = sentence[0].upper() + sentence[1:]
        if not sentence.split(" ")[0].endswith(("ed", "ing")):
            sentence = f"{verbs[index % len(verbs)]} {sentence[0].lower() + sentence[1:]}"
        rebuilt.append(sentence.rstrip(".") + ".")

    prefix = f"{instruction.capitalize()}: " if instruction else ""
    return prefix + " ".join(rebuilt)


def draft_resume(req: DraftResumeRequest) -> Resume:
    """Turn a one-line brief into an editable CV skeleton."""
    brief = normalize(req.prompt)
    keywords = extract_keywords(brief, limit=8)
    title = (brief.split(" for ")[0].strip()[:70] or "Professional").title()
    role = keywords[0].title() if keywords else title

    ctx = ProfileContext(
        job_title=role,
        skills=[k.title() for k in keywords[:6]],
        locale=req.locale,
        language=LOCALE_NAMES.get(req.locale, "English"),
    )

    bullets = generate_bullets(BulletsRequest(**ctx.model_dump(), role=role, count=4))
    skills = suggest_skills(SkillsRequest(**ctx.model_dump(), existing_skills=[], limit=10))

    return Resume(
        title=title,
        template=req.template,
        locale=req.locale,
        personal=PersonalInfo(headline=f"{role} — drafted from your brief"),
        summary=generate_summary(SummaryRequest(**ctx.model_dump(), existing_text="")),
        experience=[
            ExperienceItem(
                role=role,
                company="[Company]",
                location="[Location]",
                start_date="[YYYY-MM]",
                end_date="Present",
                current=True,
                bullets=bullets,
            )
        ],
        skills=[SkillGroup(name=translate_heading(req.locale, "Skills"), skills=skills)],
        languages=[LanguageItem(name="[Language]", level="[Level]")],
    )


