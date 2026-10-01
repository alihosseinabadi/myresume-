"""ATS rule engine tests: checks, keyword coverage, grades and the endpoint."""

from __future__ import annotations

from models import AtsScoreRequest, PersonalInfo, Resume
from services.ats import grade_for, keyword_coverage, score_resume
from services.ats_checks import run_checks


def test_check_weights_sum_to_one_hundred(filled_resume):
    checks = run_checks(filled_resume)
    assert sum(c.weight for c in checks) == 100
    assert len(checks) == 15


def test_strong_resume_scores_high(filled_resume):
    result = score_resume(filled_resume)
    assert result.score >= 85
    assert result.grade in {"A", "A+"}
    assert result.checks
    assert all(isinstance(c.passed, bool) for c in result.checks)


def test_empty_resume_scores_low_with_suggestions(minimal_resume):
    result = score_resume(minimal_resume)
    assert result.score <= 25
    assert result.grade == "F"
    assert any("phone" in s.lower() for s in result.suggestions)


def test_failing_checks_are_ordered_by_weight(minimal_resume):
    result = score_resume(minimal_resume)
    failed = [c for c in result.checks if not c.passed]
    weights = [c.weight for c in failed]
    assert min(weights) == 4  # phone is the lowest-weight failing check
    assert max(weights) == 10
    # suggestions are emitted in descending weight order
    assert result.suggestions[0].startswith("Experience section filled")


def test_checks_cover_every_expected_id(filled_resume):
    ids = {c.id for c in run_checks(filled_resume)}
    assert ids == {
        "email", "phone", "location", "headline", "summary_present", "summary_length",
        "experience", "bullets", "quantified", "action_verbs", "no_first_person",
        "no_cliches", "skills", "education", "extras",
    }


def test_first_person_and_cliches_are_penalised(minimal_resume):
    resume: Resume = minimal_resume.model_copy(deep=True)
    resume.summary = (
        "I am a hard worker and a team player who is responsible for delivery. "
        "My experience spans several teams and I am detail-oriented."
    )
    result = score_resume(resume)
    flags = {c.id: c.passed for c in result.checks}
    assert flags["no_first_person"] is False
    assert flags["no_cliches"] is False


def test_quantified_bullets_are_required(minimal_resume):
    resume: Resume = minimal_resume.model_copy(deep=True)
    from models import ExperienceItem

    resume.experience = [
        ExperienceItem(
            role="Analyst",
            company="Acme",
            bullets=["Managed reporting", "Owned dashboards", "Supported planning"],
        )
    ]
    flags = {c.id: c.passed for c in run_checks(resume)}
    assert flags["quantified"] is False
    assert flags["bullets"] is True


def test_keyword_coverage_reports_matches_and_gaps(filled_resume):
    jd = (
        "Looking for a backend engineer with Python, Go and Docker experience. "
        "You will work with Kafka and Rust on high throughput services."
    )
    matched, missing, ratio = keyword_coverage(filled_resume, jd)
    assert "python" in matched
    assert "rust" in missing or "kafka" in missing
    assert 0 < ratio < 1


def test_keyword_coverage_without_job_description(filled_resume):
    matched, missing, ratio = keyword_coverage(filled_resume, "")
    assert matched == [] and missing == [] and ratio == 0.0


def test_job_description_blends_into_score(filled_resume):
    without = score_resume(filled_resume)
    relevant = score_resume(
        filled_resume,
        "Backend engineer with Python, Kubernetes, Terraform and Kafka experience.",
    )
    irrelevant = score_resume(
        filled_resume,
        "We need a florist with floristry certification and retail experience.",
    )
    assert relevant.score >= irrelevant.score
    assert without.score != relevant.score or relevant.score >= 80


def test_grades_map_bands():
    assert grade_for(95) == "A+"
    assert grade_for(85) == "A"
    assert grade_for(72) == "B"
    assert grade_for(61) == "C"
    assert grade_for(51) == "D"
    assert grade_for(10) == "F"


def test_ats_endpoint(client, filled_resume):
    payload = AtsScoreRequest(
        resume=filled_resume,
        job_description="Python backend engineer, Docker, Kubernetes, Kafka.",
    )
    body = client.post("/api/ai/ats-score", json=payload.model_dump(mode="json")).json()
    assert 0 <= body["score"] <= 100
    assert body["grade"]
    assert len(body["checks"]) == 15
    assert body["suggestions"]
    assert isinstance(body["matched_keywords"], list)


def test_ats_endpoint_accepts_bare_minimum_resume(client):
    resume = Resume(title="Blank", personal=PersonalInfo())
    payload = AtsScoreRequest(resume=resume)
    body = client.post("/api/ai/ats-score", json=payload.model_dump(mode="json")).json()
    assert body["score"] < 20
    assert len(body["suggestions"]) >= 3
