"""Tests for GitHub service."""
from __future__ import annotations

import pytest

from app.services.github_service import GitHubService


@pytest.mark.asyncio
async def test_mock_pr_files():
    service = GitHubService()
    files = await service.get_pr_files("example/repo", 42)
    assert isinstance(files, list)
    assert len(files) > 0
    for f in files:
        assert "filename" in f


@pytest.mark.asyncio
async def test_mock_pr_metadata():
    service = GitHubService()
    meta = await service.get_pr_metadata("example/repo", 42)
    assert meta["is_mock"] is True
    assert meta["number"] == 42


@pytest.mark.asyncio
async def test_mock_pr_files_returns_expected_filenames():
    service = GitHubService()
    files = await service.get_pr_files("example/repo", 1)
    filenames = [f["filename"] for f in files]
    assert "src/lambda/handler.py" in filenames


@pytest.mark.asyncio
async def test_mock_pr_files_have_required_fields():
    service = GitHubService()
    files = await service.get_pr_files("example/repo", 1)
    for f in files:
        assert "filename" in f
        assert "status" in f
        assert "additions" in f
        assert "deletions" in f


@pytest.mark.asyncio
async def test_mock_pr_metadata_has_title():
    service = GitHubService()
    meta = await service.get_pr_metadata("example/repo", 5)
    assert "title" in meta
    assert len(meta["title"]) > 0
