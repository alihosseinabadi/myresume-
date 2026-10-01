"""Job-link import tests (network is faked with httpx.MockTransport)."""

from __future__ import annotations

import json

import httpx
import pytest

from models import JobImportRequest
from services.html_extract import HtmlProbe, json_ld_jobs
from services.job_import import fetch_job

POSTING_HTML = """
<!doctype html>
<html><head>
  <title>Senior Data Analyst | Acme Careers</title>
  <meta property="og:site_name" content="Acme" />
  <meta name="description" content="short meta" />
  <script type="application/ld+json">
  {"@context":"https://schema.org","@type":"JobPosting",
   "title":"Senior Data Analyst",
   "hiringOrganization":{"@type":"Organization","name":"Acme Analytics"},
   "jobLocation":{"@type":"Place","address":{"addressLocality":"Berlin"}},
   "description":"<p>We are looking for a Senior Data Analyst to own experimentation and reporting.</p><ul><li>SQL and Python daily</li><li>Build dbt models</li><li>Partner with product on A/B testing</li><li>Tableau dashboards for finance</li></ul><p>Stakeholder management and forecasting experience required. You will work with Kafka data streams and mentor two analysts.</p>"
  }
  </script>
</head>
<body><nav>Skip me</nav><main><p>Visible fallback text that is long enough to be used if JSON-LD is missing.</p></main></body></html>
"""


def client_for(html: str, status_code: int = 200) -> httpx.Client:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, text=html)

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_strip_html_ignores_scripts_and_nav():
    probe = HtmlProbe()
    probe.feed("<nav>menu</nav><p>Real content here</p><script>var x=1</script>")
    assert "Real content" in probe.text
    assert "menu" not in probe.text
    assert "var x" not in probe.text


def test_json_ld_jobs_finds_nested_posting():
    blocks = [
        json.dumps({
            "@context": "https://schema.org",
            "@graph": [{"@type": "WebSite"}, {"@type": ["JobPosting"], "title": "Nurse"}],
        })
    ]
    jobs = json_ld_jobs(blocks)
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Nurse"


def test_fetch_job_reads_json_ld():
    job = fetch_job("https://jobs.example.com/123", client=client_for(POSTING_HTML), engines=["http"])
    assert job.ok is True
    assert job.title == "Senior Data Analyst"
    assert job.company == "Acme Analytics"
    assert job.location == "Berlin"
    assert "A/B testing" in job.description
    assert "<p>" not in job.description
    assert "sql" in job.keywords
    assert job.engine == "http"
    assert job.attempts and job.attempts[0].startswith("http:")


def test_fetch_job_falls_back_to_meta_and_text():
    html = (
        "<html><head><title>Support Engineer - Globex</title>"
        "<meta name='description' content='welcome'></head>"
        "<body><p>" + ("Handle escalations, Zendesk and SLA reporting. " * 12) + "</p></body></html>"
    )
    job = fetch_job("globex.example/careers/1", client=client_for(html), engines=["http"])
    assert job.title == "Support Engineer"
    assert "Zendesk" in job.description
    assert job.source in {"meta", "html"}


def test_fetch_job_handles_http_errors():
    job = fetch_job(
        "https://blocked.example/job",
        client=client_for("nope", status_code=403),
        engines=["http"],
    )
    assert job.ok is False
    assert job.company == "blocked.example"
    assert "paste the advert text" in job.message.lower()
    assert job.engine == ""  # nothing answered
    assert any("403" in a or "http:" in a for a in job.attempts)


@pytest.mark.parametrize("bad", ["", "   "])
def test_fetch_job_rejects_empty_input(bad):
    job = fetch_job(bad, client=client_for("<html></html>"), engines=["http"])
    assert job.ok is False
    assert job.message


def test_import_endpoint_requires_a_url(client):
    response = client.post("/api/jobs/import", json=JobImportRequest(url="").model_dump())
    assert response.status_code == 422
