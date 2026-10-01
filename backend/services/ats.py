"""ATS scoring: blends the structural checks with job-ad keyword coverage."""

from __future__ import annotations

from ai.keywords import extract_keywords
from models import AtsCheck, AtsScoreResponse, Resume
from services.ats_checks import all_bullets, all_skills, run_checks

KEYWORD_WEIGHT = 0.25  # rule weight is 1 - KEYWORD_WEIGHT when a JD is given


def keyword_coverage(resume: Resume, job_description: str) -> tuple[list[str], list[str], float]:
    """Return ``(matched, missing, ratio)`` for the job-ad keywords."""
    keywords = extract_keywords(job_description, limit=25)
    if not keywords:
        return [], [], 0.0

    haystack = " ".join([
        resume.summary,
        resume.personal.headline,
        resume.personal.full_name,
        " ".join(item.description for item in resume.experience),
        " ".join(all_bullets(resume)),
        " ".join(all_skills(resume)),
        " ".join(item.description for item in resume.education),
        " ".join(section.body for section in resume.custom_sections),
    ]).lower()

    matched = [k for k in keywords if k in haystack]
    missing = [k for k in keywords if k not in haystack]
    return matched, missing, len(matched) / len(keywords)


def local_suggestions(checks: list[AtsCheck], missing: list[str]) -> list[str]:
    """Deterministic, impact-ordered fixes derived from the failing checks."""
    fixes = [
        f"{check.label}: {check.detail}" if check.detail else check.label
        for check in sorted((c for c in checks if not c.passed), key=lambda c: -c.weight)
    ]
    if missing:
        fixes.append(
            "Add these job-ad keywords where they are genuinely true: "
            + ", ".join(missing[:8]) + "."
        )
    if not fixes:
        fixes.append("Nothing critical left — tailor the summary to each specific job ad.")
    return fixes


def grade_for(score: int) -> str:
    if score >= 90:
        return "A+"
    if score >= 80:
        return "A"
    if score >= 70:
        return "B"
    if score >= 60:
        return "C"
    if score >= 50:
        return "D"
    return "F"


def score_resume(resume: Resume, job_description: str = "") -> AtsScoreResponse:
    """Full rule-based scoring, with keyword blending when a JD is provided."""
    checks = run_checks(resume)
    total_weight = sum(c.weight for c in checks) or 1
    earned = sum(c.weight for c in checks if c.passed)
    rule_score = round(earned / total_weight * 100)

    matched, missing, ratio = keyword_coverage(resume, job_description)
    if job_description and matched:
        score = round((1 - KEYWORD_WEIGHT) * rule_score + KEYWORD_WEIGHT * ratio * 100)
    else:
        score = rule_score
    score = max(0, min(100, score))

    return AtsScoreResponse(
        score=score,
        grade=grade_for(score),
        matched_keywords=matched,
        missing_keywords=missing,
        checks=checks,
        suggestions=local_suggestions(checks, missing),
    )
