"""MyResume API — FastAPI application entry point.

Run locally::

    cd backend
    python -m uvicorn main:app --reload --port 8000

Interactive docs: http://localhost:8000/docs
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ai import providers
from catalog import TEMPLATES
from config import settings
from db import count_resumes, init_db
from models import HealthResponse
from routers import ai as ai_router
from routers import careers as careers_router
from routers import export as export_router
from routers import jobs as jobs_router
from routers import resumes as resumes_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=(
        "Resume builder API with an AI provider chain (OpenRouter, Groq, Gemini, "
        "Mistral, Cerebras, Ollama) and a deterministic offline engine fallback, "
        "plus ATS scoring and PDF/DOCX export."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

app.include_router(ai_router.router)
app.include_router(careers_router.router)
app.include_router(jobs_router.router)
app.include_router(resumes_router.router)
app.include_router(export_router.router)


@app.exception_handler(ValueError)
async def value_error_handler(_: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.get("/api/health", response_model=HealthResponse, tags=["meta"])
def health() -> HealthResponse:
    """Liveness + AI readiness probe used by the landing page status pill."""
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        env=settings.app_env,
        ai_provider=providers.active_provider_name(),
        ai_ready=True,
        providers=providers.catalog(),
    )


@app.get("/", tags=["meta"])
def root() -> dict:
    return {
        "app": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs",
        "templates": len(TEMPLATES),
        "saved_resumes": count_resumes(),
        "ai_provider": providers.active_provider_name(),
        "endpoints": [
            "/api/health",
            "/api/templates",
            "/api/resumes",
            "/api/resumes/sample",
            "/api/jobs/import",
            "/api/jobs/tailor",
            "/api/ai/summary",
            "/api/ai/bullets",
            "/api/ai/skills",
            "/api/ai/rewrite",
            "/api/ai/cover-letter",
            "/api/ai/ats-score",
            "/api/ai/translate",
            "/api/ai/draft",
            "/api/ai/chat",
            "/api/ai/providers",
            "/api/export/pdf",
            "/api/export/docx",
            "/api/export/txt",
        ],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.api_host, port=settings.api_port, reload=True)
