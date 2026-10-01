"""Render a resume into a minimal, valid .docx (OOXML) using only the stdlib.

Deliberately dependency-free: python-docx is not required to ship Word export.
The archive follows the ECMA-376 minimum part set that Word, Google Docs and
LibreOffice all accept.
"""

from __future__ import annotations

from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

from ai.translations import translate_heading
from models import Resume
from services.docx_parts import CONTENT_TYPES, DOC_RELS, RELS, STYLES


def _esc(text: str) -> str:
    return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _para(text: str, style: str = "") -> str:
    style_xml = f'<w:pStyle w:val="{style}"/>' if style else ""
    return (
        f"<w:p><w:pPr>{style_xml}</w:pPr>"
        f'<w:r><w:t xml:space="preserve">{_esc(text)}</w:t></w:r></w:p>'
    )


def _bullet(text: str) -> str:
    return _para(f"\u2022  {text}", "ListBullet")


def _date_range(start: str, end: str, current: bool = False) -> str:
    finish = "Present" if current or not end else end
    if start and finish:
        return f"{start} - {finish}"
    return start or finish


def resume_blocks(resume: Resume) -> list[str]:
    """The document body as a list of ``w:p`` XML strings (shared with PDF meta)."""
    heading = lambda key: translate_heading(resume.locale, key)  # noqa: E731
    blocks: list[str] = []
    personal = resume.personal

    if personal.full_name:
        blocks.append(_para(personal.full_name, "Heading1"))
    if personal.headline:
        blocks.append(_para(personal.headline))
    contact = " | ".join(
        part for part in [
            personal.email, personal.phone, personal.location,
            personal.website, personal.linkedin, personal.github,
        ] if part
    )
    if contact:
        blocks.append(_para(contact))

    if resume.summary:
        blocks.append(_para(heading("Summary"), "Heading2"))
        blocks.append(_para(resume.summary))

    if resume.experience:
        blocks.append(_para(heading("Experience"), "Heading2"))
        for item in resume.experience:
            header = " — ".join(p for p in [item.role, item.company] if p)
            if header:
                blocks.append(_para(header, "Heading2"))
            meta = " | ".join(
                p for p in [
                    item.location,
                    _date_range(item.start_date, item.end_date, item.current),
                ] if p
            )
            if meta:
                blocks.append(_para(meta))
            if item.description:
                blocks.append(_para(item.description))
            blocks.extend(_bullet(b) for b in item.bullets if b.strip())

    if resume.education:
        blocks.append(_para(heading("Education"), "Heading2"))
        for item in resume.education:
            header = " — ".join(p for p in [item.degree, item.school] if p)
            if header:
                blocks.append(_para(header, "Heading2"))
            meta = " | ".join(
                p for p in [item.location, _date_range(item.start_date, item.end_date)] if p
            )
            if meta:
                blocks.append(_para(meta))
            if item.description:
                blocks.append(_para(item.description))

    if resume.skills:
        blocks.append(_para(heading("Skills"), "Heading2"))
        for group in resume.skills:
            if group.skills:
                blocks.append(_bullet(f"{group.name}: {', '.join(group.skills)}"))

    if resume.projects:
        blocks.append(_para(heading("Projects"), "Heading2"))
        for item in resume.projects:
            label = item.name + (f" ({item.link})" if item.link else "")
            if label:
                blocks.append(_para(label, "Heading2"))
            if item.description:
                blocks.append(_para(item.description))
            blocks.extend(_bullet(b) for b in item.bullets if b.strip())

    if resume.certifications:
        blocks.append(_para(heading("Certifications"), "Heading2"))
        for item in resume.certifications:
            line = " — ".join(p for p in [item.name, item.issuer, item.date] if p)
            if line:
                blocks.append(_bullet(line))

    if resume.languages:
        blocks.append(_para(heading("Languages"), "Heading2"))
        line = ", ".join(
            f"{lang.name}{f' ({lang.level})' if lang.level else ''}"
            for lang in resume.languages if lang.name
        )
        if line:
            blocks.append(_para(line))

    for section in resume.custom_sections:
        if not section.title:
            continue
        blocks.append(_para(section.title, "Heading2"))
        if section.body:
            blocks.append(_para(section.body))
        blocks.extend(_bullet(b) for b in section.bullets if b.strip())

    return blocks


def render_docx(resume: Resume) -> bytes:
    """Return the .docx file bytes for ``resume``."""
    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body>"
        + "".join(resume_blocks(resume))
        + '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134"/></w:sectPr>'
        "</w:body></w:document>"
    )

    buffer = BytesIO()
    with ZipFile(buffer, "w", ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", CONTENT_TYPES)
        archive.writestr("_rels/.rels", RELS)
        archive.writestr("word/_rels/document.xml.rels", DOC_RELS)
        archive.writestr("word/styles.xml", STYLES)
        archive.writestr("word/document.xml", document)
    return buffer.getvalue()
