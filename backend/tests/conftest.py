"""Shared test fixtures and configuration."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.repositories.analysis_repository import LocalAnalysisRepository, analysis_repository
from app.repositories.audit_repository import LocalAuditRepository, audit_repository
from app.repositories.project_repository import LocalProjectRepository, project_repository


def _reset_repos() -> None:
    """Clear all in-memory repos between tests."""
    if isinstance(project_repository, LocalProjectRepository):
        project_repository.clear()
    if isinstance(analysis_repository, LocalAnalysisRepository):
        analysis_repository.clear()
    if isinstance(audit_repository, LocalAuditRepository):
        audit_repository.clear()


@pytest.fixture(autouse=True)
def reset_repositories():
    """Automatically reset in-memory repositories before each test."""
    _reset_repos()
    yield
    _reset_repos()


@pytest.fixture
def client():
    """FastAPI test client."""
    from app.main import app  # noqa: PLC0415

    return TestClient(app)


@pytest.fixture
def project_payload() -> dict:
    return {
        "name": "Test App",
        "repo_url": "https://github.com/example/test-app",
        "default_branch": "main",
        "aws_region": "us-east-1",
    }


@pytest.fixture
def analysis_payload() -> dict:
    return {
        "pr_number": 42,
        "commit_sha": "abc1234def5678",
    }


@pytest.fixture
def created_project(client, project_payload):
    """Helper fixture: create a project and return its data."""
    resp = client.post("/api/v1/projects", json=project_payload)
    assert resp.status_code == 201
    return resp.json()
