"""Outcome service — wraps analysis service outcome recording."""
from __future__ import annotations

from app.schemas.outcome import OutcomeCreate, OutcomeResponse
from app.services.analysis_service import record_outcome


async def submit_outcome(analysis_id: str, outcome_in: OutcomeCreate) -> OutcomeResponse:
    """Submit deployment outcome for an analysis."""
    return await record_outcome(analysis_id, outcome_in)
