"""Tailoring tests: advert → a CV written for that advert, plus its ATS score."""

from __future__ import annotations

from models import TailorRequest

ADVERT = (
    "We are hiring a Senior Data Analyst to own experimentation and reporting. "
    "You will use SQL and Python daily, build dbt models and design A/B tests. "
    "Tableau and stakeholder management required for our fintech scale-up."
)


def test_tailor_from_pasted_advert(client):
    response = client.post(
        "/api/jobs/tailor",
        json=TailorRequest(
            job_description=ADVERT,
            full_name="Alex Morgan",
            email="alex@example.com",
            years_experience=6,
            seniority="senior",
            achievements=["Cut reporting time by 40%"],
        ).model_dump(),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["resume"]["personal"]["full_name"] == "Alex Morgan"
    assert body["resume"]["summary"]
    assert body["resume"]["experience"][0]["bullets"]
    assert body["score"]["score"] > 40
    assert body["job"]["source"] == "paste"
    # Coverage now travels as data (the two keyword lists), never as prose, so the
    # studio cannot print the same information twice next to the CV sheet.
    assert body["matched_keywords"]
    assert not any("advert keyword" in note for note in body["notes"])
    assert body["provider"] == "local"


def test_tailor_uses_advert_vocabulary_in_skills(client):
    advert = "Senior Data Analyst: dbt, Airflow, causal inference, experimentation, Snowflake."
    body = client.post(
        "/api/jobs/tailor", json=TailorRequest(job_description=advert).model_dump()
    ).json()
    skills = [skill.lower() for group in body["resume"]["skills"] for skill in group["skills"]]
    assert any(word in skills for word in ("dbt", "airflow", "snowflake"))


def test_tailor_from_link_cleans_board_title_to_role(client, monkeypatch):
    """A scraped page title must reach the CV as a role, not as an advert.

    The Sber board once poured "Вакансия Data Engineer (команда B2C-SQL) в г
    Москва" into the CV title, headline, summary, experience role and bullets.
    """
    from models import JobPosting

    advert = (
        "Data Engineer: build batch and streaming pipelines in Spark and Kafka "
        "with Scala, SQL and ClickHouse on Kubernetes. Mentored two engineers."
    )
    monkeypatch.setattr(
        "ai.tailor.fetch_job",
        lambda url: JobPosting(
            url=url,
            ok=True,
            title="Вакансия Data Engineer (команда B2C-SQL) в г Москва",
            company="Работа в Сбере",
            description=advert,
            keywords=[],
            source="meta",
        ),
    )
    body = client.post(
        "/api/jobs/tailor", json=TailorRequest(url="https://rabota.sber.ru/x/1").model_dump()
    ).json()
    resume = body["resume"]

    # The role, stripped of board boilerplate, heads the CV.
    assert resume["title"] == "Data Engineer — tailored"
    assert resume["personal"]["headline"].startswith("Data Engineer |")
    assert "Вакансия" not in resume["summary"]
    assert "в г Москва" not in resume["summary"]
    assert "команда" not in resume["summary"]

    # The company you apply to is never your employer in the CV.
    assert all(item["company"] == "[Company]" for item in resume["experience"])
    assert "Сбере" not in str(resume["experience"])

    # Real skills from the advert, no page furniture.
    skills = [s.lower() for g in resume["skills"] for s in g["skills"]]
    assert "spark" in skills and "kafka" in skills
    assert not any("cookies" in s for s in skills)
    assert not any("sberbank" in s for s in skills)
    assert not any("b2c" in s for s in skills)

    # Bullets talk about the job's tools, not the hiring company.
    bullets = " ".join(b for item in resume["experience"] for b in item["bullets"]).lower()
    assert "спере" not in bullets and "b2c" not in bullets


def test_clean_role_title_strips_board_boilerplate():
    from ai.tailor import clean_role_title

    assert clean_role_title("Вакансия Data Engineer (команда B2C-SQL) в г Москва") == "Data Engineer"
    assert clean_role_title("Job: Senior Nurse - Careers | Acme") == "Senior Nurse"
    assert clean_role_title("Vacancy: Product Manager в Санкт-Петербурге") == "Product Manager"
    assert clean_role_title("Data Analyst") == "Data Analyst"
    assert clean_role_title("") == ""


def test_advert_skills_drop_page_junk(client):
    from ai.tailor import _advert_skills

    picked = _advert_skills(
        ["cookies", "www.sberbank.ru", "b2c-sql", "quality", "spark", "kafka", "sql"], 10
    )
    lowered = [s.lower() for s in picked]
    assert "spark" in lowered and "kafka" in lowered and "sql" in lowered
    assert "cookies" not in lowered
    assert not any("sberbank" in s for s in lowered)
    # Unknown words are not skills even when they appear in the advert.
    assert "quality" not in lowered


def test_tailor_from_title_only_returns_usable_cv(client):
    body = client.post(
        "/api/jobs/tailor", json=TailorRequest(job_title="Registered Nurse").model_dump()
    ).json()
    assert body["resume"]["summary"]
    assert "nurse" in body["resume"]["summary"].lower()
    assert any("job title alone" in note for note in body["notes"])
    assert body["resume"]["experience"][0]["company"] == "[Company]"


def test_tailor_keeps_existing_resume_content(client, sample):
    body = client.post(
        "/api/jobs/tailor",
        json=TailorRequest(
            job_description="Analytics role needing SQL, Python, dbt and A/B testing.",
            base_resume=sample.model_dump(mode="json"),
        ).model_dump(mode="json"),
    ).json()
    assert body["resume"]["personal"]["full_name"] == "Alex Morgan"
    assert len(body["resume"]["experience"]) == 2  # history preserved
    assert body["resume"]["experience"][0]["bullets"]


def test_tailor_applies_template_and_locale(client):
    body = client.post(
        "/api/jobs/tailor",
        json=TailorRequest(job_title="Data Analyst", locale="de", template="berlin").model_dump(),
    ).json()
    assert body["resume"]["template"] == "berlin"
    assert body["resume"]["locale"] == "de"
    assert body["resume"]["skills"][0]["name"] == "Kenntnisse"


def test_tailored_resume_can_be_exported(client):
    tailored = client.post(
        "/api/jobs/tailor", json=TailorRequest(job_description=ADVERT).model_dump()
    ).json()["resume"]
    pdf = client.post("/api/export/pdf", json=tailored)
    assert pdf.status_code == 200
    assert pdf.content.startswith(b"%PDF")
    docx = client.post("/api/export/docx", json=tailored)
    assert docx.status_code == 200
