"""
AWS CloudWatch Telemetry package for InfraShift.
"""

from .cloudwatch import CloudWatchTelemetry
from .metrics import (
    MetricNamespace,
    LambdaMetrics,
    DynamoDBMetrics,
    METRIC_STATISTICS,
)
from .telemetry_loop import (
    WindowType,
    TelemetryWindow,
    TelemetryLoopService,
    aggregate_datapoints,
)
from .forecast_comparison import (
    ComparisonStatus,
    MetricForecast,
    ResourceForecastInput,
    ActualObservation,
    MetricComparison,
    ResourceComparisonResult,
    DeploymentForecastVsActualResult,
    ForecastVsActualService,
)

__all__ = [
    "CloudWatchTelemetry",
    "MetricNamespace",
    "LambdaMetrics",
    "DynamoDBMetrics",
    "METRIC_STATISTICS",
    "WindowType",
    "TelemetryWindow",
    "TelemetryLoopService",
    "aggregate_datapoints",
    "ComparisonStatus",
    "MetricForecast",
    "ResourceForecastInput",
    "ActualObservation",
    "MetricComparison",
    "ResourceComparisonResult",
    "DeploymentForecastVsActualResult",
    "ForecastVsActualService",
]

