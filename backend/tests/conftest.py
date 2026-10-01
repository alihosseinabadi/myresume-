"""Shared pytest fixtures. Forces the offline engine so tests never hit the network."""

from __future__ import annotations

import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

# Must be set before `config` is imported anywhere.
os.environ["AI_PROVIDER"] = "local"
os.environ["DATABASE_PATH"] = str(BACKEND_DIR / "data" / "test.db")

import pytest  # noqa: E402

from ai.runtime import clear_cache  # noqa: E402
from db import init_db  # noqa: E402
from models import (  # noqa: E402
    ExperienceItem,
    PersonalInfo,
    Resume,
    SkillGroup,
    SummaryRequest,
)
from sample import sample_resume  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _database() -> None:
    init_db()


@pytest.fixture(autouse=True)
def _clear_ai_cache() -> None:
    clear_cache()
    yield
    clear_cache()


@pytest.fixture
def client():
    from fastapi.testclient import TestClient

    from main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample() -> Resume:
    return sample_resume()


@pytest.fixture
def minimal_resume() -> Resume:
    return Resume(
        title="Minimal",
        personal=PersonalInfo(full_name="Jane Doe", email="jane@example.com"),
    )


@pytest.fixture
def filled_resume() -> Resume:
    return Resume(
        title="Backend Engineer",
        personal=PersonalInfo(
            full_name="Sam Rivera",
            headline="Backend Engineer — Payments",
            email="sam@example.com",
            phone="+1 555 0100",
            location="Berlin, DE",
        ),
        summary=(
            "Backend Engineer with 7+ years building payment systems in Python and Go. "
            "Led the migration of a monolith to services handling 12M requests per day, "
            "cutting p99 latency by 43% and infrastructure cost by 28%. Mentored 5 engineers "
            "and now targeting platform engineering roles where reliability is the product."
        ),
        experience=[
            ExperienceItem(
                role="Senior Backend Engineer",
                company="Nordpay",
                location="Berlin, DE",
                start_date="2021-01",
                end_date="",
                current=True,
                bullets=[
                    "Led migration of a monolith into 9 services handling 12M requests per day, cutting p99 latency 43%.",
                    "Reduced infrastructure spend 28% by right-sizing Kubernetes workloads across 3 regions.",
                    "Built a payment reconciliation pipeline in Python that recovered EUR 310K of failed charges in year one.",
                ],
            )
        ],
        skills=[
            SkillGroup(name="Languages", skills=["Python", "Go", "SQL", "TypeScript", "Bash", "Docker"]),
            SkillGroup(name="Platform", skills=["Kubernetes", "Terraform", "Kafka", "PostgreSQL"]),
        ],
        languages=[],
    )


@pytest.fixture
def summary_request() -> SummaryRequest:
    return SummaryRequest(
        job_title="Data Analyst",
        industry="fintech",
        seniority="senior",
        years_experience=6,
        skills=["SQL", "Python", "dbt"],
        achievements=["Cut reporting time by 40% by rebuilding the finance dashboard"],
    )
