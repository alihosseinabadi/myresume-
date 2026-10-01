"""Offline engine tests: achievement bullets, skill suggestions and rewriting."""

from __future__ import annotations

from ai import local_engine
from ai.keywords import starts_with_action_verb
from models import BulletsRequest, SkillsRequest


def test_bullets_endpoint(client, summary_request):
    payload = BulletsRequest(**summary_request.model_dump(), role="Data Analyst", count=5)
    body = client.post("/api/ai/bullets", json=payload.model_dump()).json()
    assert body["fallback"] is True
    assert len(body["items"]) == 5
    assert all(item.endswith(".") for item in body["items"])
    assert any(starts_with_action_verb(item) for item in body["items"])


def test_bullets_clamp_count(summary_request):
    assert len(local_engine.generate_bullets(
        BulletsRequest(**summary_request.model_dump(), count=50)
    )) == 8
    assert len(local_engine.generate_bullets(
        BulletsRequest(**summary_request.model_dump(), count=0)
    )) == 2


def test_bullets_prefer_supplied_achievements(summary_request):
    payload = BulletsRequest(
        **summary_request.model_dump(exclude={"achievements"}),
        role="Data Analyst",
        count=2,
        achievements=["ran the migration to dbt", "trained 6 analysts"],
    )
    items = local_engine.generate_bullets(payload)
    assert items[0] == "Ran the migration to dbt."
    assert items[1] == "Trained 6 analysts."


def test_bullets_never_say_responsible_for(summary_request):
    payload = BulletsRequest(**summary_request.model_dump(), role="QA Engineer", count=8)
    joined = " ".join(local_engine.generate_bullets(payload)).lower()
    assert "responsible for" not in joined


def test_bullets_use_role_specific_skills(summary_request):
    payload = BulletsRequest(
        **summary_request.model_dump(exclude={"job_title", "achievements"}),
        job_title="registered nurse",
        role="Staff Nurse",
        count=4,
    )
    joined = " ".join(local_engine.generate_bullets(payload)).lower()
    assert "patient care" in joined or "clinical documentation" in joined


def test_bullets_lead_with_supplied_skills(summary_request):
    """A tailored CV's bullets must use the advert's own tools first.

    Passing Spark/Kafka for a data-engineering advert used to yield generic
    role-pool bullets (React, Node.js) because the pool ignored req.skills.
    """
    payload = BulletsRequest(
        **summary_request.model_dump(exclude={"job_title", "achievements", "skills"}),
        job_title="Data Engineer",
        role="Data Engineer",
        skills=["Spark", "Kafka"],
        count=4,
    )
    joined = " ".join(local_engine.generate_bullets(payload)).lower()
    assert "spark" in joined and "kafka" in joined


def test_skills_endpoint_excludes_existing(client, summary_request):
    payload = SkillsRequest(**summary_request.model_dump(), existing_skills=["SQL"], limit=6)
    body = client.post("/api/ai/skills", json=payload.model_dump()).json()
    assert len(body["items"]) == 6
    assert "SQL" not in body["items"]


def test_skills_endpoint_foregrounds_requested_skills(client, summary_request):
    payload = SkillsRequest(
        **summary_request.model_dump(exclude={"skills"}),
        existing_skills=[],
        limit=4,
        skills=["Snowflake"],
    )
    items = client.post("/api/ai/skills", json=payload.model_dump()).json()["items"]
    assert items[0] == "Snowflake"


def test_skills_react_to_job_title(summary_request):
    engineer = local_engine.suggest_skills(
        SkillsRequest(
            **summary_request.model_dump(exclude={"job_title"}),
            job_title="backend engineer",
            limit=8,
        )
    )
    assert "Docker" in engineer or "TypeScript" in engineer


def test_skills_limit_bounds(summary_request):
    assert len(local_engine.suggest_skills(
        SkillsRequest(**summary_request.model_dump(), limit=200)
    )) <= 24
    assert len(local_engine.suggest_skills(
        SkillsRequest(**summary_request.model_dump(), limit=1)
    )) >= 4


def test_rewrite_strips_cliches_and_pronouns(client):
    body = client.post(
        "/api/ai/rewrite",
        json={
            "text": "I was responsible for the reporting pipeline. My work helped the team.",
            "instruction": "tighten",
        },
    ).json()
    assert body["fallback"] is True
    assert "responsible for" not in body["text"].lower()
    assert " my " not in body["text"].lower()
    assert body["text"].lower().startswith("tighten:")


def test_rewrite_keeps_facts(client):
    body = client.post(
        "/api/ai/rewrite",
        json={"text": "Delivered 12 dashboards for finance in 2023", "instruction": ""},
    ).json()
    assert "12 dashboards" in body["text"]
    assert "2023" in body["text"]
