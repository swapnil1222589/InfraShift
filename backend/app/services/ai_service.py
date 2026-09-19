"""AI service — mock and real adapter interface."""
from __future__ import annotations

import logging
from typing import Any, Protocol

from pydantic import ValidationError

from app.core.config import settings
from app.schemas.analysis import (
    AIResponseModel,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Protocol (interface) — allows future Bedrock/other adapters without
# rewriting the API layer.
# ---------------------------------------------------------------------------


class AIServiceProtocol(Protocol):
    async def analyze(self, context: dict[str, Any]) -> AIResponseModel: ...


# ---------------------------------------------------------------------------
# Mock AI adapter
# ---------------------------------------------------------------------------

_MOCK_AI_RESPONSE: dict[str, Any] = {
    "impact": {
        "overall_risk": "medium",
        "affected_resources": [
            {
                "resource_type": "AWS::Lambda::Function",
                "resource_id": "demo-app-handler",
                "change_type": "modified",
                "impact": "medium",
            },
            {
                "resource_type": "AWS::DynamoDB::Table",
                "resource_id": "demo-app-table",
                "change_type": "access_pattern_change",
                "impact": "low",
            },
        ],
        "categories": {
            "compute": "medium",
            "database": "low",
            "network": "low",
            "api": "medium",
        },
    },
    "forecast": {
        "predicted_impact": {
            "invocations": {"direction": "increase", "percentage": 15.0},
            "latency": {"direction": "increase", "percentage": 8.0},
            "errors": {"direction": "stable", "percentage": 0.0},
        },
        "confidence": 0.78,
        "time_horizon": "24h",
        "signals": [
            "Lambda handler modification detected",
            "Database access pattern changed",
            "Historical invocation trend (7d): +12%",
        ],
        "uncertainty": [
            "Traffic volume may vary with deployment window",
            "Limited historical data for this repository",
        ],
        "insufficient_evidence": False,
    },
    "recommendations": [
        {
            "id": "rec-001",
            "priority": "high",
            "category": "observability",
            "title": "Enable enhanced Lambda monitoring",
            "description": "Turn on Lambda Insights for detailed performance metrics before deploying.",
            "reason": "Handler changes detected; need baseline metrics to detect regressions.",
            "evidence_refs": ["cloudwatch:Invocations", "cloudwatch:Duration"],
        },
        {
            "id": "rec-002",
            "priority": "medium",
            "category": "database",
            "title": "Review DynamoDB access patterns",
            "description": "Verify the new query patterns are covered by existing indexes.",
            "reason": "db.py was modified — new scan or query operations may increase read costs.",
            "evidence_refs": ["aws:AWS::DynamoDB::Table"],
        },
        {
            "id": "rec-003",
            "priority": "low",
            "category": "deployment",
            "title": "Use staged rollout (10% → 50% → 100%)",
            "description": "Canary or traffic-shifting deployment is recommended given medium risk.",
            "reason": "Medium overall risk score detected from code analysis.",
            "evidence_refs": [],
        },
    ],
    "confidence": 0.78,
    "evidence_summary": [
        "14,520 Lambda invocations in last 7 days",
        "23 errors (0.16% error rate) — within acceptable range",
        "Average duration: 187ms",
    ],
    "uncertainty": [
        "Traffic volume may vary with deployment window",
        "Limited historical data for this repository",
    ],
    "insufficient_evidence": False,
    "is_mock": True,
}


class MockAIService:
    """Deterministic mock AI service for local/test mode."""

    async def analyze(self, context: dict[str, Any]) -> AIResponseModel:
        logger.info("MOCK AI: returning deterministic mock analysis (is_mock=True)")
        try:
            return AIResponseModel(**_MOCK_AI_RESPONSE)
        except ValidationError as exc:
            logger.error("Mock AI response failed Pydantic validation: %s", exc)
            raise


# ---------------------------------------------------------------------------
# Real AI adapter stub
# ---------------------------------------------------------------------------


class RealAIService:
    """
    Placeholder for the real AI adapter.

    INTEGRATION: Implement this class to connect to Amazon Bedrock, Strands,
    or any other AI provider. The `analyze` method must return a validated
    AIResponseModel. The mock service above documents the expected schema.

    To activate: set MOCK_AI=false in your .env and implement this class.
    """

    async def analyze(self, context: dict[str, Any]) -> AIResponseModel:
        # TODO: Implement real AI call (Person 1 / AI team)
        # Example with Bedrock:
        #   import boto3
        #   bedrock = boto3.client("bedrock-runtime", region_name=settings.AWS_REGION)
        #   response = bedrock.invoke_model(...)
        #   raw = json.loads(response["body"].read())
        #   return AIResponseModel(**raw)  # always validate
        msg = (
            "Real AI adapter not yet implemented. "
            "Set MOCK_AI=true for local development, or implement RealAIService.analyze()."
        )
        raise NotImplementedError(msg)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def create_ai_service() -> AIServiceProtocol:
    if settings.MOCK_AI:
        return MockAIService()
    return RealAIService()


ai_service: AIServiceProtocol = create_ai_service()
