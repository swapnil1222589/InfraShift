"""Tests for repositories."""
from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.models.analysis import AnalysisModel
from app.models.audit import AuditEventModel
from app.models.project import ProjectModel
from app.repositories.analysis_repository import LocalAnalysisRepository
from app.repositories.audit_repository import LocalAuditRepository
from app.repositories.project_repository import LocalProjectRepository
from app.schemas.analysis import AnalysisStatus


def _make_project(project_id: str = "proj-1", repo_url: str = "https://github.com/example/app") -> ProjectModel:
    now = datetime.now(UTC)
    return ProjectModel(
        project_id=project_id,
        name="Test Project",
        repo_url=repo_url,
        default_branch="main",
        aws_region="us-east-1",
        created_at=now,
        updated_at=now,
    )


def _make_analysis(
    analysis_id: str = "ana-1",
    project_id: str = "proj-1",
    pr_number: int = 1,
    commit_sha: str = "abc123",
) -> AnalysisModel:
    now = datetime.now(UTC)
    return AnalysisModel(
        analysis_id=analysis_id,
        project_id=project_id,
        pr_number=pr_number,
        commit_sha=commit_sha,
        status=AnalysisStatus.QUEUED,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_project_save_and_get():
    repo = LocalProjectRepository()
    project = _make_project()
    await repo.save(project)
    result = await repo.get(project.project_id)
    assert result is not None
    assert result.project_id == project.project_id


@pytest.mark.asyncio
async def test_project_get_not_found():
    repo = LocalProjectRepository()
    result = await repo.get("nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_project_get_by_repo_url():
    repo = LocalProjectRepository()
    project = _make_project(repo_url="https://github.com/example/myapp")
    await repo.save(project)
    result = await repo.get_by_repo_url("https://github.com/example/myapp")
    assert result is not None
    assert result.project_id == project.project_id


@pytest.mark.asyncio
async def test_project_get_by_repo_url_not_found():
    repo = LocalProjectRepository()
    result = await repo.get_by_repo_url("https://github.com/nobody/nowhere")
    assert result is None


@pytest.mark.asyncio
async def test_analysis_save_and_get():
    repo = LocalAnalysisRepository()
    analysis = _make_analysis()
    await repo.save(analysis)
    result = await repo.get(analysis.analysis_id)
    assert result is not None
    assert result.analysis_id == analysis.analysis_id


@pytest.mark.asyncio
async def test_analysis_get_by_project():
    repo = LocalAnalysisRepository()
    a1 = _make_analysis(analysis_id="a1", project_id="proj-1")
    a2 = _make_analysis(analysis_id="a2", project_id="proj-1")
    a3 = _make_analysis(analysis_id="a3", project_id="proj-2")
    await repo.save(a1)
    await repo.save(a2)
    await repo.save(a3)
    results = await repo.get_by_project("proj-1")
    assert len(results) == 2
    ids = {r.analysis_id for r in results}
    assert "a1" in ids
    assert "a2" in ids


@pytest.mark.asyncio
async def test_analysis_find_duplicate():
    repo = LocalAnalysisRepository()
    analysis = _make_analysis(project_id="proj-1", pr_number=42, commit_sha="sha123")
    await repo.save(analysis)
    duplicate = await repo.find_duplicate("proj-1", 42, "sha123")
    assert duplicate is not None
    assert duplicate.analysis_id == analysis.analysis_id


@pytest.mark.asyncio
async def test_analysis_find_no_duplicate():
    repo = LocalAnalysisRepository()
    analysis = _make_analysis(project_id="proj-1", pr_number=42, commit_sha="sha123")
    await repo.save(analysis)
    no_dup = await repo.find_duplicate("proj-1", 99, "sha123")
    assert no_dup is None


@pytest.mark.asyncio
async def test_audit_save_and_query():
    repo = LocalAuditRepository()
    event = AuditEventModel(
        event_id="ev-1",
        project_id="proj-1",
        analysis_id="ana-1",
        event_type="ANALYSIS_STARTED",
        timestamp=datetime.now(UTC),
        metadata={},
    )
    await repo.save(event)
    results = await repo.get_by_analysis("ana-1")
    assert len(results) == 1
    assert results[0].event_type == "ANALYSIS_STARTED"


@pytest.mark.asyncio
async def test_audit_multiple_events():
    repo = LocalAuditRepository()
    for et in ["ANALYSIS_STARTED", "GITHUB_FETCHED", "ANALYSIS_COMPLETED"]:
        await repo.save(AuditEventModel(
            event_id=f"ev-{et}",
            project_id="proj-1",
            analysis_id="ana-1",
            event_type=et,
            timestamp=datetime.now(UTC),
            metadata={},
        ))
    results = await repo.get_by_analysis("ana-1")
    assert len(results) == 3
