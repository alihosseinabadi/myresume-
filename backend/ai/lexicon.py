"""Static language data used by the offline (no-API-key) resume engine."""

from __future__ import annotations

ACTION_VERBS: dict[str, list[str]] = {
    "leadership": [
        "Led", "Directed", "Managed", "Owned", "Coordinated", "Mentored",
        "Supervised", "Championed", "Spearheaded",
    ],
    "delivery": [
        "Delivered", "Launched", "Shipped", "Implemented", "Rolled out",
        "Executed", "Deployed", "Introduced",
    ],
    "improvement": [
        "Improved", "Optimised", "Reduced", "Cut", "Increased", "Grew", "Streamlined",
        "Accelerated", "Scaled", "Simplified", "Doubled", "Tripled",
    ],
    "analysis": [
        "Analysed", "Modelled", "Forecasted", "Audited", "Benchmarked",
        "Identified", "Diagnosed", "Quantified",
    ],
    "building": [
        "Built", "Designed", "Developed", "Architected", "Engineered",
        "Prototyped", "Automated", "Integrated",
    ],
    "collaboration": [
        "Partnered", "Collaborated", "Liaised", "Aligned", "Facilitated",
        "Presented", "Negotiated", "Influenced",
    ],
}

ALL_VERBS: list[str] = [v for group in ACTION_VERBS.values() for v in group]

# Irregular past tenses that do not end in "-ed" but are still strong openers.
IRREGULAR_PAST: list[str] = [
    "led", "built", "ran", "drove", "won", "cut", "grew", "made", "held", "set",
    "met", "sold", "sought", "brought", "found", "kept", "began", "chose", "spent",
    "took", "gave", "sent", "put", "taught", "wrote", "spoke", "shrank", "swept",
    "rebuilt", "reduced", "oversaw", "reorganised", "reorganized", "mentored",
]

STOPWORDS: set[str] = {
    "a", "an", "the", "and", "or", "but", "if", "then", "than", "so", "as",
    "at", "by", "for", "from", "in", "into", "of", "on", "onto", "to", "with",
    "within", "without", "about", "across", "after", "before", "between",
    "during", "over", "under", "up", "down", "out", "off", "per", "via",
    "is", "are", "was", "were", "be", "been", "being", "am", "do", "does",
    "did", "doing", "have", "has", "had", "having", "will", "would", "shall",
    "should", "can", "could", "may", "might", "must", "we", "you", "they",
    "he", "she", "it", "i", "our", "your", "their", "his", "her", "its",
    "this", "that", "these", "those", "there", "here", "who", "whom", "which",
    "what", "when", "where", "why", "how", "all", "any", "both", "each",
    "few", "more", "most", "other", "some", "such", "no", "nor", "not",
    "only", "own", "same", "too", "very", "also", "well", "plus", "etc",
    "ability", "able", "based", "candidate", "candidates", "company",
    "day", "days", "develop", "ensure", "excellent", "experience", "experienced",
    "good", "great", "help", "high", "including", "join", "job", "knowledge",
    "like", "looking", "need", "new", "opportunity", "position",
    "preferred", "proven", "required", "requirement", "requirements", "role",
    "skills", "strong", "successful", "team", "teams", "using", "want", "work",
    "working", "years", "responsibilities", "duties", "ideal",
    "please", "apply", "salary", "benefits", "offer", "offers",
    # Cookie banners and footers ride along on every scraped advert.
    "cookies", "cookie", "consent", "banner",
    # Conversational filler and number words. "Senior Data Analyst wanted …
    # mentor two analysts" used to put "wanted" and "two" on the list of
    # keywords to add to your CV, which reads as nonsense to the person using it.
    "wanted", "wanting", "seeking", "seeks", "hiring", "hire",
    "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
}

# Words that make a CV bullet look like a job description instead of an achievement.
CLICHES: list[str] = [
    "responsible for",
    "duties included",
    "hard worker",
    "team player",
    "go-getter",
    "think outside the box",
    "detail-oriented",
    "self-starter",
    "hit the ground running",
]

FIRST_PERSON: list[str] = ["i ", "i'", "my ", "me ", "we ", "our "]
