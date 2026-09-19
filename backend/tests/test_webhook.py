"""Tests for GitHub webhook endpoint."""
from __future__ import annotations

import hashlib
import hmac
import json

from app.core.config import settings


def _make_signature(payload: bytes, secret: str) -> str:
    mac = hmac.new(secret.encode(), msg=payload, digestmod=hashlib.sha256)
    return "sha256=" + mac.hexdigest()


def _pr_payload(action: str = "opened", pr_number: int = 1, sha: str = "abc123", repo: str = "example/test-repo") -> dict:
    return {
        "action": action,
        "pull_request": {
            "number": pr_number,
            "title": "Test PR",
            "head": {"sha": sha},
        },
        "repository": {
            "full_name": repo,
            "html_url": f"https://github.com/{repo}",
            "owner": {"login": "example"},
        },
    }


def _create_project(client, repo: str = "example/test-repo"):
    resp = client.post("/api/v1/projects", json={
        "name": "Webhook Test App",
        "repo_url": f"https://github.com/{repo}",
        "default_branch": "main",
        "aws_region": "us-east-1",
    })
    assert resp.status_code == 201
    return resp.json()


def test_webhook_valid_event_no_project_returns_404(client):
    payload = _pr_payload()
    resp = client.post(
        "/api/v1/github/webhook",
        json=payload,
        headers={"X-GitHub-Event": "pull_request"},
    )
    assert resp.status_code == 404


def test_webhook_valid_event_with_project_queues_analysis(client):
    _create_project(client)
    payload = _pr_payload()
    resp = client.post(
        "/api/v1/github/webhook",
        json=payload,
        headers={"X-GitHub-Event": "pull_request"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "queued"
    assert "analysis_id" in data


def test_webhook_supported_actions(client):
    for action in ["opened", "synchronize", "reopened"]:
        _create_project(client, repo=f"example/{action}-repo")
        payload = _pr_payload(action=action, repo=f"example/{action}-repo")
        resp = client.post(
            "/api/v1/github/webhook",
            json=payload,
            headers={"X-GitHub-Event": "pull_request"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] in {"queued", "duplicate"}


def test_webhook_unsupported_action_returns_ignored(client):
    payload = _pr_payload(action="closed")
    resp = client.post(
        "/api/v1/github/webhook",
        json=payload,
        headers={"X-GitHub-Event": "pull_request"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "ignored"


def test_webhook_unsupported_event_type_returns_ignored(client):
    resp = client.post(
        "/api/v1/github/webhook",
        json={"action": "created"},
        headers={"X-GitHub-Event": "issues"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "ignored"


def test_webhook_invalid_signature_returns_403(client):
    original_secret = settings.GITHUB_WEBHOOK_SECRET
    settings.GITHUB_WEBHOOK_SECRET = "test-secret-123"
    try:
        payload = json.dumps(_pr_payload()).encode()
        resp = client.post(
            "/api/v1/github/webhook",
            content=payload,
            headers={
                "X-GitHub-Event": "pull_request",
                "X-Hub-Signature-256": "sha256=invalidsignature",
                "Content-Type": "application/json",
            },
        )
        assert resp.status_code == 403
    finally:
        settings.GITHUB_WEBHOOK_SECRET = original_secret


def test_webhook_valid_signature_accepted(client):
    original_secret = settings.GITHUB_WEBHOOK_SECRET
    settings.GITHUB_WEBHOOK_SECRET = "test-secret-123"
    try:
        _create_project(client)
        payload = json.dumps(_pr_payload()).encode()
        sig = _make_signature(payload, "test-secret-123")
        resp = client.post(
            "/api/v1/github/webhook",
            content=payload,
            headers={
                "X-GitHub-Event": "pull_request",
                "X-Hub-Signature-256": sig,
                "Content-Type": "application/json",
            },
        )
        # Should be queued (project exists)
        assert resp.status_code == 200
        assert resp.json()["status"] == "queued"
    finally:
        settings.GITHUB_WEBHOOK_SECRET = original_secret


def test_webhook_missing_signature_when_secret_set_returns_401(client):
    original_secret = settings.GITHUB_WEBHOOK_SECRET
    settings.GITHUB_WEBHOOK_SECRET = "test-secret-123"
    try:
        payload = json.dumps(_pr_payload()).encode()
        resp = client.post(
            "/api/v1/github/webhook",
            content=payload,
            headers={
                "X-GitHub-Event": "pull_request",
                "Content-Type": "application/json",
            },
        )
        assert resp.status_code == 401
    finally:
        settings.GITHUB_WEBHOOK_SECRET = original_secret


def test_webhook_idempotency_same_commit(client):
    _create_project(client)
    payload = _pr_payload(pr_number=55, sha="idemp123")

    resp1 = client.post(
        "/api/v1/github/webhook",
        json=payload,
        headers={"X-GitHub-Event": "pull_request"},
    )
    assert resp1.status_code == 200
    assert resp1.json()["status"] == "queued"

    resp2 = client.post(
        "/api/v1/github/webhook",
        json=payload,
        headers={"X-GitHub-Event": "pull_request"},
    )
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "duplicate"
