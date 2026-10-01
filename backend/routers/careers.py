"""Career matching endpoint (instant, ontology-driven, no LLM)."""

from __future__ import annotations

from fastapi import APIRouter

from models import CareerMatchRequest, CareerMatchResponse
from services.careers import match_careers

router = APIRouter(prefix="/api/careers", tags=["careers"])


@router.post("/match", response_model=CareerMatchResponse)
def post_match(req: CareerMatchRequest) -> CareerMatchResponse:
    """Suggest three role families plus the skills worth putting on a CV."""
    return match_careers(req)
