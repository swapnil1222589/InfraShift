"""Tests for projects API."""
from __future__ import annotations


def test_create_project(client, project_payload):
    resp = client.post("/api/v1/projects", json=project_payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == project_payload["name"]
    assert data["repo_url"] == project_payload["repo_url"]
    assert data["default_branch"] == project_payload["default_branch"]
    assert data["aws_region"] == project_payload["aws_region"]
    assert "project_id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_project_duplicate_repo_returns_409(client, project_payload):
    client.post("/api/v1/projects", json=project_payload)
    resp = client.post("/api/v1/projects", json=project_payload)
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "PROJECT_ALREADY_EXISTS"


def test_get_project(client, created_project):
    project_id = created_project["project_id"]
    resp = client.get(f"/api/v1/projects/{project_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["project_id"] == project_id


def test_get_project_not_found(client):
    resp = client.get("/api/v1/projects/nonexistent-id")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "PROJECT_NOT_FOUND"


def test_create_project_invalid_repo_url(client):
    payload = {
        "name": "Bad Project",
        "repo_url": "not-a-valid-url",
        "default_branch": "main",
        "aws_region": "us-east-1",
    }
    resp = client.post("/api/v1/projects", json=payload)
    assert resp.status_code == 422


def test_create_project_invalid_aws_region(client):
    payload = {
        "name": "Bad Region",
        "repo_url": "https://github.com/example/repo",
        "default_branch": "main",
        "aws_region": "invalid-region",
    }
    resp = client.post("/api/v1/projects", json=payload)
    assert resp.status_code == 422


def test_create_project_empty_name(client):
    payload = {
        "name": "   ",
        "repo_url": "https://github.com/example/repo",
        "default_branch": "main",
        "aws_region": "us-east-1",
    }
    resp = client.post("/api/v1/projects", json=payload)
    assert resp.status_code == 422


def test_project_history_empty(client, created_project):
    project_id = created_project["project_id"]
    resp = client.get(f"/api/v1/projects/{project_id}/history")
    assert resp.status_code == 200
    assert resp.json() == []


def test_project_history_not_found(client):
    resp = client.get("/api/v1/projects/nonexistent-id/history")
    assert resp.status_code == 404
