"""Resignation letters: written the way a good career coach would write them.

Short, warm, no drama, and it never invents a reason — if the candidate did not
give one, the letter simply does not mention it.
"""

from __future__ import annotations

from ai.runtime import OFFLINE_MODEL, llm_json, text_from
from models import ResignationRequest, ResignationResponse

RESIGNATION_SYSTEM = (
    "You are a career coach who writes short, professional resignation letters. "
    "They are warm, forward-looking and under 180 words. They never badmouth the "
    "employer, never invent a reason the candidate did not give, and they end with "
    "a concrete handover offer. Reply with valid JSON only."
)

CHECKLIST = [
    "Give at least the contractual notice period (often 4-12 weeks).",
    "Confirm your last working day in writing.",
    "Mention a handover plan and offer to help train your replacement.",
    "Ask for a reference and a final payslip, then keep the letter for your records.",
]


def _local_letter(req: ResignationRequest) -> str:
    name = req.full_name.strip() or "[Your name]"
    role = req.job_title.strip() or "[Your role]"
    company = req.company.strip() or "[Company]"
    greeting = (
        f"Dear {req.manager_name.strip()},"
        if req.manager_name.strip()
        else "Dear Hiring Manager,"
    )
    last_day = req.last_working_day.strip() or "[last working day]"

    thanks = (
        f" I am writing to let you know that I will be leaving {company} as a "
        f"{role.lower()}."
        if role and role != "[Your role]"
        else " I am writing to let you know that I will be leaving the company."
    )
    reason = f" {req.reason.strip()}" if req.reason.strip() else ""
    highlight = (
        f" Over my time here I am most proud of {req.highlight.strip()}."
        if req.highlight.strip()
        else ""
    )
    closing = (
        " I would like to support a smooth handover and am happy to train whoever "
        "takes this on."
        if req.keep_contact
        else " I wish the team every success for the future."
    )
    contact = (
        f"\n\nI am happy to be contacted on my personal details during the notice period.\n\n"
        "Kind regards,"
        if req.keep_contact
        else "\n\nKind regards,"
    )

    return (
        f"{greeting}{thanks}\n\n"
        f"My last working day will be {last_day}.{reason}{highlight}{closing}\n\n"
        f"Thank you for the opportunity and for your support over the years.{contact}\n{name}"
    )


def resignation_letter(req: ResignationRequest) -> ResignationResponse:
    """Return a professional resignation letter (AI when available, else template)."""
    data, provider, model, latency = llm_json(
        [
            {"role": "system", "content": RESIGNATION_SYSTEM},
            {
                "role": "user",
                "content": (
                    "Write the letter as JSON with a 'letter' key. Facts:\n"
                    f"- Candidate: {req.full_name or 'their name'}\n"
                    f"- Role: {req.job_title or 'their role'}\n"
                    f"- Company: {req.company or 'the company'}\n"
                    f"- Manager: {req.manager_name or 'unknown, address as Dear Hiring Manager'}\n"
                    f"- Last working day: {req.last_working_day or 'not given'}\n"
                    f"- Reason given: {req.reason or 'none given — do not invent one'}\n"
                    f"- Highlight to remember: {req.highlight or 'none given'}\n"
                    f"- Happy to hand over: {req.keep_contact}\n"
                    f"- Tone: {req.tone}\n"
                    "Keep it under 180 words."
                ),
            },
        ],
        "resignation",
        cache_payload=req.model_dump(),
    )

    letter = text_from(data, "letter", "text")
    if letter:
        return ResignationResponse(
            letter=letter, provider=provider or model, word_count=len(letter.split())
        )

    letter = _local_letter(req)
    return ResignationResponse(
        letter=letter,
        provider="local",
        fallback=True,
        word_count=len(letter.split()),
        checklist=CHECKLIST,
    )
