"""Tests for AWS service."""
from __future__ import annotations

import pytest

from app.services.aws_service import AWSService


def test_mock_aws_returns_resources():
    service = AWSService()
    resources = service.get_lambda_resources("test-repo")
    assert isinstance(resources, list)
    assert len(resources) > 0


def test_mock_aws_resources_are_marked_mock():
    service = AWSService()
    resources = service.get_lambda_resources("test-repo")
    for r in resources:
        assert r.is_mock is True


def test_mock_aws_resources_have_source():
    service = AWSService()
    resources = service.get_lambda_resources("test-repo")
    for r in resources:
        assert r.source == "aws"


def test_mock_aws_resources_not_insufficient():
    service = AWSService()
    resources = service.get_lambda_resources("test-repo")
    for r in resources:
        assert r.insufficient_evidence is False


def test_mock_aws_resources_have_raw_data():
    service = AWSService()
    resources = service.get_lambda_resources("test-repo")
    for r in resources:
        assert r.raw is not None
        assert "resource_type" in r.raw


@pytest.mark.aws
def test_live_aws_lambda_list():
    """Requires LIVE_AWS=true and valid AWS credentials."""
    from app.core.config import settings  # noqa: PLC0415

    if not settings.LIVE_AWS:
        pytest.skip("LIVE_AWS=false — skipping real AWS test")

    service = AWSService()
    resources = service.get_lambda_resources("test")
    # Just verify it returns a list (may be empty if no lambdas)
    assert isinstance(resources, list)
