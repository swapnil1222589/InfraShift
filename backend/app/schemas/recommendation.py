"""Recommendation schemas."""
from __future__ import annotations

from enum import Enum

from app.schemas.common import InfraShiftBaseModel


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Recommendation(InfraShiftBaseModel):
    id: str
    priority: Priority
    category: str
    title: str
    description: str
    reason: str
    evidence_refs: list[str] = []


class RecommendationsResponse(InfraShiftBaseModel):
    analysis_id: str
    recommendations: list[Recommendation]
