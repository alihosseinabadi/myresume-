"""Health, catalog and provider-discovery endpoints."""

from __future__ import annotations

import pytest


def test_root_lists_endpoints(client):
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["app"]
    assert body["templates"] == 11
    assert "/api/ai/summary" in body["endpoints"]
    assert "/api/export/pdf" in body["endpoints"]


def test_health_reports_offline_provider(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["ai_provider"] == "local"  # tests force AI_PROVIDER=local
    assert body["ai_ready"] is True
    assert len(body["providers"]) == 7


def test_providers_endpoint_marks_configured_state(client):
    body = client.get("/api/ai/providers").json()
    names = [p["name"] for p in body["providers"]]
    assert names == [
        "openrouter", "groq", "gemini", "mistral", "cerebras", "ollama", "local",
    ]
    offline = next(p for p in body["providers"] if p["name"] == "local")
    assert offline["configured"] is True
    assert body["offline_capable"] is True


def test_ollama_is_skipped_when_daemon_is_down(monkeypatch):
    """`auto` must not put ollama in the chain when localhost:11434 is not listening."""
    from ai import providers

    monkeypatch.setattr(providers.settings, "ai_provider", "auto")
    monkeypatch.setattr(providers, "ollama_available", lambda: False)
    assert [p.name for p in providers.resolve_chain()] == ["local"]

    monkeypatch.setattr(providers, "ollama_available", lambda: True)
    assert [p.name for p in providers.resolve_chain()] == ["ollama", "local"]
    assert providers.active_provider_name() == "ollama"


def test_explicit_provider_always_appends_offline_engine(monkeypatch):
    from ai import providers

    monkeypatch.setattr(providers.settings, "ai_provider", "groq")
    assert [p.name for p in providers.resolve_chain()] == ["groq", "local"]

    monkeypatch.setattr(providers.settings, "ai_provider", "gemini")
    assert [p.name for p in providers.resolve_chain()] == ["gemini", "local"]

    monkeypatch.setattr(providers.settings, "ai_provider", "local")
    assert [p.name for p in providers.resolve_chain()] == ["local"]


def test_templates_catalog(client):
    body = client.get("/api/templates").json()
    assert body["count"] == 11
    ids = [t["id"] for t in body["templates"]]
    assert "athens" in ids and "prague" in ids
    assert all(t["ats_ready"] for t in body["templates"])
    assert all(t["accent"].startswith("#") for t in body["templates"])


def test_sample_resume_is_populated(client):
    resume = client.get("/api/resumes/sample").json()
    assert resume["personal"]["full_name"] == "Alex Morgan"
    assert len(resume["experience"]) == 2
    assert len(resume["skills"]) >= 3
    assert "%" in resume["summary"] or "3%" in resume["summary"]


@pytest.mark.parametrize("locale", ["en", "de", "fa", "ja", "ru"])
def test_sample_resume_accepts_locales(client, locale):
    response = client.get("/api/resumes/sample", params={"locale": locale})
    assert response.status_code == 200
    assert response.json()["locale"] == locale
