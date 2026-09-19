"""Tests for the analysis worker."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch


def _create_project_and_analysis(client):
    proj = client.post("/api/v1/projects", json={
        "name": "Worker Test App",
        "repo_url": "https://github.com/example/worker-test",
        "default_branch": "main",
        "aws_region": "us-east-1",
    })
    assert proj.status_code == 201
    project_id = proj.json()["project_id"]

    ana = client.post(f"/api/v1/projects/{project_id}/analyses", json={
        "pr_number": 1,
        "commit_sha": "test123",
    })
    assert ana.status_code == 202
    return project_id, ana.json()["analysis_id"]


def test_worker_completes_in_local_mode(client):
    project_id, analysis_id = _create_project_and_analysis(client)
    resp = client.get(f"/api/v1/analyses/{analysis_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "COMPLETED"
    assert data["impact"] is not None
    assert data["forecast"] is not None
    assert data["recommendations"] is not None


def test_worker_sets_completed_at(client):
    project_id, analysis_id = _create_project_and_analysis(client)
    resp = client.get(f"/api/v1/analyses/{analysis_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["completed_at"] is not None


def test_worker_github_failure_sets_failed(client):
    """If GitHub service raises, analysis should be FAILED."""
    with patch("app.services.evidence_service.github_service.get_pr_files", new_callable=AsyncMock) as mock_gh:
        mock_gh.side_effect = RuntimeError("GitHub API down")
        project_id, analysis_id = _create_project_and_analysis(client)

    resp = client.get(f"/api/v1/analyses/{analysis_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "FAILED"
    assert data["error"] is not None


def test_worker_ai_failure_sets_failed(client):
    """If AI service raises, analysis should be FAILED."""
    with patch("app.services.ai_service.MockAIService.analyze", new_callable=AsyncMock) as mock_ai:
        mock_ai.side_effect = ValueError("AI exploded")
        project_id, analysis_id = _create_project_and_analysis(client)

    resp = client.get(f"/api/v1/analyses/{analysis_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "FAILED"


def test_worker_impact_has_correct_schema(client):
    project_id, analysis_id = _create_project_and_analysis(client)
    resp = client.get(f"/api/v1/analyses/{analysis_id}/impact")
    assert resp.status_code == 200
    data = resp.json()
    assert data["overall_risk"] in {"low", "medium", "high", "critical"}
    assert isinstance(data["affected_resources"], list)
    assert "categories" in data


def test_worker_forecast_has_correct_schema(client):
    project_id, analysis_id = _create_project_and_analysis(client)
    resp = client.get(f"/api/v1/analyses/{analysis_id}/forecast")
    assert resp.status_code == 200
    data = resp.json()
    assert 0.0 <= data["confidence"] <= 1.0
    assert "predicted_impact" in data
    assert "signals" in data
    assert data["is_mock"] is True
