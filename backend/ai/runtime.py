"""Provider plumbing shared by the engine features: caching, JSON repair, logging."""

from __future__ import annotations

import hashlib
import json
import re
import time
from typing import Any

from ai import providers
from ai.keywords import normalize
from config import settings
from db import log_ai_event

CACHE_MAX = 256
CACHE_TTL_SECONDS = 3600
OFFLINE_MODEL = "myresume-offline-engine"
_CACHE: dict[str, tuple[float, Any]] = {}
_JSON_BLOCK = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


def cache_key(feature: str, payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, default=str, ensure_ascii=False)
    return f"{feature}:{hashlib.sha256(raw.encode()).hexdigest()[:24]}"


def cache_get(key: str) -> Any | None:
    entry = _CACHE.get(key)
    if not entry:
        return None
    stored_at, value = entry
    if time.time() - stored_at > CACHE_TTL_SECONDS:
        _CACHE.pop(key, None)
        return None
    return value


def cache_put(key: str, value: Any) -> None:
    if len(_CACHE) >= CACHE_MAX:
        oldest = min(_CACHE.items(), key=lambda kv: kv[1][0])[0]
        _CACHE.pop(oldest, None)
    _CACHE[key] = (time.time(), value)


def clear_cache() -> None:
    _CACHE.clear()


def coerce_json(raw: str) -> Any | None:
    """Parse model output into JSON, tolerating fences and surrounding prose."""
    if not raw:
        return None
    text = raw.strip()
    fenced = _JSON_BLOCK.search(text)
    if fenced:
        text = fenced.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    for opener, closer in (("{", "}"), ("[", "]")):
        start, end = text.find(opener), text.rfind(closer)
        if start != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                continue
    return None


def log_event(feature: str, provider: str, model: str, latency_ms: int, ok: bool = True) -> None:
    """Record AI usage; telemetry must never break a request."""
    try:
        log_ai_event(feature, provider, model, ok, latency_ms)
    except Exception:  # noqa: BLE001
        pass


def llm_json(
    messages: list[dict[str, str]],
    feature: str,
    cache_payload: Any = None,
    use_cache: bool = True,
) -> tuple[Any | None, str, str, int]:
    """Call the provider chain; return ``(parsed_json, provider, model, latency_ms)``.

    ``(None, "local", "", 0)`` means "no provider answered" — the caller should
    use the offline engine. A raw string is returned when the model replied with
    usable prose instead of JSON.
    """
    if (settings.ai_provider or "").strip().lower() == "local":
        log_event(feature, "local", OFFLINE_MODEL, 0)
        return None, "local", "", 0

    key = cache_key(feature, cache_payload if cache_payload is not None else messages)
    if use_cache:
        cached = cache_get(key)
        if cached is not None:
            return cached

    result = providers.chat(messages)
    if result.fallback or not result.text:
        log_event(feature, "local", "", 0, ok=False)
        return None, "local", "", 0

    parsed = coerce_json(result.text)
    if parsed is None:
        log_event(feature, result.provider, result.model, result.latency_ms, ok=False)
        return result.text, result.provider, result.model, result.latency_ms

    if use_cache:
        cache_put(key, (parsed, result.provider, result.model, result.latency_ms))
    log_event(feature, result.provider, result.model, result.latency_ms)
    return parsed, result.provider, result.model, result.latency_ms


def text_from(data: Any, *keys: str) -> str:
    """Pull a prose string out of a JSON dict, or accept raw prose as-is."""
    if isinstance(data, dict):
        for key in keys:
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                return normalize(value)
    if isinstance(data, str):
        stripped = data.strip()
        if len(stripped) > 40 and not stripped.startswith(("{", "[")):
            return normalize(stripped)
    return ""


def list_from(data: Any, *keys: str) -> list[str]:
    """Pull a list of strings out of a JSON dict or a bare array."""
    container = data
    if isinstance(data, dict):
        container = next(
            (data.get(k) for k in keys if isinstance(data.get(k), (list, tuple))), None
        )
    if isinstance(container, (list, tuple)):
        return [normalize(str(item)) for item in container if str(item).strip()]
    return []
