"""
CloudWatch Telemetry Module.
Retrieves and normalizes CloudWatch metrics for AWS Lambda and DynamoDB.
Returns explicit empty lists when no AWS data is present; never fabricates data.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Union, Dict, Any
from botocore.exceptions import BotoCoreError, ClientError

from aws.config.aws_config import AWSClientFactory, AWSConfig
from aws.models.aws_models import TelemetrySeries, Datapoint, ResourceType
from aws.telemetry.metrics import (
    MetricNamespace,
    LambdaMetrics,
    DynamoDBMetrics,
    METRIC_STATISTICS,
)

logger = logging.getLogger("infrashift.aws.telemetry.cloudwatch")


class CloudWatchTelemetry:
    """Retrieves CloudWatch metrics for AWS infrastructure resources."""

    def __init__(self, client_factory: Optional[AWSClientFactory] = None, config: Optional[AWSConfig] = None):
        if client_factory:
            self.factory = client_factory
        else:
            self.factory = AWSClientFactory(config=config or AWSConfig())

    def get_client(self):
        return self.factory.get_client("cloudwatch")

    def _parse_datetime(self, dt_val: Union[datetime, str]) -> datetime:
        """Helper to ensure datetime object."""
        if isinstance(dt_val, datetime):
            return dt_val
        # Remove trailing Z if present for ISO parsing
        clean_str = dt_val.rstrip("Z")
        return datetime.fromisoformat(clean_str)

    def get_metric_series(
        self,
        resource_id: str,
        resource_type: Union[ResourceType, str],
        resource_name: str,
        metric_name: str,
        namespace: str,
        statistic: Optional[str] = None,
        start_time: Optional[Union[datetime, str]] = None,
        end_time: Optional[Union[datetime, str]] = None,
        period_seconds: int = 300,
    ) -> TelemetrySeries:
        """
        Fetch CloudWatch metrics for a specific resource and metric name.

        :param resource_id: Resource identifier / ARN.
        :param resource_type: ResourceType (LAMBDA, DYNAMODB, etc.).
        :param resource_name: Name of the AWS resource.
        :param metric_name: Name of CloudWatch metric (e.g. 'Invocations', 'Duration').
        :param namespace: CloudWatch namespace (e.g. 'AWS/Lambda', 'AWS/DynamoDB').
        :param statistic: Statistic type ('Sum', 'Average', 'Maximum', etc.). Defaults based on metric.
        :param start_time: Start window (defaults to 1 hour ago).
        :param end_time: End window (defaults to now).
        :param period_seconds: Period in seconds (default 300).
        """
        now = datetime.now(timezone.utc)
        end_dt = self._parse_datetime(end_time) if end_time else now
        start_dt = self._parse_datetime(start_time) if start_time else (end_dt - timedelta(hours=1))

        resolved_stat = statistic or METRIC_STATISTICS.get(metric_name, "Sum")

        # Build dimensions based on resource type
        dimensions: List[Dict[str, str]] = []
        res_type_str = str(resource_type).lower()

        if "lambda" in res_type_str or namespace == MetricNamespace.LAMBDA:
            dimensions = [{"Name": "FunctionName", "Value": resource_name}]
        elif "dynamodb" in res_type_str or namespace == MetricNamespace.DYNAMODB:
            dimensions = [{"Name": "TableName", "Value": resource_name}]
        elif "apigateway" in res_type_str or namespace == MetricNamespace.API_GATEWAY:
            dimensions = [{"Name": "ApiName", "Value": resource_name}]

        datapoints: List[Datapoint] = []

        try:
            client = self.get_client()
            response = client.get_metric_statistics(
                Namespace=namespace,
                MetricName=metric_name,
                Dimensions=dimensions,
                StartTime=start_dt,
                EndTime=end_dt,
                Period=period_seconds,
                Statistics=[resolved_stat],
            )

            raw_datapoints = response.get("Datapoints", [])
            # Sort datapoints chronologically
            sorted_points = sorted(raw_datapoints, key=lambda x: x.get("Timestamp"))

            for dp in sorted_points:
                val = dp.get(resolved_stat, dp.get("Value", 0.0))
                ts_str = dp["Timestamp"].isoformat() if isinstance(dp["Timestamp"], datetime) else str(dp["Timestamp"])
                datapoints.append(
                    Datapoint(
                        timestamp=ts_str,
                        value=float(val),
                        unit=dp.get("Unit"),
                    )
                )

        except (BotoCoreError, ClientError) as e:
            logger.error(
                "Failed to fetch CloudWatch metric '%s' for resource '%s': %s",
                metric_name,
                resource_name,
                str(e),
            )
            # Return safe series with empty datapoints on API error

        return TelemetrySeries(
            resource_id=resource_id,
            metric_name=metric_name,
            namespace=namespace,
            statistic=resolved_stat,
            start_time=start_dt.isoformat() + "Z",
            end_time=end_dt.isoformat() + "Z",
            period_seconds=period_seconds,
            datapoints=datapoints,
            is_inferred=False,
        )

    def get_lambda_telemetry(
        self,
        function_arn: str,
        function_name: str,
        metrics: Optional[List[str]] = None,
        start_time: Optional[Union[datetime, str]] = None,
        end_time: Optional[Union[datetime, str]] = None,
        period_seconds: int = 300,
    ) -> List[TelemetrySeries]:
        """Fetch all standard telemetry metrics for a Lambda function."""
        target_metrics = metrics or LambdaMetrics.ALL_DEFAULT
        series_list = []
        for m in target_metrics:
            series = self.get_metric_series(
                resource_id=function_arn,
                resource_type=ResourceType.LAMBDA,
                resource_name=function_name,
                metric_name=m,
                namespace=MetricNamespace.LAMBDA,
                start_time=start_time,
                end_time=end_time,
                period_seconds=period_seconds,
            )
            series_list.append(series)
        return series_list

    def get_dynamodb_telemetry(
        self,
        table_arn: str,
        table_name: str,
        metrics: Optional[List[str]] = None,
        start_time: Optional[Union[datetime, str]] = None,
        end_time: Optional[Union[datetime, str]] = None,
        period_seconds: int = 300,
    ) -> List[TelemetrySeries]:
        """Fetch all standard telemetry metrics for a DynamoDB table."""
        target_metrics = metrics or DynamoDBMetrics.ALL_DEFAULT
        series_list = []
        for m in target_metrics:
            series = self.get_metric_series(
                resource_id=table_arn,
                resource_type=ResourceType.DYNAMODB,
                resource_name=table_name,
                metric_name=m,
                namespace=MetricNamespace.DYNAMODB,
                start_time=start_time,
                end_time=end_time,
                period_seconds=period_seconds,
            )
            series_list.append(series)
        return series_list
