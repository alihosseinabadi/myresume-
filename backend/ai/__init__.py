"""MyResume AI layer.

Public surface::

    from ai import engine, engine_ats
    engine.generate_summary(SummaryRequest(...))
    engine_ats.score_ats(AtsScoreRequest(...))

The LLM provider chain is tried first; :mod:`ai.local_engine` answers whenever
no provider is reachable, so the API is fully functional with zero API keys.
"""

from ai import (  # noqa: F401
    engine,
    engine_ats,
    keywords,
    lexicon,
    local_engine,
    prompts,
    prompts_letters,
    providers,
    runtime,
    skills,
    translations,
)

__all__ = [
    "engine",
    "engine_ats",
    "local_engine",
    "providers",
    "runtime",
    "keywords",
    "lexicon",
    "prompts",
    "prompts_letters",
    "skills",
    "translations",
]
