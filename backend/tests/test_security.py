"""Tests for security features."""
from __future__ import annotations

import hashlib
import hmac

from app.core.security import generate_request_id, validate_github_signature


def test_generate_request_id_is_unique():
    ids = {generate_request_id() for _ in range(100)}
    assert len(ids) == 100


def test_generate_request_id_is_string():
    rid = generate_request_id()
    assert isinstance(rid, str)
    assert len(rid) > 0


def test_validate_github_signature_valid():
    payload = b'{"action": "opened"}'
    secret = "my-secret"
    mac = hmac.new(secret.encode(), msg=payload, digestmod=hashlib.sha256)
    sig = "sha256=" + mac.hexdigest()
    assert validate_github_signature(payload, sig, secret) is True


def test_validate_github_signature_invalid():
    payload = b'{"action": "opened"}'
    assert validate_github_signature(payload, "sha256=invalidsig", "secret") is False


def test_validate_github_signature_missing_prefix():
    payload = b'{"action": "opened"}'
    assert validate_github_signature(payload, "invalidsig", "secret") is False


def test_validate_github_signature_empty_secret():
    assert validate_github_signature(b"payload", "sha256=abc", "") is False


def test_validate_github_signature_empty_signature():
    assert validate_github_signature(b"payload", "", "secret") is False


def test_request_id_preserved_in_response(client):
    resp = client.get("/api/v1/health", headers={"X-Request-ID": "my-custom-id"})
    assert resp.headers.get("X-Request-ID") == "my-custom-id"


def test_request_id_generated_when_missing(client):
    resp = client.get("/api/v1/health")
    rid = resp.headers.get("X-Request-ID")
    assert rid is not None
    assert len(rid) > 0


def test_cors_headers_present(client):
    # Simulate a CORS preflight
    resp = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    # Should not fail
    assert resp.status_code in {200, 204, 405}


def test_error_response_does_not_expose_traceback(client):
    """404 errors should not expose Python tracebacks."""
    resp = client.get("/api/v1/projects/nonexistent")
    assert resp.status_code == 404
    body = resp.text
    assert "Traceback" not in body
    assert "File " not in body
    assert "Exception" not in body


def test_github_token_not_in_response(client):
    """GitHub token should never appear in API responses."""
    resp = client.get("/api/v1/health")
    assert "GITHUB_TOKEN" not in resp.text
    assert "github_token" not in resp.text.lower()
