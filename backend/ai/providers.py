"""LLM provider chain.

Providers are tried in a fixed order and the first *configured* one wins:

    openrouter → groq → gemini → mistral → cerebras → ollama → local

Every transport is plain ``httpx`` against the provider's OpenAI-compatible
(or Gemini native) HTTP API, so there are no vendor SDK dependencies. A custom
``httpx.Client`` can be injected for tests.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import httpx

from config import settings
from models import ProviderInfo


@dataclass(frozen=True)
class Provider:
    name: str
    model: str
    kind: str  # "openai" | "gemini" | "local"
    base_url: str
    api_key: str = ""

    @property
    def configured(self) -> bool:
        if self.kind == "local":
            return True  # the offline engine is always available
        if self.kind == "openai" and "11434" in self.base_url:
            return True  # ollama needs no key
        return bool(self.api_key)


@dataclass
class ChatResult:
    text: str
    provider: str
    model: str
    latency_ms: int
    fallback: bool = False


CHAIN_ORDER = ["openrouter", "groq", "gemini", "mistral", "cerebras", "ollama", "local"]


def _catalog() -> dict[str, Provider]:
    return {
        "openrouter": Provider(
            name="openrouter",
            model=settings.openrouter_model,
            kind="openai",
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.openrouter_api_key,
        ),
        "groq": Provider(
            name="groq",
            model=settings.groq_model,
            kind="openai",
            base_url="https://api.groq.com/openai/v1",
            api_key=settings.groq_api_key,
        ),
        "gemini": Provider(
            name="gemini",
            model=settings.gemini_model,
            kind="gemini",
            base_url="https://generativelanguage.googleapis.com/v1beta",
            api_key=settings.gemini_api_key,
        ),
        "mistral": Provider(
            name="mistral",
            model=settings.mistral_model,
            kind="openai",
            base_url="https://api.mistral.ai/v1",
            api_key=settings.mistral_api_key,
        ),
        "cerebras": Provider(
            name="cerebras",
            model=settings.cerebras_model,
            kind="openai",
            base_url="https://api.cerebras.ai/v1",
            api_key=settings.cerebras_api_key,
        ),
        "ollama": Provider(
            name="ollama",
            model=settings.ollama_model,
            kind="openai",
            base_url=f"{settings.ollama_base_url.rstrip('/')}/v1",
        ),
        "local": Provider(
            name="local",
            model="myresume-offline-engine",
            kind="local",
            base_url="",
        ),
    }


def catalog() -> list[ProviderInfo]:
    """Every provider with its availability — drives `/api/ai/providers`."""
    cat = _catalog()
    return [
        ProviderInfo(
            name=cat[name].name,
            model=cat[name].model,
            configured=cat[name].configured,
            kind=cat[name].kind,
        )
        for name in CHAIN_ORDER
    ]


def resolve_chain() -> list[Provider]:
    """Ordered list of providers to attempt, honouring ``AI_PROVIDER``."""
    cat = _catalog()
    requested = (settings.ai_provider or "auto").strip().lower()

    if requested in cat and requested != "auto":
        primary = [cat[requested]]
        if requested != "local":
            primary.append(cat["local"])
        return primary

    chain = []
    for name in CHAIN_ORDER:
        if name == "local":
            continue
        provider = cat[name]
        if not provider.configured:
            continue
        # Ollama needs no key, so verify the daemon is actually listening before
        # putting it in the chain — otherwise every call wastes a connect attempt.
        if name == "ollama" and not ollama_available():
            continue
        chain.append(provider)
    chain.append(cat["local"])
    return chain


_OLLAMA_PROBE = {"checked_at": 0.0, "ok": False}
OLLAMA_PROBE_TTL_SECONDS = 60.0


def ollama_available() -> bool:
    """Cached liveness probe for a local Ollama daemon."""
    now = time.time()
    if now - _OLLAMA_PROBE["checked_at"] < OLLAMA_PROBE_TTL_SECONDS:
        return bool(_OLLAMA_PROBE["ok"])
    ok = False
    try:
        with httpx.Client(timeout=1.5) as client:
            ok = client.get(f"{settings.ollama_base_url.rstrip('/')}/api/tags").status_code == 200
    except Exception:  # noqa: BLE001 - daemon simply is not running
        ok = False
    _OLLAMA_PROBE.update(checked_at=now, ok=ok)
    return ok


def active_provider_name() -> str:
    chain = resolve_chain()
    return chain[0].name if chain else "local"


def _openai_payload(provider: Provider, messages: list[dict[str, str]], **kw: Any) -> dict[str, Any]:
    return {
        "model": provider.model,
        "messages": messages,
        "temperature": kw.get("temperature", settings.ai_temperature),
        "max_tokens": kw.get("max_tokens", settings.ai_max_tokens),
    }


def _gemini_payload(messages: list[dict[str, str]], **kw: Any) -> dict[str, Any]:
    system_parts = [m["content"] for m in messages if m["role"] == "system"]
    user_parts = [m["content"] for m in messages if m["role"] != "system"]
    payload: dict[str, Any] = {
        "contents": [{"role": "user", "parts": [{"text": "\n\n".join(user_parts)}]}],
        "generationConfig": {
            "temperature": kw.get("temperature", settings.ai_temperature),
            "maxOutputTokens": kw.get("max_tokens", settings.ai_max_tokens),
        },
    }
    if system_parts:
        payload["systemInstruction"] = {"parts": [{"text": "\n\n".join(system_parts)}]}
    return payload


def _extract_openai_text(data: dict[str, Any]) -> str:
    choices = data.get("choices") or []
    if not choices:
        return ""
    return (choices[0].get("message") or {}).get("content", "") or ""


def _extract_gemini_text(data: dict[str, Any]) -> str:
    candidates = data.get("candidates") or []
    if not candidates:
        return ""
    parts = (candidates[0].get("content") or {}).get("parts") or []
    return "".join(p.get("text", "") for p in parts)


def chat(
    messages: list[dict[str, str]],
    client: httpx.Client | None = None,
    **kw: Any,
) -> ChatResult:
    """Send ``messages`` to the first working provider.

    Returns a :class:`ChatResult`; on total failure ``text`` is empty and
    ``fallback`` is True, so callers switch to the offline engine.
    """
    owned_client = client is None
    http = client or httpx.Client(timeout=settings.ai_timeout_seconds)

    try:
        for provider in resolve_chain():
            if provider.kind == "local":
                break
            started = time.perf_counter()
            try:
                if provider.kind == "gemini":
                    resp = http.post(
                        f"{provider.base_url}/models/{provider.model}:generateContent",
                        params={"key": provider.api_key},
                        json=_gemini_payload(messages, **kw),
                    )
                    resp.raise_for_status()
                    text = _extract_gemini_text(resp.json())
                else:
                    headers = {"Content-Type": "application/json"}
                    if provider.api_key:
                        headers["Authorization"] = f"Bearer {provider.api_key}"
                    resp = http.post(
                        f"{provider.base_url}/chat/completions",
                        headers=headers,
                        json=_openai_payload(provider, messages, **kw),
                    )
                    resp.raise_for_status()
                    text = _extract_openai_text(resp.json())

                if text.strip():
                    return ChatResult(
                        text=text.strip(),
                        provider=provider.name,
                        model=provider.model,
                        latency_ms=int((time.perf_counter() - started) * 1000),
                    )
            except Exception:  # noqa: BLE001 - provider outages are expected
                continue
    finally:
        if owned_client:
            http.close()

    return ChatResult(text="", provider="local", model="", latency_ms=0, fallback=True)

