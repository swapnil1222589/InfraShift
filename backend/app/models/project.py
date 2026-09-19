"""DynamoDB / in-memory project model."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ProjectModel(BaseModel):
    """Raw storage model for a project."""

    project_id: str
    name: str
    repo_url: str
    default_branch: str
    aws_region: str
    created_at: datetime
    updated_at: datetime
