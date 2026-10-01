"""Resume CRUD, template catalog and the demo sample."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query

from catalog import TEMPLATES, template_by_id
from db import (
    count_resumes,
    delete_resume,
    get_resume,
    list_resumes,
    save_resume,
)
from models import Resume, ResumeCreate
from sample import sample_resume

router = APIRouter(prefix="/api", tags=["resumes"])


@router.get("/templates")
def get_templates() -> dict:
    """The 11 recruiter-approved templates used by the builder and the landing page."""
    return {"templates": TEMPLATES, "count": len(TEMPLATES)}


@router.get("/resumes")
def get_resumes(limit: int = Query(default=50, ge=1, le=200)) -> dict:
    resumes = list_resumes(limit)
    return {"resumes": resumes, "count": len(resumes)}


@router.post("/resumes", response_model=Resume, status_code=201)
def create_resume(payload: ResumeCreate) -> Resume:
    template = template_by_id(payload.template)
    resume = Resume(
        title=payload.title,
        template=payload.template,
        locale=payload.locale,
        accent_color=(template or {}).get("accent", "#0F766E"),
    )
    if payload.personal:
        resume.personal = payload.personal
    return save_resume(resume)


@router.get("/resumes/sample", response_model=Resume)
def get_sample_resume(locale: str = "en", template: str = "athens") -> Resume:
    """Populated example resume — powers the landing page live preview."""
    return sample_resume(locale=locale, template=template)


@router.get("/resumes/{resume_id}", response_model=Resume)
def get_one(resume_id: str) -> Resume:
    resume = get_resume(resume_id)
    if resume is None:
        raise HTTPException(status_code=404, detail=f"Resume {resume_id} not found")
    return resume


@router.put("/resumes/{resume_id}", response_model=Resume)
def update_resume(resume_id: str, payload: Resume) -> Resume:
    if get_resume(resume_id) is None:
        raise HTTPException(status_code=404, detail=f"Resume {resume_id} not found")
    payload.id = resume_id
    payload.updated_at = datetime.now(timezone.utc)
    return save_resume(payload)


@router.post("/resumes/{resume_id}/duplicate", response_model=Resume, status_code=201)
def duplicate_resume(resume_id: str) -> Resume:
    resume = get_resume(resume_id)
    if resume is None:
        raise HTTPException(status_code=404, detail=f"Resume {resume_id} not found")
    clone = resume.model_copy(deep=True)
    clone.id = Resume().id
    clone.title = f"{resume.title} (copy)"
    clone.created_at = datetime.now(timezone.utc)
    clone.updated_at = clone.created_at
    return save_resume(clone)


@router.delete("/resumes/{resume_id}")
def remove_resume(resume_id: str) -> dict:
    if not delete_resume(resume_id):
        raise HTTPException(status_code=404, detail=f"Resume {resume_id} not found")
    return {"deleted": resume_id, "remaining": count_resumes()}
