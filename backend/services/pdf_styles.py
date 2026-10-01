"""Font registration and paragraph styles for PDF export."""

from __future__ import annotations

import os

import reportlab
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from models import Resume

FONT_FILES = {
    "ResumeSans": "DejaVuSans.ttf",
    "ResumeSans-Bold": "DejaVuSans-Bold.ttf",
    "ResumeSerif": "DejaVuSerif.ttf",
}

_REGISTERED = False
SANS, SANS_BOLD, SERIF, MONO = "Helvetica", "Helvetica-Bold", "Times-Roman", "Courier"


def register_dejavu() -> bool:
    """Register ReportLab's bundled DejaVu fonts (Latin + Greek + Cyrillic)."""
    global _REGISTERED, SANS, SANS_BOLD, SERIF
    if _REGISTERED:
        return True
    fonts_dir = os.path.join(os.path.dirname(reportlab.__file__), "fonts")
    try:
        for name, filename in FONT_FILES.items():
            pdfmetrics.registerFont(TTFont(name, os.path.join(fonts_dir, filename)))
    except Exception:  # noqa: BLE001 - fall back to the base-14 fonts
        return False
    SANS, SANS_BOLD, SERIF = "ResumeSans", "ResumeSans-Bold", "ResumeSerif"
    _REGISTERED = True
    return True


def hex_to_color(value: str) -> colors.Color:
    try:
        return colors.HexColor(value if value.startswith("#") else f"#{value}")
    except Exception:  # noqa: BLE001 - any invalid colour falls back to teal
        return colors.HexColor("#0F766E")


def font_family(resume: Resume) -> tuple[str, str]:
    if resume.font == "mono":
        return MONO, "Courier-Bold"
    if resume.font == "serif":
        register_dejavu()
        return SERIF, SANS_BOLD
    register_dejavu()
    return SANS, SANS_BOLD


def build_styles(resume: Resume, accent: colors.Color) -> dict[str, ParagraphStyle]:
    regular, bold = font_family(resume)
    return {
        "name": ParagraphStyle(
            "ResumeName", fontName=bold, fontSize=19, leading=23,
            textColor=accent, alignment=TA_CENTER, spaceAfter=2,
        ),
        "headline": ParagraphStyle(
            "ResumeHeadline", fontName=regular, fontSize=11, leading=15,
            alignment=TA_CENTER, textColor=colors.HexColor("#374151"),
        ),
        "contact": ParagraphStyle(
            "ResumeContact", fontName=regular, fontSize=9, leading=13,
            alignment=TA_CENTER, textColor=colors.HexColor("#6B7280"),
        ),
        "section": ParagraphStyle(
            "ResumeSection", fontName=bold, fontSize=11, leading=14,
            textColor=accent, spaceBefore=9, spaceAfter=3,
        ),
        "body": ParagraphStyle(
            "ResumeBody", fontName=regular, fontSize=9.5, leading=13.5,
            textColor=colors.HexColor("#1F2937"),
        ),
        "role": ParagraphStyle(
            "ResumeRole", fontName=bold, fontSize=10, leading=13,
            textColor=colors.HexColor("#111827"),
        ),
        "meta": ParagraphStyle(
            "ResumeMeta", fontName=regular, fontSize=8.5, leading=12,
            textColor=colors.HexColor("#6B7280"),
        ),
        "bullet": ParagraphStyle(
            "ResumeBullet", fontName=regular, fontSize=9.5, leading=13.5,
            leftIndent=10, bulletIndent=0, spaceAfter=1.5,
            textColor=colors.HexColor("#1F2937"),
        ),
    }
