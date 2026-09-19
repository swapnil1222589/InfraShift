"""GitHub webhook schemas."""
from __future__ import annotations

from typing import Any

from app.schemas.common import InfraShiftBaseModel


class GitHubRepo(InfraShiftBaseModel):
    full_name: str
    html_url: str | None = None
    clone_url: str | None = None


class GitHubPR(InfraShiftBaseModel):
    number: int
    title: str | None = None
    head_sha: str  # head.sha


class WebhookPayload(InfraShiftBaseModel):
    action: str
    pull_request: dict[str, Any]
    repository: dict[str, Any]


class PRFile(InfraShiftBaseModel):
    filename: str
    status: str
    additions: int = 0
    deletions: int = 0
    changes: int = 0
    patch: str | None = None
