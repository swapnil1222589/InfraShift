"""Analysis service — business logic layer."""
from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime

from app.core.errors import ConflictError, InvalidStateTransitionError, NotFoundError
from app.models.analysis import AnalysisModel
from app.repositories.analysis_repository import analysis_repository
from app.schemas.analysis import (
    AnalysisCreate,
    AnalysisResponse,
    AnalysisStatus,
)
from app.schemas.evidence import EvidenceItem
from app.schemas.forecast import ForecastResponse
from app.schemas.impact import ImpactResponse
from app.schemas.outcome import OutcomeCreate, OutcomeResponse
from app.schemas.recommendation import Recommendation

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _model_to_response(model: AnalysisModel) -> AnalysisResponse:
    """Convert storage model to API response schema."""
    impact = ImpactResponse(**model.impact) if model.impact else None
    forecast = ForecastResponse(**model.forecast) if model.forecast else None
    evidence = [EvidenceItem(**e) for e in model.evidence] if model.evidence else None
    recommendations = [Recommendation(**r) for r in model.recommendations] if model.recommendations else None
    outcome = OutcomeResponse(**model.outcome) if model.outcome else None

    return AnalysisResponse(
        analysis_id=model.analysis_id,
        project_id=model.project_id,
        pr_number=model.pr_number,
        commit_sha=model.commit_sha,
        status=model.status,
        created_at=model.created_at,
        updated_at=model.updated_at,
        completed_at=model.completed_at,
        error=model.error,
        impact=impact,
        forecast=forecast,
        evidence=evidence,
        recommendations=recommendations,
        outcome=outcome,
    )


# ---------------------------------------------------------------------------
# Service functions
# ---------------------------------------------------------------------------


async def create_analysis(project_id: str, analysis_in: AnalysisCreate) -> AnalysisModel:
    """
    Create a new analysis with idempotency check.
    Raises ConflictError if same (project_id, pr_number, commit_sha) already exists.
    """
    existing = await analysis_repository.find_duplicate(
        project_id, analysis_in.pr_number, analysis_in.commit_sha
    )
    if existing:
        logger.info(
            "Duplicate analysis detected: analysis_id=%s project_id=%s pr=%d sha=%s",
            existing.analysis_id, project_id, analysis_in.pr_number, analysis_in.commit_sha,
        )
        raise ConflictError(
            f"Analysis already exists for PR #{analysis_in.pr_number} commit {analysis_in.commit_sha}",
            error_code="ANALYSIS_ALREADY_EXISTS",
        )

    now = datetime.now(UTC)
    model = AnalysisModel(
        analysis_id=str(uuid.uuid4()),
        project_id=project_id,
        pr_number=analysis_in.pr_number,
        commit_sha=analysis_in.commit_sha,
        status=AnalysisStatus.QUEUED,
        created_at=now,
        updated_at=now,
    )

    await analysis_repository.save(model)
    logger.info(
        "Analysis created: analysis_id=%s project_id=%s pr=%d sha=%s",
        model.analysis_id, project_id, analysis_in.pr_number, analysis_in.commit_sha,
    )
    return model


async def get_analysis(analysis_id: str) -> AnalysisResponse:
    """Get analysis by ID. Raises NotFoundError if not found."""
    model = await analysis_repository.get(analysis_id)
    if not model:
        raise NotFoundError(f"Analysis not found: {analysis_id}", error_code="ANALYSIS_NOT_FOUND")
    return _model_to_response(model)


async def get_project_history(project_id: str) -> list[AnalysisResponse]:
    """Get all analyses for a project."""
    models = await analysis_repository.get_by_project(project_id)
    return [_model_to_response(m) for m in models]


async def transition_status(
    model: AnalysisModel,
    new_status: AnalysisStatus,
) -> AnalysisModel:
    """Transition analysis status with validation."""
    if not model.status.can_transition_to(new_status):
        raise InvalidStateTransitionError(
            f"Cannot transition from {model.status} to {new_status}"
        )
    model.status = new_status
    model.updated_at = datetime.now(UTC)
    await analysis_repository.save(model)
    return model


async def record_outcome(analysis_id: str, outcome_in: OutcomeCreate) -> OutcomeResponse:
    """Record deployment outcome for an analysis."""
    model = await analysis_repository.get(analysis_id)
    if not model:
        raise NotFoundError(f"Analysis not found: {analysis_id}", error_code="ANALYSIS_NOT_FOUND")

    now = datetime.now(UTC)
    outcome = OutcomeResponse(
        outcome_id=str(uuid.uuid4()),
        analysis_id=analysis_id,
        deployment_id=outcome_in.deployment_id,
        deployment_status=outcome_in.deployment_status,
        observed_metrics=outcome_in.observed_metrics,
        notes=outcome_in.notes,
        recorded_at=now,
    )

    # Persist outcome into analysis model
    model.outcome = outcome.model_dump(mode="json")
    model.updated_at = now
    await analysis_repository.save(model)

    logger.info(
        "Outcome recorded: analysis_id=%s deployment_id=%s status=%s",
        analysis_id, outcome_in.deployment_id, outcome_in.deployment_status,
    )
    return outcome
