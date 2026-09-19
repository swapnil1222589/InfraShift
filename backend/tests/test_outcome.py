"""Tests for outcome recording."""
from __future__ import annotations


def _setup(client, suffix: str = ""):
    unique = suffix or "default"
    proj = client.post("/api/v1/projects", json={
        "name": f"Outcome Test App {unique}",
        "repo_url": f"https://github.com/example/outcome-test-{unique}",
        "default_branch": "main",
        "aws_region": "us-east-1",
    })
    project_id = proj.json()["project_id"]
    ana = client.post(f"/api/v1/projects/{project_id}/analyses", json={
        "pr_number": 10,
        "commit_sha": "outcome123",
    })
    analysis_id = ana.json()["analysis_id"]
    return project_id, analysis_id


def test_record_outcome(client):
    project_id, analysis_id = _setup(client)
    resp = client.post(f"/api/v1/analyses/{analysis_id}/outcome", json={
        "deployment_id": "deploy-001",
        "deployment_status": "success",
        "observed_metrics": {
            "invocations": 1500,
            "errors": 12,
            "duration_ms": 210,
        },
        "notes": "Controlled rollout",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["analysis_id"] == analysis_id
    assert data["deployment_status"] == "success"
    assert "outcome_id" in data
    assert "recorded_at" in data


def test_outcome_appears_in_analysis(client):
    project_id, analysis_id = _setup(client)
    client.post(f"/api/v1/analyses/{analysis_id}/outcome", json={
        "deployment_id": "deploy-002",
        "deployment_status": "success",
    })
    resp = client.get(f"/api/v1/analyses/{analysis_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["outcome"] is not None
    assert data["outcome"]["deployment_id"] == "deploy-002"


def test_outcome_appears_in_history(client):
    project_id, analysis_id = _setup(client)
    client.post(f"/api/v1/analyses/{analysis_id}/outcome", json={
        "deployment_id": "deploy-003",
        "deployment_status": "success",
    })
    resp = client.get(f"/api/v1/projects/{project_id}/history")
    assert resp.status_code == 200
    history = resp.json()
    assert len(history) > 0
    # Find the analysis with outcome
    analysis_with_outcome = next(
        (a for a in history if a["analysis_id"] == analysis_id), None
    )
    assert analysis_with_outcome is not None
    assert analysis_with_outcome["outcome"] is not None


def test_outcome_invalid_status(client):
    project_id, analysis_id = _setup(client)
    resp = client.post(f"/api/v1/analyses/{analysis_id}/outcome", json={
        "deployment_id": "deploy-bad",
        "deployment_status": "invalid_status",
    })
    assert resp.status_code == 422


def test_outcome_analysis_not_found(client):
    resp = client.post("/api/v1/analyses/nonexistent/outcome", json={
        "deployment_id": "deploy-x",
        "deployment_status": "success",
    })
    assert resp.status_code == 404


def test_outcome_all_valid_statuses(client):
    for status_val in ["success", "failure", "partial", "rollback"]:
        project_id, analysis_id = _setup(client, suffix=status_val)
        resp = client.post(f"/api/v1/analyses/{analysis_id}/outcome", json={
            "deployment_id": f"deploy-{status_val}",
            "deployment_status": status_val,
        })
        assert resp.status_code == 201

