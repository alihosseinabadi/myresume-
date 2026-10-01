"""Resume CRUD endpoint tests."""

from __future__ import annotations


def test_create_resume_uses_template_accent(client):
    body = client.post(
        "/api/resumes",
        json={"title": "My CV", "template": "berlin", "locale": "en"},
    ).json()
    assert body["id"]
    assert body["template"] == "berlin"
    assert body["accent_color"] == "#1D4ED8"  # berlin accent from the catalog
    assert body["personal"]["full_name"] == ""


def test_create_resume_accepts_personal_details(client):
    body = client.post(
        "/api/resumes",
        json={
            "title": "Engineer CV",
            "template": "athens",
            "personal": {"full_name": "Jane Doe", "email": "jane@example.com"},
        },
    ).json()
    assert body["personal"]["full_name"] == "Jane Doe"


def test_full_crud_cycle(client):
    created = client.post("/api/resumes", json={"title": "Lifecycle", "template": "oslo"}).json()
    resume_id = created["id"]

    listed = client.get("/api/resumes").json()
    assert any(r["id"] == resume_id for r in listed["resumes"])

    fetched = client.get(f"/api/resumes/{resume_id}").json()
    assert fetched["title"] == "Lifecycle"

    created["title"] = "Lifecycle updated"
    updated = client.put(f"/api/resumes/{resume_id}", json=created).json()
    assert updated["title"] == "Lifecycle updated"

    clone = client.post(f"/api/resumes/{resume_id}/duplicate").json()
    assert clone["id"] != resume_id
    assert clone["title"] == "Lifecycle updated (copy)"

    removed = client.delete(f"/api/resumes/{clone['id']}")
    assert removed.status_code == 200
    assert removed.json()["deleted"] == clone["id"]


def test_missing_resume_returns_404(client):
    assert client.get("/api/resumes/does-not-exist").status_code == 404
    assert client.delete("/api/resumes/does-not-exist").status_code == 404
    assert client.post(
        "/api/resumes/does-not-exist/duplicate"
    ).status_code == 404


def test_resume_limit_validation(client):
    assert client.get("/api/resumes", params={"limit": 0}).status_code == 422
    assert client.get("/api/resumes", params={"limit": 500}).status_code == 422


def test_invalid_template_is_rejected(client):
    response = client.post("/api/resumes", json={"title": "Bad", "template": "atlantis"})
    assert response.status_code == 422
