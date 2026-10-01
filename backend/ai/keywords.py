"""Text utilities shared by the offline engine and the ATS rule engine."""

from __future__ import annotations

import re
from collections import Counter

from ai.lexicon import ALL_VERBS, IRREGULAR_PAST, STOPWORDS
from ai.skills import ROLE_SKILLS, TECH_TERMS

TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9+#./\-]{1,}")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n+")
NUMBER_RE = re.compile(r"\d")

# Multi-word skills that must survive tokenisation (matched case-insensitively).
KNOWN_PHRASES: list[str] = sorted(
    {
        skill.lower()
        for group in ROLE_SKILLS.values()
        for skill in group
        if " " in skill
    }
    | {
        # Multi-word technologies (e.g. "delta lake", "data quality") promote to
        # phrase keywords so ATS matching and skill carry-over see them whole.
        term.lower()
        for term in TECH_TERMS
        if " " in term
    }
    | {
        "machine learning", "deep learning", "project management", "product management",
        "data analysis", "data engineering", "customer success", "supply chain",
        "unit testing", "design thinking", "user research", "stakeholder management",
        "financial modelling", "risk management", "quality assurance", "content marketing",
        "digital marketing", "business intelligence", "change management", "six sigma",
    }
)

_VERB_LOOKUP = {v.lower() for v in ALL_VERBS} | set(IRREGULAR_PAST)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def word_count(text: str) -> int:
    return len(TOKEN_RE.findall(text or ""))


def has_number(text: str) -> bool:
    return bool(NUMBER_RE.search(text or ""))


def sentences(text: str) -> list[str]:
    return [s.strip() for s in SENTENCE_SPLIT_RE.split(text or "") if s.strip()]


def tokenize(text: str) -> list[str]:
    return [
        t.lower().strip(".,;:()[]{}-")
        for t in TOKEN_RE.findall(text or "")
    ]


# Tokens that are clearly web furniture, never skills or ATS keywords.
_TLDS = ("com", "net", "org", "io", "ru", "рф", "info", "site", "online",
         "app", "dev", "ai", "co", "uk", "de", "fr", "gov", "edu")
_DOMAIN_RE = re.compile(r"^(?:[\w-]+\.)+(?:%s)$" % "|".join(_TLDS))

# Internal team codes such as "b2c-sql" or "team-42": a token carrying both
# a digit and a hyphen. Real skills with digits ("3d", "html5", "c++") have
# no hyphen, and real compounds ("etl/elt", "ci-cd") have no digit.
_TEAM_CODE_RE = re.compile(r"(?=.*\d)(?=.*-)[a-z0-9-]+")


def is_domain_token(token: str) -> bool:
    """True for leftover URLs/domains like ``www.sberbank.ru`` in scraped text."""
    return bool(_DOMAIN_RE.match((token or "").lower()))


def extract_keywords(text: str, limit: int = 25) -> list[str]:
    """Rank the significant terms of a job ad.

    Multi-word skill phrases are promoted above single tokens because ATS
    keyword matching is phrase-aware.
    """
    lowered = (text or "").lower()
    phrases = [p for p in KNOWN_PHRASES if p in lowered]

    counts = Counter(
        t for t in tokenize(lowered)
        if len(t) > 2 and t not in STOPWORDS and not t.isdigit()
        # Cookie banners and footer links leak into scraped adverts; a domain
        # is never a keyword, and hyphen artifacts ("quality-") are noise.
        and not is_domain_token(t)
        # Team codes like "b2c-sql" (letters, digits and a hyphen at once)
        # are internal jargon, not skills a candidate can add.
        and not _TEAM_CODE_RE.fullmatch(t)
    )
    single = [
        word for word, _ in sorted(counts.items(), key=lambda kv: (-kv[1], -len(kv[0])))
        if all(word not in phrase for phrase in phrases)
    ]

    ranked = phrases + single
    ranked_set = set(ranked)
    seen: set[str] = set()
    out: list[str] = []
    for term in ranked:
        if term in seen:
            continue
        # "analyst" and "analysts" are one keyword to a reader. Listing the
        # plural as well made the panel contradict itself — the same word under
        # "in your CV" and under "worth adding" at once.
        if term.endswith("s") and term[:-1] in ranked_set:
            continue
        seen.add(term)
        out.append(term)
        if len(out) >= limit:
            break
    return out


def starts_with_action_verb(sentence: str) -> bool:
    first = (normalize(sentence).split(" ")[0] if sentence else "").lower().rstrip(",.:;")
    if not first:
        return False
    if first in _VERB_LOOKUP:
        return True
    return first.endswith("ed") and len(first) > 4


def to_bullet_case(text: str) -> str:
    """Normalise a bullet: capitalise, strip trailing period, drop 'I'/'my'."""
    cleaned = normalize(text).lstrip("-•*+ \t")
    if not cleaned:
        return ""
    cleaned = re.sub(r"^(i|we)\s+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b(i|my|me)\b\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned[0].upper() + cleaned[1:] if cleaned else ""
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.rstrip(".").strip()
