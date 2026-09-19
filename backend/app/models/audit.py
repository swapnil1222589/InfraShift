"""Audit event model."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AuditEventModel(BaseModel):
    """Audit event stored to DynamoDB audit table."""

    event_id: str
    project_id: str | None = None
    analysis_id: str | None = None
    event_type: str
    timestamp: datetime
    metadata: dict[str, Any] = {}
