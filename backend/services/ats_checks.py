"""The fifteen weighted ATS structural checks."""

from __future__ import annotations

from ai.keywords import has_number, normalize, starts_with_action_verb, word_count
from ai.lexicon import CLICHES
from models import AtsCheck, Resume


def all_bullets(resume: Resume) -> list[str]:
    bullets = [b for item in resume.experience for b in item.bullets if b and b.strip()]
    bullets += [b for item in resume.projects for b in item.bullets if b and b.strip()]
    bullets += [b for s in resume.custom_sections for b in s.bullets if b and b.strip()]
    return bullets


def all_skills(resume: Resume) -> list[str]:
    return [s for group in resume.skills for s in group.skills if s and s.strip()]


def run_checks(resume: Resume) -> list[AtsCheck]:
    """Evaluate every rule and return the checks in display order."""
    personal = resume.personal
    summary = normalize(resume.summary)
    bullets = all_bullets(resume)
    skills = all_skills(resume)
    prose = " ".join([summary] + bullets).lower()

    quantified = [b for b in bullets if has_number(b)]
    quantified_ratio = len(quantified) / len(bullets) if bullets else 0.0
    verb_first = [b for b in bullets if starts_with_action_verb(b)]
    verb_ratio = len(verb_first) / len(bullets) if bullets else 0.0
    cliche_hits = [c for c in CLICHES if c in prose]
    first_person = any(token in f" {prose} " for token in (" i ", " my ", " we ", " our "))
    summary_words = word_count(summary)
    total = len(bullets) or 1

    return [
        AtsCheck(
            id="email", label="Contact email present", weight=10,
            passed=bool(personal.email and "@" in personal.email),
            detail=personal.email or "No email set — ATS cannot route your application.",
        ),
        AtsCheck(
            id="phone", label="Phone number present", weight=6,
            passed=bool(personal.phone.strip()),
            detail=personal.phone or "Add a phone number including country code.",
        ),
        AtsCheck(
            id="location", label="Location present", weight=4,
            passed=bool(personal.location.strip()),
            detail=personal.location or "Recruiters filter by city/country — add your location.",
        ),
        AtsCheck(
            id="headline", label="Professional headline", weight=5,
            passed=bool(personal.headline.strip()),
            detail=personal.headline or "Add a headline matching the job title you target.",
        ),
        AtsCheck(
            id="summary_present", label="Summary written", weight=8,
            passed=summary_words >= 30,
            detail=f"{summary_words} words — aim for 55-90.",
        ),
        AtsCheck(
            id="summary_length", label="Summary length in range", weight=6,
            passed=30 <= summary_words <= 120,
            detail=f"{summary_words} words — keep between 30 and 120.",
        ),
        AtsCheck(
            id="experience", label="Experience section filled", weight=10,
            passed=any(item.role and item.company for item in resume.experience),
            detail=f"{len(resume.experience)} entries; each needs a role and a company.",
        ),
        AtsCheck(
            id="bullets", label="At least 3 achievement bullets", weight=8,
            passed=len(bullets) >= 3,
            detail=f"{len(bullets)} bullets found.",
        ),
        AtsCheck(
            id="quantified", label="Bullets contain numbers", weight=10,
            passed=quantified_ratio >= 0.4,
            detail=f"{len(quantified)}/{total} bullets quantified "
                   f"({int(quantified_ratio * 100)}%); target 40%+.",
        ),
        AtsCheck(
            id="action_verbs", label="Bullets start with action verbs", weight=8,
            passed=verb_ratio >= 0.6,
            detail=f"{len(verb_first)}/{total} start with a verb "
                   f"({int(verb_ratio * 100)}%); target 60%+.",
        ),
        AtsCheck(
            id="no_first_person", label="No first-person pronouns", weight=5,
            passed=not first_person,
            detail="Found I/my/we/our in the prose sections."
            if first_person else "Impersonal voice used throughout.",
        ),
        AtsCheck(
            id="no_cliches", label="No filler clichés", weight=5,
            passed=not cliche_hits,
            detail=("Remove: " + ", ".join(cliche_hits)) if cliche_hits
            else "No clichés detected.",
        ),
        AtsCheck(
            id="skills", label="Six or more skills listed", weight=7,
            passed=len(skills) >= 6,
            detail=f"{len(skills)} skills listed.",
        ),
        AtsCheck(
            id="education", label="Education section filled", weight=4,
            passed=bool(resume.education),
            detail=f"{len(resume.education)} entries.",
        ),
        AtsCheck(
            id="extras", label="Projects, certifications or languages", weight=4,
            passed=bool(resume.projects or resume.certifications or resume.languages),
            detail="Optional sections add credibility and extra ATS keywords.",
        ),
    ]
