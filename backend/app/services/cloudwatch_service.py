"""CloudWatch service — real AWS and mock implementations."""
from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.config import settings
from app.schemas.evidence import EvidenceItem

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Mock data
# ---------------------------------------------------------------------------

_MOCK_METRICS: list[dict[str, Any]] = [
    {
        "source": "cloudwatch",
        "namespace": "AWS/Lambda",
        "metric": "Invocations",
        "value": 14520.0,
        "unit": "Count",
        "period": 86400,
        "is_mock": True,
        "insufficient_evidence": False,
    },
    {
        "source": "cloudwatch",
        "namespace": "AWS/Lambda",
        "metric": "Errors",
        "value": 23.0,
        "unit": "Count",
        "period": 86400,
        "is_mock": True,
        "insufficient_evidence": False,
    },
    {
        "source": "cloudwatch",
        "namespace": "AWS/Lambda",
        "metric": "Duration",
        "value": 187.5,
        "unit": "Milliseconds",
        "period": 86400,
        "is_mock": True,
        "insufficient_evidence": False,
    },
]


class CloudWatchService:
    """Service for AWS CloudWatch metrics retrieval."""

    def __init__(self) -> None:
        self._client: Any = None

    def _get_client(self) -> Any:
        """Lazy boto3 client — only created when LIVE_AWS=true."""
        if self._client is None:
            import boto3  # noqa: PLC0415

            self._client = boto3.client("cloudwatch", region_name=settings.AWS_REGION)
        return self._client

    def _collect_lambda_metrics(self, function_name: str, days: int) -> list[EvidenceItem]:
        """Synchronous boto3 call — run in executor from async context."""
        from botocore.exceptions import ClientError  # noqa: PLC0415

        client = self._get_client()
        end_time = datetime.now(UTC)
        start_time = end_time - timedelta(days=days)

        metrics_to_fetch = [
            ("Invocations", "Sum", "Count"),
            ("Errors", "Sum", "Count"),
            ("Duration", "Average", "Milliseconds"),
        ]

        results: list[EvidenceItem] = []

        for metric_name, stat, unit in metrics_to_fetch:
            try:
                resp = client.get_metric_data(
                    MetricDataQueries=[
                        {
                            "Id": "q1",
                            "MetricStat": {
                                "Metric": {
                                    "Namespace": "AWS/Lambda",
                                    "MetricName": metric_name,
                                    "Dimensions": [
                                        {"Name": "FunctionName", "Value": function_name}
                                    ],
                                },
                                "Period": 86400,
                                "Stat": stat,
                            },
                        }
                    ],
                    StartTime=start_time,
                    EndTime=end_time,
                )
                values = resp.get("MetricDataResults", [{}])[0].get("Values", [])
                total = sum(values) if values else None
                results.append(
                    EvidenceItem(
                        source="cloudwatch",
                        namespace="AWS/Lambda",
                        metric=metric_name,
                        value=total,
                        unit=unit,
                        period=86400,
                        start_time=start_time,
                        end_time=end_time,
                        is_mock=False,
                        insufficient_evidence=total is None,
                    )
                )
            except ClientError as exc:
                code = exc.response["Error"]["Code"]
                logger.error("CloudWatch GetMetricData failed [%s]: %s", code, exc)
                results.append(
                    EvidenceItem(
                        source="cloudwatch",
                        namespace="AWS/Lambda",
                        metric=metric_name,
                        is_mock=False,
                        insufficient_evidence=True,
                    )
                )

        return results

    async def get_lambda_metrics(
        self,
        function_name: str,
        days: int | None = None,
    ) -> list[EvidenceItem]:
        """Get Lambda metrics — mock or real depending on configuration."""
        if days is None:
            days = settings.CLOUDWATCH_LOOKBACK_DAYS

        if not settings.LIVE_AWS:
            logger.info("MOCK: returning mock CloudWatch metrics (is_mock=True)")
            now = datetime.now(UTC)
            return [
                EvidenceItem(
                    source=m["source"],
                    namespace=m["namespace"],
                    metric=m["metric"],
                    value=m["value"],
                    unit=m["unit"],
                    period=m["period"],
                    start_time=now - timedelta(days=days),
                    end_time=now,
                    is_mock=True,
                    insufficient_evidence=False,
                )
                for m in _MOCK_METRICS
            ]

        # Run blocking boto3 in thread executor
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, self._collect_lambda_metrics, function_name, days
        )


cloudwatch_service = CloudWatchService()
