"""Offline engine tests: professional summary generation."""

from __future__ import annotations

from ai import local_engine
from ai.keywords import word_count
from models import SummaryRequest


def test_summary_endpoint_uses_offline_engine(client, summary_request):
    body = client.post("/api/ai/summary", json=summary_request.model_dump()).json()
    assert body["fallback"] is True
    assert body["provider"] == "local"
    assert 30 <= word_count(body["text"]) <= 130
    assert "of experience of experience" not in body["text"]
    assert "Data Analyst" in body["text"]
    assert body["text"].count(".") >= 3


def test_summary_is_deterministic(summary_request):
    first = local_engine.generate_summary(summary_request)
    second = local_engine.generate_summary(summary_request)
    assert first == second


def test_summary_respects_tone(summary_request):
    baseline = local_engine.generate_summary(summary_request)
    concise = local_engine.generate_summary(summary_request.model_copy(update={"tone": "concise"}))
    executive = local_engine.generate_summary(summary_request.model_copy(update={"tone": "executive"}))
    assert concise != executive
    assert "leadership level" in executive.lower()
    assert word_count(concise) < word_count(baseline)


def test_summary_reuses_existing_draft(summary_request):
    with_draft = summary_request.model_copy(update={"existing_text": "Analyst focused on pricing."})
    assert "pricing" in local_engine.generate_summary(with_draft).lower()


def test_summary_without_skills_uses_role_ontology():
    text = local_engine.generate_summary(
        SummaryRequest(job_title="registered nurse", years_experience=0)
    )
    assert "nurse" in text.lower()
    assert "project exposure" in text.lower()
    assert "patient care" in text.lower()


def test_summary_handles_empty_profile():
    text = local_engine.generate_summary(SummaryRequest())
    assert len(text) > 60
    assert "Professional" in text


def test_summary_years_phrasing():
    one = local_engine.generate_summary(SummaryRequest(job_title="Analyst", years_experience=1))
    many = local_engine.generate_summary(SummaryRequest(job_title="Analyst", years_experience=9))
    assert "1 year of experience" in one
    assert "9+ years of experience" in many


def test_summary_hits_product_word_target(summary_request):
    """The marketing promise is a 55-90 word summary; allow a small margin."""
    for tone in ("professional", "confident", "friendly", "executive"):
        text = local_engine.generate_summary(summary_request.model_copy(update={"tone": tone}))
        assert 45 <= word_count(text) <= 110, f"{tone}: {word_count(text)} words"
