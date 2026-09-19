"""AWS infrastructure evidence service."""
from __future__ import annotations

import logging
from typing import Any

from app.core.config import settings
from app.schemas.evidence import EvidenceItem

logger = logging.getLogger(__name__)

# Mock Lambda resource evidence
_MOCK_LAMBDA_RESOURCES: list[dict[str, Any]] = [
    {
        "resource_type": "AWS::Lambda::Function",
        "resource_id": "demo-app-handler",
        "runtime": "python3.11",
        "memory_mb": 256,
        "timeout_s": 30,
        "region": "us-east-1",
    },
    {
        "resource_type": "AWS::DynamoDB::Table",
        "resource_id": "demo-app-table",
        "billing_mode": "PAY_PER_REQUEST",
        "region": "us-east-1",
    },
]


class AWSService:
    """Read-only AWS infrastructure evidence collector.

    IMPORTANT: This service performs READ OPERATIONS ONLY.
    No create/delete/update/deploy operations are permitted.
    """

    def get_lambda_resources(self, repo_name: str) -> list[EvidenceItem]:
        """Collect Lambda-related infrastructure evidence."""
        if not settings.LIVE_AWS:
            logger.info("MOCK: returning mock Lambda resources (is_mock=True)")
            return [
                EvidenceItem(
                    source="aws",
                    namespace="AWS::Lambda::Function",
                    metric="resource_discovery",
                    raw=res,
                    is_mock=True,
                    insufficient_evidence=False,
                )
                for res in _MOCK_LAMBDA_RESOURCES
            ]

        return self._discover_lambda_resources(repo_name)

    def _discover_lambda_resources(self, repo_name: str) -> list[EvidenceItem]:
        """Real AWS resource discovery (read-only)."""
        try:
            import boto3  # noqa: PLC0415

            lambda_client = boto3.client("lambda", region_name=settings.AWS_REGION)
            response = lambda_client.list_functions()
            functions = response.get("Functions", [])

            items: list[EvidenceItem] = []
            for fn in functions:
                items.append(
                    EvidenceItem(
                        source="aws",
                        namespace="AWS::Lambda::Function",
                        metric="resource_discovery",
                        raw={
                            "resource_type": "AWS::Lambda::Function",
                            "resource_id": fn["FunctionName"],
                            "runtime": fn.get("Runtime", "unknown"),
                            "memory_mb": fn.get("MemorySize", 128),
                            "timeout_s": fn.get("Timeout", 3),
                            "region": settings.AWS_REGION,
                        },
                        is_mock=False,
                        insufficient_evidence=False,
                    )
                )
            return items
        except Exception as exc:  # noqa: BLE001
            logger.error("AWS Lambda list_functions failed: %s", exc)
            return [
                EvidenceItem(
                    source="aws",
                    namespace="AWS::Lambda::Function",
                    metric="resource_discovery",
                    is_mock=False,
                    insufficient_evidence=True,
                )
            ]


aws_service = AWSService()
