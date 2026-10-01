"""Career matching: point a candidate at roles from the skill ontology.

No LLM needed — the answer comes from the same family/role data the CV writer
uses, so it is instant, deterministic and free.
"""

from __future__ import annotations

from ai.keywords import extract_keywords
from ai.skills import ROLE_SKILLS, family_label
from models import CareerMatchRequest, CareerMatchResponse

# Which role families suit each self-described strength, best first.
STRENGTH_ROLES: dict[str, list[str]] = {
    "ideas": ["product", "design", "marketing", "software"],
    "data": ["data", "finance", "software", "product"],
    "people": ["support", "sales", "healthcare", "education"],
    "operations": ["operations", "supply", "project", "finance"],
}

# Friendly titles per family, with the family label for context.
FAMILY_TITLES: dict[str, list[str]] = {
    "software": ["Backend Engineer", "Full-stack Engineer", "Platform Engineer"],
    "data": ["Data Analyst", "Analytics Engineer", "Data Scientist"],
    "product": ["Product Manager", "Product Owner", "Growth Lead"],
    "marketing": ["Growth Marketer", "Content Strategist", "Lifecycle Manager"],
    "sales": ["Account Executive", "Sales Development Rep", "Customer Success Lead"],
    "design": ["Product Designer", "UX Researcher", "Design Systems Designer"],
    "finance": ["Financial Analyst", "FP&A Manager", "Controller"],
    "operations": ["Operations Manager", "Programme Manager", "Supply Chain Analyst"],
    "support": ["Customer Success Manager", "Support Lead", "Onboarding Specialist"],
    "healthcare": ["Registered Nurse", "Clinical Coordinator", "Patient Advocate"],
    "education": ["Teacher", "Curriculum Designer", "Learning Specialist"],
}

# Words in the interests field that nudge one family above another.
INTEREST_HINTS: dict[str, list[str]] = {
    "software": ["code", "developer", "engineer", "api", "backend", "frontend", "app"],
    "data": ["data", "sql", "analytics", "metrics", "statistics", "dashboard", "forecast"],
    "product": ["product", "roadmap", "discovery", "prioritis", "prioritiz", "strategy"],
    "marketing": ["marketing", "seo", "brand", "content", "campaign", "social"],
    "sales": ["sales", "account", "closing", "relationship", "revenue"],
    "design": ["design", "ux", "ui", "figma", "research", "visual"],
    "finance": ["finance", "budget", "forecast", "audit", "accounting", "fp&a"],
    "operations": ["operations", "process", "logistics", "vendor", "plan"],
    "support": ["support", "customer", "help", "onboarding", "service"],
    "healthcare": ["care", "patient", "clinic", "nurse", "health"],
    "education": ["teach", "school", "curriculum", "student", "learn"],
}

LEVEL_SUFFIX = {
    "intern": ["Intern", "Placement Student", "Graduate Trainee"],
    "junior": ["Junior", "Associate", "I"],
    "mid": ["", ""],
    "senior": ["Senior ", ""],
    "lead": ["Lead ", "Principal "],
    "manager": ["Manager", "Head of "],
    "director": ["Director", "Head of "],
    "executive": ["Chief", "VP "],
}


def _interest_boosts(interests: str) -> dict[str, int]:
    words = extract_keywords(interests, limit=20)
    boosts: dict[str, int] = {}
    for family, hints in INTEREST_HINTS.items():
        hits = sum(1 for word in words if any(hint in word for hint in hints))
        if hits:
            boosts[family] = hits
    return boosts


def match_careers(req: CareerMatchRequest) -> CareerMatchResponse:
    """Recommend role families, ordered by strength then stated interests.

    The sort is stable, so families with equal boost keep the order implied by
    the chosen strength — an unrelated interest can never outrank it by accident.
    """
    boosts = _interest_boosts(req.interests)
    order = list(STRENGTH_ROLES.get(req.strength, STRENGTH_ROLES["data"]))
    for family in boosts:
        if family not in order:
            order.append(family)
    order.sort(key=lambda family: -boosts.get(family, 0))

    prefixes = LEVEL_SUFFIX.get(req.seniority, ["", ""])
    roles: list[dict] = []
    for family in order[:3]:
        titles = FAMILY_TITLES.get(family, ["Professional"])
        for index, title in enumerate(titles[:2]):
            prefix = prefixes[index] if index < len(prefixes) else ""
            roles.append(
                {
                    "family": family,
                    "field": family_label(family),
                    "title": f"{prefix}{title}",
                    "why": _why(family, boosts.get(family, 0), req),
                }
            )

    top_family = order[0]
    return CareerMatchResponse(
        roles=roles,
        skills=ROLE_SKILLS.get(top_family, ROLE_SKILLS["operations"])[:8],
        note=(
            f"Based on what you told us, {family_label(top_family)} roles fit best. "
            "Pick one, paste a real advert, and we will write the CV for it."
        ),
    )


def _why(family: str, interest_hits: int, req: CareerMatchRequest) -> str:
    if interest_hits:
        return f"Matches the '{req.interests.strip()}' work you mentioned ({interest_hits} signal(s))."
    if req.years_experience >= 8:
        return f"Senior level fits your {req.years_experience} years of experience."
    return f"Strong overlap with a {family_label(family)} skill set."
