"""Export endpoints: PDF, DOCX and plain text."""

from __future__ import annotations

import re

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from models import Resume
from services.export_docx import resume_blocks, render_docx
from services.export_pdf import render_pdf

router = APIRouter(prefix="/api/export", tags=["export"])

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def safe_filename(resume: Resume, extension: str) -> str:
    """Build ``firstname-lastname-job-title.ext`` from the resume, safely."""
    parts = [resume.personal.full_name, resume.title]
    stem = "-".join(p.strip() for p in parts if p and p.strip())
    slug = re.sub(r"[^A-Za-z0-9]+", "-", stem).strip("-").lower()
    return f"{slug[:70]}.{extension}" if slug else f"resume.{extension}"


def _attachment(filename: str, media_type: str, payload: bytes) -> Response:
    return Response(
        content=payload,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(payload)),
        },
    )


@router.post("/pdf")
def export_pdf(resume: Resume) -> Response:
    """Render an ATS-safe A4 PDF."""
    payload = render_pdf(resume)
    if not payload.startswith(b"%PDF"):
        raise HTTPException(status_code=500, detail="PDF renderer produced an invalid file")
    return _attachment(safe_filename(resume, "pdf"), "application/pdf", payload)


@router.post("/docx")
def export_docx(resume: Resume) -> Response:
    """Render an editable Word document (dependency-free OOXML writer)."""
    payload = render_docx(resume)
    return _attachment(safe_filename(resume, "docx"), DOCX_MIME, payload)


@router.post("/txt")
def export_txt(resume: Resume) -> Response:
    """Plain-text dump — useful for pasting into application forms."""
    text = re.sub(r"<[^>]+>", "", "".join(resume_blocks(resume)))
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return _attachment(
        safe_filename(resume, "txt"), "text/plain; charset=utf-8", text.encode("utf-8")
    )
