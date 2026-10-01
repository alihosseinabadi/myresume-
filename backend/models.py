"""Pydantic schemas shared by the API, the AI engine and the exporters."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field

Tone = Literal["professional", "confident", "friendly", "concise", "executive"]
Seniority = Literal["intern", "junior", "mid", "senior", "lead", "manager", "director", "executive"]
TemplateId = Literal["athens", "berlin", "cairo", "dublin", "geneva", "helsinki", "istanbul", "lisbon", "munich", "oslo", "prague"]


def _uid() -> str:
    return uuid4().hex[:12]


def _now() -> datetime:
    return datetime.now(timezone.utc)


class PersonalInfo(BaseModel):
    full_name: str = ""
    headline: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    website: str = ""
    linkedin: str = ""
    github: str = ""
    photo_url: str = ""


class ExperienceItem(BaseModel):
    id: str = Field(default_factory=_uid)
    role: str = ""
    company: str = ""
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    current: bool = False
    description: str = ""
    bullets: list[str] = Field(default_factory=list)


class EducationItem(BaseModel):
    id: str = Field(default_factory=_uid)
    degree: str = ""
    school: str = ""
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    description: str = ""


class SkillGroup(BaseModel):
    id: str = Field(default_factory=_uid)
    name: str = "Skills"
    skills: list[str] = Field(default_factory=list)


class ProjectItem(BaseModel):
    id: str = Field(default_factory=_uid)
    name: str = ""
    link: str = ""
    description: str = ""
    bullets: list[str] = Field(default_factory=list)


class CertificationItem(BaseModel):
    id: str = Field(default_factory=_uid)
    name: str = ""
    issuer: str = ""
    date: str = ""


class LanguageItem(BaseModel):
    id: str = Field(default_factory=_uid)
    name: str = ""
    level: str = ""


class CustomSection(BaseModel):
    id: str = Field(default_factory=_uid)
    title: str = ""
    body: str = ""
    bullets: list[str] = Field(default_factory=list)


class Resume(BaseModel):
    id: str = Field(default_factory=_uid)
    title: str = "Untitled resume"
    template: TemplateId = "athens"
    accent_color: str = "#0F766E"
    font: Literal["sans", "serif", "mono"] = "sans"
    locale: str = "en"
    personal: PersonalInfo = Field(default_factory=PersonalInfo)
    summary: str = ""
    experience: list[ExperienceItem] = Field(default_factory=list)
    education: list[EducationItem] = Field(default_factory=list)
    skills: list[SkillGroup] = Field(default_factory=list)
    projects: list[ProjectItem] = Field(default_factory=list)
    certifications: list[CertificationItem] = Field(default_factory=list)
    languages: list[LanguageItem] = Field(default_factory=list)
    custom_sections: list[CustomSection] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class ResumeCreate(BaseModel):
    title: str = "Untitled resume"
    template: TemplateId = "athens"
    locale: str = "en"
    personal: PersonalInfo | None = None


class ResumeUpdate(BaseModel):
    resume: Resume


# ── AI request / response contracts ───────────────────────


class ProfileContext(BaseModel):
    job_title: str = ""
    company: str = ""
    seniority: Seniority = "mid"
    years_experience: int = 0
    industry: str = ""
    skills: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)
    tone: Tone = "professional"
    locale: str = "en"
    language: str = "English"


class SummaryRequest(ProfileContext):
    existing_text: str = ""


class BulletsRequest(ProfileContext):
    role: str = ""
    count: int = 4


class SkillsRequest(ProfileContext):
    existing_skills: list[str] = Field(default_factory=list)
    limit: int = 12


class CoverLetterRequest(ProfileContext):
    company: str = ""
    hiring_manager: str = ""
    job_description: str = ""
    highlights: list[str] = Field(default_factory=list)


class AtsScoreRequest(BaseModel):
    resume: Resume
    job_description: str = ""


class AtsCheck(BaseModel):
    id: str
    label: str
    passed: bool
    weight: int
    detail: str = ""


class AtsScoreResponse(BaseModel):
    score: int
    grade: str
    matched_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    checks: list[AtsCheck] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


class TranslateRequest(BaseModel):
    target_locale: str
    headings: list[str] = Field(default_factory=list)


class DraftResumeRequest(BaseModel):
    prompt: str
    locale: str = "en"
    template: TemplateId = "athens"


class AiTextResponse(BaseModel):
    text: str
    provider: str
    model: str = ""
    latency_ms: int = 0
    fallback: bool = False


class AiListResponse(BaseModel):
    items: list[str]
    provider: str
    model: str = ""
    latency_ms: int = 0
    fallback: bool = False


class ProviderInfo(BaseModel):
    name: str
    model: str
    configured: bool
    kind: str


class HealthResponse(BaseModel):
    status: str
    app: str
    env: str
    ai_provider: str
    ai_ready: bool
    providers: list[ProviderInfo]


# ── Letters & career matching ─────────────────────────────


class ResignationRequest(BaseModel):
    full_name: str = ""
    job_title: str = ""
    company: str = ""
    manager_name: str = ""
    last_working_day: str = ""   # free text, e.g. "28 February 2026" or "in two weeks"
    reason: str = ""             # optional; never required for a professional exit
    tone: Tone = "professional"
    keep_contact: bool = True
    highlight: str = ""          # what you want remembered (a project, a launch…)


class ResignationResponse(BaseModel):
    letter: str
    provider: str = "local"
    fallback: bool = False
    word_count: int = 0
    checklist: list[str] = Field(default_factory=list)


class CareerMatchRequest(BaseModel):
    strength: Literal["ideas", "data", "people", "operations"] = "data"
    interests: str = ""
    years_experience: int = 0
    seniority: Seniority = "mid"


class CareerMatchResponse(BaseModel):
    roles: list[dict] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    note: str = ""


# ── Job-link import & tailoring ───────────────────────────


class JobImportRequest(BaseModel):
    url: str


class JobPosting(BaseModel):
    url: str = ""
    ok: bool = True
    title: str = ""
    company: str = ""
    location: str = ""
    description: str = ""
    keywords: list[str] = Field(default_factory=list)
    source: str = ""  # json-ld | meta | html | markdown | paste | title
    engine: str = ""  # scrapegraph | playwright | reader | http
    attempts: list[str] = Field(default_factory=list)
    message: str = ""


class TailorRequest(BaseModel):
    """Either a job URL, a pasted advert, or just a job title — plus the profile."""

    url: str = ""
    job_description: str = ""
    job_title: str = ""
    locale: str = "en"
    template: TemplateId = "athens"

    # What we already know about the candidate (all optional).
    full_name: str = ""
    headline: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    years_experience: int = 0
    seniority: Seniority = "mid"
    tone: Tone = "professional"
    skills: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)
    base_resume: Resume | None = None


class TailorResponse(BaseModel):
    resume: Resume
    score: AtsScoreResponse
    job: JobPosting
    matched_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    provider: str = "local"
    latency_ms: int = 0
    notes: list[str] = Field(default_factory=list)
