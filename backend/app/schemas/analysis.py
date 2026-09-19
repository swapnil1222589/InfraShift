"""Analysis schemas."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated, Any

from pydantic import Field, field_validator

from app.schemas.common import InfraShiftBaseModel
from app.schemas.evidence import EvidenceItem
from app.schemas.forecast import ForecastResponse
from app.schemas.impact import ImpactResponse
from app.schemas.outcome import OutcomeResponse
from app.schemas.recommendation import Recommendation


class AnalysisStatus(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

    @classmethod
    def valid_transitions(cls) -> dict[AnalysisStatus, set[AnalysisStatus]]:
        return {
            cls.QUEUED: {cls.RUNNING},
            cls.RUNNING: {cls.COMPLETED, cls.FAILED},
            cls.COMPLETED: set(),
            cls.FAILED: set(),
        }

    def can_transition_to(self, target: AnalysisStatus) -> bool:
        return target in self.__class__.valid_transitions()[self]


class AnalysisCreate(InfraShiftBaseModel):
    pr_number: int
    commit_sha: str

    @field_validator("pr_number")
    @classmethod
    def pr_number_positive(cls, v: int) -> int:
        if v <= 0:
            msg = "pr_number must be a positive integer"
            raise ValueError(msg)
        return v

    @field_validator("commit_sha")
    @classmethod
    def commit_sha_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            msg = "commit_sha must not be empty"
            raise ValueError(msg)
        return v


class AnalysisResponse(InfraShiftBaseModel):
    analysis_id: str
    project_id: str
    pr_number: int
    commit_sha: str
    status: AnalysisStatus
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None
    error: str | None = None
    # Rich data populated after worker completes
    impact: ImpactResponse | None = None
    forecast: ForecastResponse | None = None
    evidence: list[EvidenceItem] | None = None
    recommendations: list[Recommendation] | None = None
    outcome: OutcomeResponse | None = None


class AnalysisCreatedResponse(InfraShiftBaseModel):
    analysis_id: str
    status: AnalysisStatus


# ---------------------------------------------------------------------------
# AI service models
# ---------------------------------------------------------------------------


class AIImpactModel(InfraShiftBaseModel):
    overall_risk: str = "medium"
    affected_resources: list[dict[str, Any]] = []
    categories: dict[str, str] = {}


class AIForecastModel(InfraShiftBaseModel):
    predicted_impact: dict[str, Any] = {}
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] = 0.5
    time_horizon: str = "24h"
    signals: list[str] = []
    uncertainty: list[str] = []
    insufficient_evidence: bool = False


class AIRecommendationModel(InfraShiftBaseModel):
    id: str
    priority: str
    category: str
    title: str
    description: str
    reason: str
    evidence_refs: list[str] = []


class AIResponseModel(InfraShiftBaseModel):
    """Validated AI service output. Never trust raw AI JSON — always validate this."""

    impact: AIImpactModel
    forecast: AIForecastModel
    recommendations: list[AIRecommendationModel]
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    evidence_summary: list[str] = []
    uncertainty: list[str] = []
    insufficient_evidence: bool = False
    is_mock: bool = True
