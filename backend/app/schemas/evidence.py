"""Evidence schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from app.schemas.common import InfraShiftBaseModel

VALID_SOURCES = {"github", "aws", "cloudwatch", "deployment", "ai"}


class EvidenceItem(InfraShiftBaseModel):
    source: str
    namespace: str | None = None
    metric: str | None = None
    value: float | None = None
    unit: str | None = None
    period: int | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    raw: dict[str, Any] | None = None
    is_mock: bool = False
    insufficient_evidence: bool = False


class EvidenceResponse(InfraShiftBaseModel):
    analysis_id: str
    items: list[EvidenceItem]
    is_mock: bool = False
    insufficient_evidence: bool = False
