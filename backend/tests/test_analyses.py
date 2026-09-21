"""Tests for analyses API."""
from __future__ import annotations


def _create_project(client):
    resp = client.post("/api/v1/projects", json={
        "name": "Analyses Test App",
        "repo_url": "https://github.com/example/analyses-test",
        "default_branch": "main",
        "aws_region": "us-east-1",
    })
    assert resp.status_code == 201   
    return resp.json()["project_id"]


def _create_analysis(client, project_id, pr_number=42, commit_sha="abc1234"):
    resp = client.post(f"/api/v1/projects/{project_id}/analyses", json={
        "pr_number": pr_number,
        "commit_sha": commit_sha,
    })
    return resp


def test_create_analysis_returns_202(client):
    project_id = _create_project(client)
    resp = _create_analysis(client, project_id)
    assert resp.status_code == 202
    data = resp.json()
    assert "analysis_id" in data
    assert data["status"] == "QUEUED"


def test_get_analysis(client):
    project_id = _create_project(client)
    create_resp = _create_analysis(client, project_id)
    analysis_id = create_resp.json()["analysis_id"]

    # Background tasks run synchronously in TestClient
    resp = client.get(f"/api/v1/analyses/{analysis_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["analysis_id"] == analysis_id
    assert data["status"] in {"QUEUED", "RUNNING", "COMPLETED", "FAILED"}


def test_analysis_completes_in_local_mode(client):
    project_id = _create_project(client)
    create_resp = _create_analysis(client, project_id)
    analysis_id = create_resp.json()["analysis_id"]

    resp = client.get(f"/api/v1/analyses/{analysis_id}")
    assert resp.status_code == 200
    data = resp.json()
    # TestClient runs background tasks synchronously
    assert data["status"] == "COMPLETED"


def test_analysis_not_found(client):
    resp = client.get("/api/v1/analyses/nonexistent-id")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "ANALYSIS_NOT_FOUND"


def test_create_analysis_project_not_found(client):
    resp = client.post("/api/v1/projects/nonexistent/analyses", json={
        "pr_number": 1,
        "commit_sha": "abc123",
    })
    assert resp.status_code == 404


def test_duplicate_analysis_returns_409(client):
    project_id = _create_project(client)
    _create_analysis(client, project_id, pr_number=99, commit_sha="dup1234")
    resp2 = _create_analysis(client, project_id, pr_number=99, commit_sha="dup1234")
    assert resp2.status_code == 409
    assert resp2.json()["error"]["code"] == "ANALYSIS_ALREADY_EXISTS"


def test_get_impact(client):
    project_id = _create_project(client)
    create_resp = _create_analysis(client, project_id)
    analysis_id = create_resp.json()["analysis_id"]

    resp = client.get(f"/api/v1/analyses/{analysis_id}/impact")
    assert resp.status_code == 200
    data = resp.json()
    assert "overall_risk" in data
    assert "affected_resources" in data
    assert "categories" in data
    assert data["analysis_id"] == analysis_id


def test_get_forecast(client):
    project_id = _create_project(client)
    create_resp = _create_analysis(client, project_id)
    analysis_id = create_resp.json()["analysis_id"]

    resp = client.get(f"/api/v1/analyses/{analysis_id}/forecast")
    assert resp.status_code == 200
    data = resp.json()
    assert "confidence" in data
    assert 0.0 <= data["confidence"] <= 1.0
    assert "predicted_impact" in data
    assert data["is_mock"] is True


def test_get_evidence(client):
    project_id = _create_project(client)
    create_resp = _create_analysis(client, project_id)
    analysis_id = create_resp.json()["analysis_id"]

    resp = client.get(f"/api/v1/analyses/{analysis_id}/evidence")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert data["analysis_id"] == analysis_id


def test_get_recommendations(client):
    project_id = _create_project(client)
    create_resp = _create_analysis(client, project_id)
    analysis_id = create_resp.json()["analysis_id"]

    resp = client.get(f"/api/v1/analyses/{analysis_id}/recommendations")
    assert resp.status_code == 200
    data = resp.json()
    assert "recommendations" in data
    assert len(data["recommendations"]) > 0


def test_create_analysis_invalid_pr_number(client):
    project_id = _create_project(client)
    resp = client.post(f"/api/v1/projects/{project_id}/analyses", json={
        "pr_number": 0,
        "commit_sha": "abc123",
    })
    assert resp.status_code == 422


def test_create_analysis_empty_commit_sha(client):
    project_id = _create_project(client)
    resp = client.post(f"/api/v1/projects/{project_id}/analyses", json={
        "pr_number": 1,
        "commit_sha": "",
    })
    assert resp.status_code == 422
