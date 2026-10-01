"""The 11 recruiter-approved template catalog served to the builder and landing page."""

from __future__ import annotations

TEMPLATES: list[dict] = [
    {"id": "athens", "name": "Athens", "accent": "#0F766E", "tagline": "Recruiter-approved classic", "layout": "single", "ats_ready": True},
    {"id": "berlin", "name": "Berlin", "accent": "#1D4ED8", "tagline": "Two-column for tech roles", "layout": "two-column", "ats_ready": True},
    {"id": "cairo", "name": "Cairo", "accent": "#B45309", "tagline": "Bold headline band", "layout": "sidebar", "ats_ready": True},
    {"id": "dublin", "name": "Dublin", "accent": "#065F46", "tagline": "ATS-first plain layout", "layout": "single", "ats_ready": True},
    {"id": "geneva", "name": "Geneva", "accent": "#7C3AED", "tagline": "Executive serif", "layout": "single", "ats_ready": True},
    {"id": "helsinki", "name": "Helsinki", "accent": "#0369A1", "tagline": "Minimal Nordic", "layout": "two-column", "ats_ready": True},
    {"id": "istanbul", "name": "Istanbul", "accent": "#BE123C", "tagline": "Creative with skill bars", "layout": "sidebar", "ats_ready": True},
    {"id": "lisbon", "name": "Lisbon", "accent": "#0E7490", "tagline": "Warm modern grid", "layout": "two-column", "ats_ready": True},
    {"id": "munich", "name": "Munich", "accent": "#334155", "tagline": "Engineering precision", "layout": "single", "ats_ready": True},
    {"id": "oslo", "name": "Oslo", "accent": "#4D7C0F", "tagline": "Clean student layout", "layout": "single", "ats_ready": True},
    {"id": "prague", "name": "Prague", "accent": "#9333EA", "tagline": "Portfolio-first", "layout": "sidebar", "ats_ready": True},
]


def template_by_id(template_id: str) -> dict | None:
    return next((t for t in TEMPLATES if t["id"] == template_id), None)
