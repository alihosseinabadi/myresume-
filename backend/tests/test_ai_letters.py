"""Cover letters, heading translation, drafting, chat and usage telemetry."""

from __future__ import annotations

import pytest

from ai import engine
from ai.keywords import extract_keywords, word_count
from ai.translations import HEADING_KEYS, HEADING_TRANSLATIONS, translate_heading
from models import CoverLetterRequest

JD = (
    "We are hiring a Senior Data Analyst to own experimentation and reporting. "
    "You will use SQL and Python daily, build dbt models, and partner with product "
    "to design A/B tests. Experience with Tableau and stakeholder management required."
)


def test_cover_letter_endpoint(client, summary_request):
    payload = CoverLetterRequest(
        **summary_request.model_dump(exclude={"company"}),
        company="Payflow",
        job_description=JD,
        highlights=["Cut reporting time 40%", "Built 12 dashboards"],
    )
    body = client.post("/api/ai/cover-letter", json=payload.model_dump()).json()
    text = body["text"]
    assert body["fallback"] is True
    assert "Dear Hiring Manager," in text
    assert "Payflow" in text
    assert "Data Analyst" in text
    assert 120 <= word_count(text) <= 450
    assert "thank you for your time" in text.lower()
    assert text.count("\n\n") >= 4


def test_cover_letter_uses_hiring_manager_name(client, summary_request):
    payload = CoverLetterRequest(
        **summary_request.model_dump(exclude={"company"}),
        company="Acme",
        hiring_manager="Dana Reed",
    )
    text = client.post("/api/ai/cover-letter", json=payload.model_dump()).json()["text"]
    assert text.startswith("Dear Dana Reed,")


def test_cover_letter_mirrors_job_ad_keywords(summary_request):
    payload = CoverLetterRequest(
        **summary_request.model_dump(exclude={"company"}),
        company="Acme",
        job_description=JD,
    )
    text = engine.local_engine.generate_cover_letter(payload).lower()
    assert "sql" in text or "dbt" in text or "testing" in text


def test_cover_letter_can_be_saved(client, summary_request):
    payload = CoverLetterRequest(
        **summary_request.model_dump(exclude={"company"}), company="Saved Co"
    )
    body = client.post(
        "/api/ai/cover-letter", params={"save": True}, json=payload.model_dump()
    ).json()
    assert body["text"]
    letters = client.get("/api/ai/cover-letters").json()
    assert any(letter["company"] == "Saved Co" for letter in letters["letters"])


def test_translate_endpoint(client):
    body = client.post(
        "/api/ai/translate",
        json={"target_locale": "de", "headings": ["Experience", "Education"]},
    ).json()
    assert body["headings"]["Experience"] == "Berufserfahrung"
    assert body["headings"]["Education"] == "Ausbildung"


def test_translate_all_headings_when_none_requested(client):
    headings = client.post(
        "/api/ai/translate", json={"target_locale": "fa", "headings": []}
    ).json()["headings"]
    assert len(headings) == len(HEADING_KEYS)
    assert headings["Skills"] == "مهارتها"


def test_translate_unknown_locale_falls_back_to_english():
    assert translate_heading("xx", "Skills") == "Skills"
    assert translate_heading("ja", "Education") == "学歴"
    assert translate_heading("", "Experience") == "Experience"


def test_all_locales_cover_every_heading():
    for locale, table in HEADING_TRANSLATIONS.items():
        missing = [key for key in HEADING_KEYS if key not in table]
        assert not missing, f"{locale} missing {missing}"
        assert all(value.strip() for value in table.values())


def test_translate_supports_at_least_twenty_locales():
    assert len(HEADING_TRANSLATIONS) >= 20


def test_draft_endpoint_returns_editable_resume(client):
    resume = client.post(
        "/api/ai/draft",
        json={"prompt": "marketing manager for a SaaS scale-up", "locale": "en"},
    ).json()
    assert resume["id"]
    assert resume["summary"]
    assert resume["experience"][0]["bullets"]
    assert resume["skills"][0]["name"] == "Skills"
    assert resume["experience"][0]["company"] == "[Company]"


def test_draft_endpoint_localises_skill_heading(client):
    resume = client.post("/api/ai/draft", json={"prompt": "vendeur", "locale": "fr"}).json()
    assert resume["skills"][0]["name"] == "Compétences"
    assert resume["locale"] == "fr"


def test_draft_endpoint_respects_template(client):
    resume = client.post(
        "/api/ai/draft",
        json={"prompt": "nurse", "template": "berlin"},
    ).json()
    assert resume["template"] == "berlin"


def test_chat_offline_advice_flags_missing_metrics(client):
    body = client.post(
        "/api/ai/chat",
        json={"question": "Is my CV good?", "cv_text": "Summary\n- managed a team\n- owned reporting"},
    ).json()
    assert body["fallback"] is True
    assert "bullets contain a number" in body["text"] or "verb" in body["text"]


def test_usage_endpoint_records_calls(client, summary_request):
    client.post("/api/ai/summary", json=summary_request.model_dump())
    body = client.get("/api/ai/usage").json()
    assert body["total_calls"] >= 1
    assert any(row["feature"] == "summary" for row in body["usage"])


def test_engine_module_surface():
    for name in (
        "generate_summary", "generate_bullets", "suggest_skills",
        "rewrite", "generate_cover_letter", "draft_resume", "translate_sections",
    ):
        assert callable(getattr(engine, name))


def test_keyword_extraction_promotes_phrases_and_drops_stopwords():
    keywords = extract_keywords(JD, limit=25)
    assert "sql" in keywords
    assert "experience" not in keywords
    assert len(keywords) <= 25
    assert keywords[0] in {"stakeholder management", "a/b testing"} or len(keywords[0]) > 5


def test_keyword_extraction_drops_page_furniture():
    """Scraped adverts carry cookie banners and footer domains — not keywords."""
    text = (
        "We need a Data Engineer with Spark and SQL. "
        "Cookies policy on www.sberbank.ru and cookie consent banner. "
        "Data Quality-фреймворк and ETL/ELT-процессов."
    )
    keywords = extract_keywords(text, limit=25)
    assert "spark" in keywords and "sql" in keywords
    assert "cookies" not in keywords
    assert "cookie" not in keywords
    assert not any("sberbank" in k for k in keywords)
    assert not any(k.endswith("-") for k in keywords)  # hyphen debris stripped


def test_keyword_extraction_drops_team_codes():
    """"b2c-sql" is a team name, not something to put on a CV."""
    keywords = extract_keywords(
        "Data Engineer (команда B2C-SQL) in Berlin. Skills: Spark, Kafka, team-42.",
        limit=25,
    )
    assert "spark" in keywords and "kafka" in keywords
    assert "b2c-sql" not in keywords
    assert "team-42" not in keywords
    # Digit-only skills without a hyphen are still fine.
    assert "html5" in extract_keywords("HTML5 and CSS3 please", limit=10)


@pytest.mark.parametrize(
    "locale,expected",
    [("tr", "İş deneyimi"), ("zh", "工作经历"), ("ru", "Опыт работы"), ("ar", "الخبرة المهنية")],
)
def test_heading_translations_spot_check(locale, expected):
    assert translate_heading(locale, "Experience") == expected
