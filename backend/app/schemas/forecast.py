"""Forecast schemas."""
from __future__ import annotations

from typing import Annotated

from pydantic import Field

from app.schemas.common import InfraShiftBaseModel


class MetricPrediction(InfraShiftBaseModel):
    direction: str  # increase | decrease | stable
    percentage: float


class ForecastResponse(InfraShiftBaseModel):
    analysis_id: str
    predicted_impact: dict[str, MetricPrediction]
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    time_horizon: str
    signals: list[str]
    uncertainty: list[str]
    insufficient_evidence: bool = False
    is_mock: bool = False
