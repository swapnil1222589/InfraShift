"""Security utilities for InfraShift."""
from __future__ import annotations

import hashlib
import hmac
import logging
import uuid

from fastapi import Request

logger = logging.getLogger(__name__)


def generate_request_id() -> str:
    """Generate a unique request ID."""
    return str(uuid.uuid4())


def validate_github_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Validate GitHub webhook HMAC-SHA256 signature using constant-time comparison.

    Args:
        payload: Raw request body bytes.
        signature: Value of X-Hub-Signature-256 header (format: 'sha256=<hex>').
        secret: The configured webhook secret.

    Returns:
        True if the signature is valid, False otherwise.
    """
    if not signature or not secret:
        return False
    if not signature.startswith("sha256="):
        return False

    mac = hmac.new(
        secret.encode("utf-8"),
        msg=payload,
        digestmod=hashlib.sha256,
    )
    expected = "sha256=" + mac.hexdigest()

    return hmac.compare_digest(expected, signature)


def get_request_id(request: Request) -> str:
    """Get the request ID from request state (set by middleware)."""
    return getattr(request.state, "request_id", "-")
