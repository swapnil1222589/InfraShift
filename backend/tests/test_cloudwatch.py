"""Tests for CloudWatch service."""
from __future__ import annotations

import pytest

from app.schemas.evidence import EvidenceItem
from app.services.cloudwatch_service import CloudWatchService


@pytest.mark.asyncio
async def test_mock_cloudwatch_returns_metrics():
    service = CloudWatchService()
    metrics = await service.get_lambda_metrics("test-function")
    assert isinstance(metrics, list)
    assert len(metrics) > 0


@pytest.mark.asyncio
async def test_mock_cloudwatch_is_marked_mock():
    service = CloudWatchService()
    metrics = await service.get_lambda_metrics("test-function")
    for m in metrics:
        assert m.is_mock is True


@pytest.mark.asyncio
async def test_mock_cloudwatch_has_no_insufficient_evidence():
    service = CloudWatchService()
    metrics = await service.get_lambda_metrics("test-function")
    for m in metrics:
        assert m.insufficient_evidence is False


@pytest.mark.asyncio
async def test_mock_cloudwatch_returns_evidence_items():
    service = CloudWatchService()
    metrics = await service.get_lambda_metrics("test-function")
    for m in metrics:
        assert isinstance(m, EvidenceItem)
        assert m.source == "cloudwatch"


@pytest.mark.asyncio
async def test_mock_cloudwatch_has_value():
    service = CloudWatchService()
    metrics = await service.get_lambda_metrics("test-function")
    # At least invocations should have a value > 0
    invocations = [m for m in metrics if m.metric == "Invocations"]
    assert len(invocations) > 0
    assert invocations[0].value is not None
    assert invocations[0].value > 0


@pytest.mark.asyncio
async def test_mock_cloudwatch_custom_days():
    service = CloudWatchService()
    metrics = await service.get_lambda_metrics("test-function", days=14)
    assert len(metrics) > 0
    # Verify start_time is approximately 14 days ago
    for m in metrics:
        if m.start_time and m.end_time:
            delta = m.end_time - m.start_time
            assert abs(delta.days - 14) <= 1
