"""PDF / DOCX / TXT export tests."""

from __future__ import annotations

from io import BytesIO
from zipfile import ZipFile

from catalog import TEMPLATES
from routers.export import safe_filename
from services.export_docx import render_docx
from services.export_pdf import render_pdf


def test_pdf_bytes_are_a_valid_document(sample):
    payload = render_pdf(sample)
    assert payload.startswith(b"%PDF")
    assert b"%%EOF" in payload[-1024:]
    assert len(payload) > 3000


def test_pdf_handles_every_template(sample):
    for template in TEMPLATES:
        resume = sample.model_copy(deep=True)
        resume.template = template["id"]
        resume.accent_color = template["accent"]
        payload = render_pdf(resume)
        assert payload.startswith(b"%PDF")


def test_pdf_handles_serif_and_mono_fonts(sample):
    for font in ("sans", "serif", "mono"):
        resume = sample.model_copy(update={"font": font}, deep=True)
        assert render_pdf(resume).startswith(b"%PDF")


def test_pdf_handles_empty_resume(minimal_resume):
    payload = render_pdf(minimal_resume)
    assert payload.startswith(b"%PDF")


def test_pdf_handles_invalid_accent_colour(minimal_resume):
    resume = minimal_resume.model_copy(update={"accent_color": "not-a-colour"}, deep=True)
    assert render_pdf(resume).startswith(b"%PDF")


def test_docx_is_a_valid_ooxml_package(sample):
    payload = render_docx(sample)
    with ZipFile(BytesIO(payload)) as archive:
        names = set(archive.namelist())
        assert "[Content_Types].xml" in names
        assert "_rels/.rels" in names
        assert "word/document.xml" in names
        document = archive.read("word/document.xml").decode("utf-8")
    assert "Alex Morgan" in document
    assert "Payflow" in document
    assert "<w:tbl>" not in document  # ATS-safe: no tables, no columns


def test_docx_localises_headings(sample):
    resume = sample.model_copy(update={"locale": "de"}, deep=True)
    document = None
    with ZipFile(BytesIO(render_docx(resume))) as archive:
        document = archive.read("word/document.xml").decode("utf-8")
    assert "Berufserfahrung" in document
    assert "Ausbildung" in document


def test_docx_escapes_xml_specials(minimal_resume):
    resume = minimal_resume.model_copy(deep=True)
    resume.personal.full_name = "A & B <script>"
    with ZipFile(BytesIO(render_docx(resume))) as archive:
        document = archive.read("word/document.xml").decode("utf-8")
    assert "&amp;" in document
    assert "&lt;script&gt;" in document
    assert "<script>" not in document


def test_export_pdf_endpoint(client, sample):
    response = client.post("/api/export/pdf", json=sample.model_dump(mode="json"))
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert ".pdf" in response.headers["content-disposition"]
    assert response.content.startswith(b"%PDF")


def test_export_docx_endpoint(client, sample):
    response = client.post("/api/export/docx", json=sample.model_dump(mode="json"))
    assert response.status_code == 200
    assert "wordprocessingml" in response.headers["content-type"]
    assert ".docx" in response.headers["content-disposition"]
    with ZipFile(BytesIO(response.content)) as archive:
        assert "word/document.xml" in archive.namelist()


def test_export_txt_endpoint(client, sample):
    response = client.post("/api/export/txt", json=sample.model_dump(mode="json"))
    text = response.content.decode("utf-8")
    assert response.status_code == 200
    assert "Alex Morgan" in text
    assert "<w:p>" not in text
    assert "Summary" in text


def test_safe_filename_slug(sample):
    assert safe_filename(sample, "pdf") == "alex-morgan-senior-data-analyst-sample.pdf"


def test_safe_filename_falls_back_for_blank_names(minimal_resume):
    minimal_resume.personal.full_name = "***"
    minimal_resume.title = ""
    assert safe_filename(minimal_resume, "docx") == "resume.docx"
