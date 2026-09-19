"""Tests for AI service."""
from __future__ import annotations

import pytest

from app.schemas.analysis import AIResponseModel
from app.services.ai_service import MockAIService


@pytest.mark.asyncio
async def test_mock_ai_returns_valid_response():
    service = MockAIService()
    result = await service.analyze({"project_id": "test", "changed_files": []})
    assert isinstance(result, AIResponseModel)


@pytest.mark.asyncio
async def test_mock_ai_is_marked_as_mock():
    service = MockAIService()
    result = await service.analyze({})
    assert result.is_mock is True


@pytest.mark.asyncio
async def test_mock_ai_confidence_in_range():
    service = MockAIService()
    result = await service.analyze({})
    assert 0.0 <= result.confidence <= 1.0


@pytest.mark.asyncio
async def test_mock_ai_has_impact():
    service = MockAIService()
    result = await service.analyze({})
    assert result.impact is not None
    assert result.impact.overall_risk in {"low", "medium", "high", "critical"}


@pytest.mark.asyncio
async def test_mock_ai_has_forecast():
    service = MockAIService()
    result = await service.analyze({})
    assert result.forecast is not None
    assert 0.0 <= result.forecast.confidence <= 1.0


@pytest.mark.asyncio
async def test_mock_ai_has_recommendations():
    service = MockAIService()
    result = await service.analyze({})
    assert len(result.recommendations) > 0
    for rec in result.recommendations:
        assert rec.priority in {"low", "medium", "high", "critical"}


@pytest.mark.asyncio
async def test_mock_ai_not_insufficient_evidence():
    service = MockAIService()
    result = await service.analyze({})
    assert result.insufficient_evidence is False


@pytest.mark.asyncio
async def test_ai_response_model_rejects_invalid_confidence():
    """AIResponseModel must reject confidence outside [0, 1]."""
    with pytest.raises(Exception):
        AIResponseModel(
            impact={"overall_risk": "medium", "affected_resources": [], "categories": {}},
            forecast={
                "predicted_impact": {},
                "confidence": 1.5,  # invalid
                "time_horizon": "24h",
                "signals": [],
                "uncertainty": [],
            },
            recommendations=[],
            confidence=1.5,  # invalid
            is_mock=True,
        )
