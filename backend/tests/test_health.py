"""Tests for health endpoints."""
from __future__ import annotations


def test_health_check(client):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "infrashift-backend"
    assert "environment" in data
    assert "request_id" in data


def test_health_check_request_id_preserved(client):
    resp = client.get("/api/v1/health", headers={"X-Request-ID": "test-id-123"})
    assert resp.status_code == 200
    assert resp.headers.get("X-Request-ID") == "test-id-123"


def test_health_check_request_id_generated(client):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert "X-Request-ID" in resp.headers


def test_aws_health_local_mode(client):
    """In local mode (LIVE_AWS=false), should return local status without connecting to AWS."""
    resp = client.get("/api/v1/health/aws")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "local"
    assert data["aws_enabled"] is False
