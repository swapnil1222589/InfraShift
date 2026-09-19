"""Project schemas."""
from __future__ import annotations

import re
from datetime import datetime

from pydantic import field_validator

from app.schemas.common import InfraShiftBaseModel

_VALID_REGION_RE = re.compile(r"^[a-z]{2}-[a-z]+-\d$")
_VALID_REPO_URL_RE = re.compile(r"^https://github\.com/[\w.\-]+/[\w.\-]+/?$")


class ProjectCreate(InfraShiftBaseModel):
    name: str
    repo_url: str
    default_branch: str = "main"
    aws_region: str = "us-east-1"

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            msg = "Project name must not be empty"
            raise ValueError(msg)
        if len(v) > 100:
            msg = "Project name must be 100 characters or fewer"
            raise ValueError(msg)
        return v

    @field_validator("repo_url")
    @classmethod
    def repo_url_valid(cls, v: str) -> str:
        v = v.strip()
        if not _VALID_REPO_URL_RE.match(v):
            msg = "repo_url must be a valid GitHub repository URL (https://github.com/owner/repo)"
            raise ValueError(msg)
        return v.rstrip("/")

    @field_validator("default_branch")
    @classmethod
    def branch_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            msg = "default_branch must not be empty"
            raise ValueError(msg)
        return v

    @field_validator("aws_region")
    @classmethod
    def aws_region_valid(cls, v: str) -> str:
        v = v.strip()
        if not _VALID_REGION_RE.match(v):
            msg = f"aws_region '{v}' is not a valid AWS region (e.g. us-east-1)"
            raise ValueError(msg)
        return v


class ProjectResponse(InfraShiftBaseModel):
    project_id: str
    name: str
    repo_url: str
    default_branch: str
    aws_region: str
    created_at: datetime
    updated_at: datetime
