"""
Telemetry Windowing and Aggregation Module for AWS InfraShift.
Retrieves pre-deployment baseline and post-deployment actual CloudWatch telemetry.
Enforces deterministic metric aggregations and strict no-data handling.
"""

import logging
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import List, Dict, Optional, Tuple, Union, Any
from pydantic import BaseModel, Field, ConfigDict

from aws.config.aws_config import AWSClientFactory, AWSConfig
from aws.models.aws_models import Datapoint, ResourceType, TelemetrySeries
from aws.telemetry.metrics import (
    MetricNamespace,
    LambdaMetrics,
    DynamoDBMetrics,
    METRIC_STATISTICS,
)
from aws.telemetry.cloudwatch import CloudWatchTelemetry

logger = logging.getLogger("infrashift.aws.telemetry.loop")


class WindowType(str, Enum):
    """Classification of telemetry time window relative to deployment."""

    PRE_DEPLOYMENT = "pre_deployment"
    POST_DEPLOYMENT = "post_deployment"


class TelemetryWindow(BaseModel):
    """
    Normalized CloudWatch telemetry window representation (baseline or post-deployment).
    """

    model_config = ConfigDict(extra="ignore")

    resource_id: str
    metric_name: str
    namespace: str
    window_type: WindowType
    start_time: str
    end_time: str
    datapoints: List[Datapoint] = Field(default_factory=list)
    aggregation: str = Field(description="Deterministic aggregation rule e.g. sum, average")
    value: Optional[float] = Field(
        default=None,
        description="Aggregated numeric observation. STRICTLY None if datapoints list is empty.",
    )
    unit: Optional[str] = None
    datapoint_count: int = 0
    status: str = Field(default="usable", description="'usable', 'no_data', 'error'")


def aggregate_datapoints(
    datapoints: List[Datapoint],
    metric_name: str,
) -> Tuple[str, Optional[float], Optional[str]]:
    """
    Deterministically aggregate CloudWatch datapoints based on metric characteristics.

    :param datapoints: List of Datapoint objects.
    :param metric_name: Name of metric e.g. 'Invocations', 'Duration', 'ConsumedReadCapacityUnits'.
    :return: Tuple of (aggregation_name, aggregated_value, unit).
    """
    if not datapoints:
        agg = METRIC_STATISTICS.get(metric_name, "Sum").lower()
        return agg, None, None

    unit = datapoints[0].unit
    stat = METRIC_STATISTICS.get(metric_name, "Sum")
    agg_name = stat.lower()

    values = [dp.value for dp in datapoints]

    if stat.lower() == "average":
        avg_val = sum(values) / float(len(values))
        return "average", round(avg_val, 4), unit
    elif stat.lower() == "maximum":
        return "maximum", max(values), unit
    elif stat.lower() == "minimum":
        return "minimum", min(values), unit
    else:  # Default to Sum
        return "sum", round(sum(values), 4), unit


class TelemetryLoopService:
    """
    Service for fetching pre-deployment baselines and post-deployment CloudWatch telemetry windows.
    """

    def __init__(
        self,
        client_factory: Optional[AWSClientFactory] = None,
        config: Optional[AWSConfig] = None,
        telemetry: Optional[CloudWatchTelemetry] = None,
    ):
        if telemetry:
            self.telemetry = telemetry
        else:
            self.factory = client_factory or AWSClientFactory(config=config or AWSConfig())
            self.telemetry = CloudWatchTelemetry(client_factory=self.factory)

    def _parse_datetime(self, dt_val: Union[datetime, str]) -> datetime:
        """Parse datetime or ISO 8601 string to timezone-aware UTC datetime."""
        if isinstance(dt_val, datetime):
            if dt_val.tzinfo is None:
                return dt_val.replace(tzinfo=timezone.utc)
            return dt_val
        clean_str = str(dt_val).rstrip("Z")
        dt = datetime.fromisoformat(clean_str)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    def get_pre_deployment_baseline(
        self,
        resource_id: str,
        resource_type: Union[ResourceType, str],
        resource_name: str,
        metric_name: str,
        namespace: str,
        completed_at: Union[datetime, str],
        baseline_window_minutes: int = 60,
        period_seconds: int = 300,
    ) -> TelemetryWindow:
        """
        Fetch pre-deployment historical baseline window ending at completed_at timestamp.
        """
        end_dt = self._parse_datetime(completed_at)
        start_dt = end_dt - timedelta(minutes=baseline_window_minutes)

        series = self.telemetry.get_metric_series(
            resource_id=resource_id,
            resource_type=resource_type,
            resource_name=resource_name,
            metric_name=metric_name,
            namespace=namespace,
            start_time=start_dt,
            end_time=end_dt,
            period_seconds=period_seconds,
        )

        agg_name, val, unit = aggregate_datapoints(series.datapoints, metric_name)
        status = "usable" if series.datapoints else "no_data"

        return TelemetryWindow(
            resource_id=resource_id,
            metric_name=metric_name,
            namespace=namespace,
            window_type=WindowType.PRE_DEPLOYMENT,
            start_time=start_dt.isoformat(),
            end_time=end_dt.isoformat(),
            datapoints=series.datapoints,
            aggregation=agg_name,
            value=val,
            unit=unit,
            datapoint_count=len(series.datapoints),
            status=status,
        )

    def get_post_deployment_telemetry(
        self,
        resource_id: str,
        resource_type: Union[ResourceType, str],
        resource_name: str,
        metric_name: str,
        namespace: str,
        completed_at: Union[datetime, str],
        post_window_minutes: int = 60,
        period_seconds: int = 300,
    ) -> TelemetryWindow:
        """
        Fetch post-deployment actual observation window starting at completed_at timestamp.
        """
        start_dt = self._parse_datetime(completed_at)
        end_dt = start_dt + timedelta(minutes=post_window_minutes)

        series = self.telemetry.get_metric_series(
            resource_id=resource_id,
            resource_type=resource_type,
            resource_name=resource_name,
            metric_name=metric_name,
            namespace=namespace,
            start_time=start_dt,
            end_time=end_dt,
            period_seconds=period_seconds,
        )

        agg_name, val, unit = aggregate_datapoints(series.datapoints, metric_name)
        status = "usable" if series.datapoints else "no_data"

        return TelemetryWindow(
            resource_id=resource_id,
            metric_name=metric_name,
            namespace=namespace,
            window_type=WindowType.POST_DEPLOYMENT,
            start_time=start_dt.isoformat(),
            end_time=end_dt.isoformat(),
            datapoints=series.datapoints,
            aggregation=agg_name,
            value=val,
            unit=unit,
            datapoint_count=len(series.datapoints),
            status=status,
        )
