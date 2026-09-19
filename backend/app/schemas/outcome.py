"""Outcome schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import field_validator

from app.schemas.common import InfraShiftBaseModel

VALID_DEPLOYMENT_STATUSES = {"success", "failure", "partial", "rollback"}


class ObservedMetrics(InfraShiftBaseModel):
    invocations: float | None = None
    errors: float | None = None
    duration_ms: float | None = None
    extra: dict[str, Any] | None = None


class OutcomeCreate(InfraShiftBaseModel):
    deployment_id: str
    deployment_status: str
    observed_metrics: ObservedMetrics | None = None
    notes: str | None = None

    @field_validator("deployment_status")
    @classmethod
    def status_valid(cls, v: str) -> str:
        v = v.lower().strip()
        if v not in VALID_DEPLOYMENT_STATUSES:
            msg = f"deployment_status must be one of {sorted(VALID_DEPLOYMENT_STATUSES)}"
            raise ValueError(msg)
        return v


class OutcomeResponse(InfraShiftBaseModel):
    outcome_id: str
    analysis_id: str
    deployment_id: str
    deployment_status: str
    observed_metrics: ObservedMetrics | None = None
    notes: str | None = None
    recorded_at: datetime
