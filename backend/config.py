"""Central configuration for the MyResume backend.

All values come from environment variables (see `.env.example`).
Nothing is mandatory: with no AI keys the app still serves the full API
using the deterministic offline engine.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(PROJECT_ROOT / ".env", BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ── Server ────────────────────────────────────────────
    app_name: str = "MyResume API"
    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    database_path: str = "data/myresume.db"

    # ── AI chain ──────────────────────────────────────────
    ai_provider: str = "auto"
    ai_timeout_seconds: float = 45.0
    ai_max_tokens: int = 1200
    ai_temperature: float = 0.6

    openrouter_api_key: str = ""
    openrouter_model: str = "meta-llama/llama-3.3-70b-instruct:free"
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    mistral_api_key: str = ""
    mistral_model: str = "mistral-small-latest"
    cerebras_api_key: str = ""
    cerebras_model: str = "llama3.3-70b"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"

    # ── Job-link import (scraper engine chain) ─────────────
    # `ats` first: when we recognise the board we ask its JSON API, which
    # cannot be bot-walled. The rest of the chain is the fallback for every
    # other careers page.
    scrape_engines: str = "ats,scrapegraph,playwright,reader,http"
    scrape_timeout_seconds: float = 20.0
    scrapegraph_enabled: bool = True
    scrapegraph_api_key: str = ""          # SGAI_API_KEY — hosted ScrapeGraphAI API
    scrapegraph_llm_model: str = ""        # e.g. ollama/llama3 for the OSS library
    scrapegraph_fallback_to_library: bool = True
    scrape_playwright_enabled: bool = True
    scrape_reader_enabled: bool = True

    # ── Product ───────────────────────────────────────────
    free_resume_limit: int = 2
    default_locale: str = "en"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def database_file(self) -> Path:
        path = Path(self.database_path)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        return path


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
