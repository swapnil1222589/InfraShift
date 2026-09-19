"""Impact schemas."""
from __future__ import annotations

from enum import Enum

from app.schemas.common import InfraShiftBaseModel


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AffectedResource(InfraShiftBaseModel):
    resource_type: str
    resource_id: str
    change_type: str
    impact: RiskLevel


class ImpactCategories(InfraShiftBaseModel):
    compute: RiskLevel = RiskLevel.LOW
    database: RiskLevel = RiskLevel.LOW
    network: RiskLevel = RiskLevel.LOW
    api: RiskLevel = RiskLevel.LOW


class ImpactResponse(InfraShiftBaseModel):
    analysis_id: str
    overall_risk: RiskLevel
    affected_resources: list[AffectedResource]
    categories: ImpactCategories
    is_mock: bool = False
