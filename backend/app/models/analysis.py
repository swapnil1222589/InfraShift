"""DynamoDB / in-memory analysis model."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.schemas.analysis import AnalysisStatus


class AnalysisModel(BaseModel):
    """Raw storage model for an analysis."""

    analysis_id: str
    project_id: str
    pr_number: int
    commit_sha: str
    status: AnalysisStatus = AnalysisStatus.QUEUED
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None
    error: str | None = None
    # Stored as raw dicts — deserialized when served
    impact: dict[str, Any] | None = None
    forecast: dict[str, Any] | None = None
    evidence: list[dict[str, Any]] | None = None
    recommendations: list[dict[str, Any]] | None = None
    outcome: dict[str, Any] | None = None
