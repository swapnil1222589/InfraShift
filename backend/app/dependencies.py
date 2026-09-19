"""Dependency injection helpers."""
from __future__ import annotations

from fastapi import Request

from app.core.security import get_request_id as _get_request_id
from app.repositories.analysis_repository import analysis_repository
from app.repositories.audit_repository import audit_repository
from app.repositories.project_repository import project_repository
from app.services.ai_service import ai_service
from app.services.cloudwatch_service import cloudwatch_service
from app.services.evidence_service import evidence_service
from app.services.github_service import github_service


def get_project_repository():  # noqa: ANN201
    return project_repository


def get_analysis_repository():  # noqa: ANN201
    return analysis_repository


def get_audit_repository():  # noqa: ANN201
    return audit_repository


def get_ai_service():  # noqa: ANN201
    return ai_service


def get_cloudwatch_service():  # noqa: ANN201
    return cloudwatch_service


def get_github_service():  # noqa: ANN201
    return github_service


def get_evidence_service():  # noqa: ANN201
    return evidence_service


def get_request_id(request: Request) -> str:
    return _get_request_id(request)
