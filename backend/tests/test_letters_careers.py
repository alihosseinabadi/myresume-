"""Resignation letters and career matching."""

from __future__ import annotations

import pytest

from models import (
    CareerMatchRequest,
    ResignationRequest,
    TailorRequest,
)


def test_resignation_letter_endpoint(client):
    response = client.post(
        "/api/ai/resignation",
        json=ResignationRequest(
            full_name="Alex Morgan",
            job_title="Data Analyst",
            company="Payflow",
            manager_name="Dana Reed",
            last_working_day="28 February 2026",
            highlight="building the self-serve reporting layer",
        ).model_dump(),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["fallback"] is True
    assert "Dear Dana Reed," in body["letter"]
    assert "Payflow" in body["letter"]
    assert "28 February 2026" in body["letter"]
    assert "self-serve reporting layer" in body["letter"]
    assert 80 <= body["word_count"] <= 260
    assert body["checklist"]


def test_resignation_never_invents_a_reason(client):
    body = client.post(
        "/api/ai/resignation",
        json=ResignationRequest(full_name="Sam", company="Globex").model_dump(),
    ).json()
    assert "reason" not in body["letter"].lower()
    assert "unfortunately" not in body["letter"].lower()


def test_resignation_with_a_reason_keeps_it(client):
    body = client.post(
        "/api/ai/resignation",
        json=ResignationRequest(
            full_name="Sam", company="Globex", reason="relocating to Lisbon"
        ).model_dump(),
    ).json()
    assert "relocating to Lisbon" in body["letter"]


def test_resignation_without_a_manager_uses_generic_greeting(client):
    body = client.post("/api/ai/resignation", json=ResignationRequest().model_dump()).json()
    assert body["letter"].startswith("Dear Hiring Manager,")
    assert "[Your name]" in body["letter"]


def test_career_match_returns_three_families_with_titles(client):
    body = client.post(
        "/api/careers/match",
        json=CareerMatchRequest(strength="data", years_experience=4).model_dump(),
    ).json()
    families = {role["family"] for role in body["roles"]}
    assert len(families) == 3
    assert len(body["roles"]) == 6  # two example titles per family
    assert all({"family", "field", "title", "why"} <= set(role) for role in body["roles"])
    assert body["skills"]
    assert "analytics" in body["note"].lower()


def test_career_match_follows_interests(client):
    body = client.post(
        "/api/careers/match",
        json=CareerMatchRequest(
            strength="data", interests="I love SQL, dashboards and forecasting"
        ).model_dump(),
    ).json()
    assert body["roles"][0]["family"] == "data"
    assert "signal" in body["roles"][0]["why"]


def test_career_match_applies_seniority(client):
    junior = client.post(
        "/api/careers/match",
        json=CareerMatchRequest(strength="people", seniority="junior").model_dump(),
    ).json()
    senior = client.post(
        "/api/careers/match",
        json=CareerMatchRequest(strength="people", seniority="senior").model_dump(),
    ).json()
    assert junior["roles"][0]["title"].startswith(("Junior", "Associate", "I"))
    assert senior["roles"][0]["title"].startswith(("Senior", ""))


def test_career_match_people_strength_suggests_people_families(client):
    body = client.post(
        "/api/careers/match", json=CareerMatchRequest(strength="people").model_dump()
    ).json()
    assert body["roles"][0]["family"] in {"support", "sales", "healthcare", "education"}


def test_tailor_still_works_after_new_routes(client):
    body = client.post(
        "/api/jobs/tailor",
        json=TailorRequest(job_title="Data Analyst", job_description="SQL dbt dashboards").model_dump(),
    ).json()
    assert body["resume"]["summary"]
