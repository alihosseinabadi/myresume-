"""Prompt templates for cover letters, ATS re-scoring and full CV drafting."""

from __future__ import annotations

import json

from ai.prompts import RECRUITER_SYSTEM, _profile_block
from models import CoverLetterRequest


def cover_letter_messages(req: CoverLetterRequest) -> list[dict[str, str]]:
    schema = '{"letter": "full letter text with \\n between paragraphs"}'
    user = (
        f"{_profile_block(req)}\n"
        f"Company: {req.company or 'not specified'}\n"
        f"Hiring manager: {req.hiring_manager or 'unknown'}\n"
        f"Job description excerpt:\n{(req.job_description or 'not provided')[:2500]}\n\n"
        "Write a cover letter of 220-320 words in exactly four paragraphs: "
        "(1) the role applied for and one line of genuine motivation tied to the "
        "company, (2) two proof points mapping their experience to the job ad "
        "requirements, (3) why this company specifically, (4) a confident closing "
        "with a call to action. Use 'Dear Hiring Manager,' when the name is unknown. "
        "No markdown, no bullet lists, no placeholders.\n"
        f"Return JSON exactly: {schema}"
    )
    return [
        {"role": "system", "content": RECRUITER_SYSTEM},
        {"role": "user", "content": user},
    ]


def ats_suggestions_messages(score: int, missing: list[str], job_title: str) -> list[dict[str, str]]:
    schema = '{"suggestions": ["actionable fix 1", "actionable fix 2"]}'
    user = (
        f"An ATS rule engine scored this CV {score}/100 for the role "
        f"'{job_title or 'unspecified'}'.\n"
        f"Keywords present in the job ad but missing from the CV: {', '.join(missing) or 'none'}\n\n"
        "Give 3-6 short, concrete fixes ordered by impact. Each fix: one sentence, "
        "imperative, referencing the CV section to change.\n"
        f"Return JSON exactly: {schema}"
    )
    return [
        {"role": "system", "content": RECRUITER_SYSTEM},
        {"role": "user", "content": user},
    ]


def draft_resume_messages(prompt: str, locale: str) -> list[dict[str, str]]:
    schema = json.dumps(
        {
            "title": "string",
            "personal": {"full_name": "", "headline": "", "location": "", "email": "", "phone": ""},
            "summary": "string",
            "experience": [
                {
                    "role": "", "company": "", "location": "",
                    "start_date": "YYYY-MM", "end_date": "YYYY-MM or Present",
                    "bullets": ["string"],
                }
            ],
            "education": [{"degree": "", "school": "", "start_date": "", "end_date": ""}],
            "skills": [{"name": "Skills", "skills": ["string"]}],
            "languages": [{"name": "", "level": ""}],
        },
        ensure_ascii=False,
    )
    user = (
        f"Build a realistic, ATS-friendly CV skeleton in locale {locale} from this "
        f"request:\n{prompt}\n\n"
        "Use clearly generic but plausible content — the user will edit it. Keep "
        "contact details as empty strings rather than inventing personal data. "
        "Use markdown-free plain text values.\n"
        f"Return JSON exactly matching this shape: {schema}"
    )
    return [
        {"role": "system", "content": RECRUITER_SYSTEM},
        {"role": "user", "content": user},
    ]


def chat_messages(text: str, ctx: dict | None = None) -> list[dict[str, str]]:
    """Freeform CV assistant: answer questions about the user's CV text."""
    context = f"\nUser CV excerpt:\n{text[:3000]}" if text else ""
    user = (
        "Answer the user's CV question as a recruiter would: direct, specific, "
        "under 150 words, no markdown.\n"
        f"Question: {(ctx or {}).get('question', '')}"
        f"{context}"
    )
    return [
        {"role": "system", "content": RECRUITER_SYSTEM},
        {"role": "user", "content": user},
    ]
