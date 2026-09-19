"""Analyses API endpoints."""
from __future__ import annotations

import logging

from fastapi import APIRouter, BackgroundTasks, status

from app.core.errors import NotFoundError
from app.schemas.analysis import (
    AnalysisCreate,
    AnalysisCreatedResponse,
    AnalysisResponse,
    AnalysisStatus,
)
from app.schemas.evidence import EvidenceResponse
from app.schemas.forecast import ForecastResponse
from app.schemas.impact import ImpactResponse
from app.schemas.outcome import OutcomeCreate, OutcomeResponse
from app.schemas.recommendation import RecommendationsResponse
from app.services.analysis_service import create_analysis, get_analysis, record_outcome
from app.services.project_service import get_project
from app.workers.analysis_worker import run_analysis

logger = logging.getLogger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Create analysis (under projects)
# ---------------------------------------------------------------------------


async def start_analysis_for_project(
    project_id: str,
    analysis_in: AnalysisCreate,
    background_tasks: BackgroundTasks,
) -> AnalysisCreatedResponse:
    """Create and queue an analysis for a project."""
    # Ensure project exists
    await get_project(project_id)

    model = await create_analysis(project_id, analysis_in)
    background_tasks.add_task(run_analysis, model.analysis_id)

    return AnalysisCreatedResponse(
        analysis_id=model.analysis_id,
        status=AnalysisStatus.QUEUED,
    )


# ---------------------------------------------------------------------------
# Analysis endpoints (mounted at /api/v1/analyses)
# ---------------------------------------------------------------------------


@router.get(
    "/{analysis_id}",
    response_model=AnalysisResponse,
    summary="Get full analysis",
)
async def read_analysis(analysis_id: str) -> AnalysisResponse:
    return await get_analysis(analysis_id)


@router.get(
    "/{analysis_id}/impact",
    response_model=ImpactResponse,
    summary="Get infrastructure impact",
)
async def get_impact(analysis_id: str) -> ImpactResponse:
    analysis = await get_analysis(analysis_id)
    if analysis.impact is None:
        raise NotFoundError(
            f"Impact not yet available for analysis {analysis_id}. Current status: {analysis.status}",
            error_code="IMPACT_NOT_AVAILABLE",
        )
    return analysis.impact


@router.get(
    "/{analysis_id}/forecast",
    response_model=ForecastResponse,
    summary="Get forecast",
)
async def get_forecast(analysis_id: str) -> ForecastResponse:
    analysis = await get_analysis(analysis_id)
    if analysis.forecast is None:
        raise NotFoundError(
            f"Forecast not yet available for analysis {analysis_id}. Current status: {analysis.status}",
            error_code="FORECAST_NOT_AVAILABLE",
        )
    return analysis.forecast


@router.get(
    "/{analysis_id}/evidence",
    response_model=EvidenceResponse,
    summary="Get collected evidence",
)
async def get_evidence(analysis_id: str) -> EvidenceResponse:
    analysis = await get_analysis(analysis_id)
    evidence_items = analysis.evidence or []
    is_mock = any(getattr(e, "is_mock", False) for e in evidence_items)
    insufficient = all(getattr(e, "insufficient_evidence", False) for e in evidence_items) if evidence_items else True
    return EvidenceResponse(
        analysis_id=analysis_id,
        items=evidence_items,
        is_mock=is_mock,
        insufficient_evidence=insufficient,
    )


@router.get(
    "/{analysis_id}/recommendations",
    response_model=RecommendationsResponse,
    summary="Get recommendations",
)
async def get_recommendations(analysis_id: str) -> RecommendationsResponse:
    analysis = await get_analysis(analysis_id)
    return RecommendationsResponse(
        analysis_id=analysis_id,
        recommendations=analysis.recommendations or [],
    )


@router.post(
    "/{analysis_id}/outcome",
    response_model=OutcomeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record deployment outcome",
)
async def create_outcome(analysis_id: str, outcome_in: OutcomeCreate) -> OutcomeResponse:
    return await record_outcome(analysis_id, outcome_in)
