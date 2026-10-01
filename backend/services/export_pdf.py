"""PDF export via ReportLab's Platypus engine.

Layout is deliberately single-column and machine-readable so the exported file
stays ATS-safe. Requires ``reportlab`` (already listed in requirements.txt).
"""

from __future__ import annotations

from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer

from ai.translations import translate_heading
from models import Resume
from services.pdf_styles import build_styles, hex_to_color


def date_range(start: str, end: str, current: bool = False) -> str:
    finish = "Present" if current or not end else end
    if start and finish:
        return f"{start} - {finish}"
    return start or finish


def build_flowables(
    resume: Resume,
    styles: dict[str, ParagraphStyle],
    accent,
) -> list:
    """Translate the resume model into Platypus flowables."""
    heading = lambda key: translate_heading(resume.locale, key)  # noqa: E731
    out: list = []
    personal = resume.personal

    def add(text: str, style: str, bullet: bool = False) -> None:
        if not (text or "").strip():
            return
        out.append(Paragraph(escape(text), styles[style], bulletText="•" if bullet else None))

    def section(title: str) -> None:
        add(title, "section")
        out.append(HRFlowable(width="100%", thickness=0.7, color=accent, spaceAfter=4))

    if personal.full_name:
        add(personal.full_name, "name")
    if personal.headline:
        add(personal.headline, "headline")
    add(
        " | ".join(
            part for part in [
                personal.email, personal.phone, personal.location,
                personal.website, personal.linkedin, personal.github,
            ] if part
        ),
        "contact",
    )

    if resume.summary:
        section(heading("Summary"))
        add(resume.summary, "body")

    if resume.experience:
        section(heading("Experience"))
        for item in resume.experience:
            add(" — ".join(p for p in [item.role, item.company] if p), "role")
            add(
                " | ".join(
                    p for p in [
                        item.location,
                        date_range(item.start_date, item.end_date, item.current),
                    ] if p
                ),
                "meta",
            )
            add(item.description, "body")
            for bullet in item.bullets:
                add(bullet, "bullet", bullet=True)
            out.append(Spacer(1, 4))

    if resume.education:
        section(heading("Education"))
        for item in resume.education:
            add(" — ".join(p for p in [item.degree, item.school] if p), "role")
            add(
                " | ".join(
                    p for p in [item.location, date_range(item.start_date, item.end_date)] if p
                ),
                "meta",
            )
            add(item.description, "body")
        out.append(Spacer(1, 4))

    if resume.skills:
        section(heading("Skills"))
        for group in resume.skills:
            if group.skills:
                add(f"{group.name}: {', '.join(group.skills)}", "body")

    if resume.projects:
        section(heading("Projects"))
        for item in resume.projects:
            add(item.name + (f" ({item.link})" if item.link else ""), "role")
            add(item.description, "body")
            for bullet in item.bullets:
                add(bullet, "bullet", bullet=True)

    if resume.certifications:
        section(heading("Certifications"))
        for item in resume.certifications:
            add(" — ".join(p for p in [item.name, item.issuer, item.date] if p), "bullet", bullet=True)

    if resume.languages:
        section(heading("Languages"))
        add(
            ", ".join(
                f"{lang.name}{f' ({lang.level})' if lang.level else ''}"
                for lang in resume.languages if lang.name
            ),
            "body",
        )

    for custom in resume.custom_sections:
        if not custom.title:
            continue
        section(custom.title)
        add(custom.body, "body")
        for bullet in custom.bullets:
            add(bullet, "bullet", bullet=True)

    return out


def render_pdf(resume: Resume) -> bytes:
    """Return the PDF bytes for ``resume``."""
    accent = hex_to_color(resume.accent_color)
    styles = build_styles(resume, accent)
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title=(f"{resume.title} - {resume.personal.full_name}").strip(" -") or resume.title,
        author=resume.personal.full_name or resume.title,
        subject="Resume",
    )
    doc.build(build_flowables(resume, styles, accent))
    return buffer.getvalue()
