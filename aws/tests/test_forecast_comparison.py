"""
Unit tests for Forecast-vs-Actual AWS Telemetry Loop module.
"""

from unittest.mock import MagicMock
from datetime import datetime, timezone
from aws.config.aws_config import AWSClientFactory, AWSConfig
from aws.models.aws_models import Datapoint, ResourceType, TelemetrySeries
from aws.events.event_models import DeploymentSnapshot, DeploymentStatus, DeploymentEnvironment, DeployedResource
from aws.telemetry.metrics import LambdaMetrics
from aws.telemetry.telemetry_loop import (
    TelemetryLoopService,
    TelemetryWindow,
    WindowType,
    aggregate_datapoints,
)

from aws.telemetry.forecast_comparison import (
    MetricForecast,
    ResourceForecastInput,
    ComparisonStatus,
    MetricComparison,
    ForecastVsActualService,
)


def test_aggregate_datapoints_rules():
    # 1. Sum metric (e.g. Invocations)
    dp_sum = [
        Datapoint(timestamp="2026-09-19T16:05:00Z", value=10.0, unit="Count"),
        Datapoint(timestamp="2026-09-19T16:10:00Z", value=15.0, unit="Count"),
    ]
    agg_name, val, unit = aggregate_datapoints(dp_sum, "Invocations")
    assert agg_name == "sum"
    assert val == 25.0
    assert unit == "Count"

    # 2. Average metric (e.g. Duration)
    dp_avg = [
        Datapoint(timestamp="2026-09-19T16:05:00Z", value=100.0, unit="Milliseconds"),
        Datapoint(timestamp="2026-09-19T16:10:00Z", value=200.0, unit="Milliseconds"),
    ]
    agg_name, val, unit = aggregate_datapoints(dp_avg, "Duration")
    assert agg_name == "average"
    assert val == 150.0

    # 3. Empty datapoints handling (MUST NOT be zero)
    agg_name, val, unit = aggregate_datapoints([], "Duration")
    assert val is None


def test_telemetry_loop_pre_and_post_windows():
    mock_config = AWSConfig(region_name="us-east-1")
    cw_client = MagicMock()

    # Pre-deployment datapoints
    cw_client.get_metric_statistics.return_value = {
        "Datapoints": [
            {"Timestamp": datetime(2026, 9, 19, 15, 30, tzinfo=timezone.utc), "Average": 175.0, "Unit": "Milliseconds"}
        ]
    }

    factory = AWSClientFactory(
        config=mock_config,
        custom_clients={"cloudwatch": cw_client},
    )
    loop = TelemetryLoopService(client_factory=factory)

    anchor_ts = "2026-09-19T16:00:00Z"

    # Baseline Window
    base_win = loop.get_pre_deployment_baseline(
        resource_id="arn:aws:lambda:us-east-1:123:function:orders",
        resource_type=ResourceType.LAMBDA,
        resource_name="orders",
        metric_name="Duration",
        namespace="AWS/Lambda",
        completed_at=anchor_ts,
        baseline_window_minutes=60,
    )

    assert base_win.window_type == WindowType.PRE_DEPLOYMENT
    assert base_win.start_time == "2026-09-19T15:00:00+00:00"
    assert base_win.end_time == "2026-09-19T16:00:00+00:00"
    assert base_win.value == 175.0
    assert base_win.status == "usable"

    # Post-deployment Window
    post_win = loop.get_post_deployment_telemetry(
        resource_id="arn:aws:lambda:us-east-1:123:function:orders",
        resource_type=ResourceType.LAMBDA,
        resource_name="orders",
        metric_name="Duration",
        namespace="AWS/Lambda",
        completed_at=anchor_ts,
        post_window_minutes=60,
    )

    assert post_win.window_type == WindowType.POST_DEPLOYMENT
    assert post_win.start_time == "2026-09-19T16:00:00+00:00"
    assert post_win.end_time == "2026-09-19T17:00:00+00:00"


def test_forecast_comparison_calculations():
    loop_mock = MagicMock(spec=TelemetryLoopService)

    # Mock Baseline (175.0ms)
    loop_mock.get_pre_deployment_baseline.return_value = TelemetryWindow(
        resource_id="arn:aws:lambda:us-east-1:123:function:orders",
        metric_name="Duration",
        namespace="AWS/Lambda",
        window_type=WindowType.PRE_DEPLOYMENT,
        start_time="2026-09-19T15:00:00Z",
        end_time="2026-09-19T16:00:00Z",
        datapoints=[Datapoint(timestamp="2026-09-19T15:30:00Z", value=175.0, unit="Milliseconds")],
        aggregation="average",
        value=175.0,
        unit="Milliseconds",
        datapoint_count=1,
        status="usable",
    )

    # Mock Actual Post-deployment Observation (184.2ms)
    loop_mock.get_post_deployment_telemetry.return_value = TelemetryWindow(
        resource_id="arn:aws:lambda:us-east-1:123:function:orders",
        metric_name="Duration",
        namespace="AWS/Lambda",
        window_type=WindowType.POST_DEPLOYMENT,
        start_time="2026-09-19T16:00:00Z",
        end_time="2026-09-19T17:00:00Z",
        datapoints=[Datapoint(timestamp="2026-09-19T16:30:00Z", value=184.2, unit="Milliseconds")],
        aggregation="average",
        value=184.2,
        unit="Milliseconds",
        datapoint_count=1,
        status="usable",
    )

    service = ForecastVsActualService(loop_service=loop_mock)

    forecast = MetricForecast(
        predicted_value=190.0,
        lower_bound=175.0,
        upper_bound=210.0,
        unit="Milliseconds",
    )

    comp = service.compare_metric(
        forecast=forecast,
        actual_window=loop_mock.get_post_deployment_telemetry.return_value,
        baseline_window=loop_mock.get_pre_deployment_baseline.return_value,
    )

    assert comp.status == ComparisonStatus.USABLE
    assert comp.baseline_value == 175.0
    assert comp.actual.value == 184.2
    assert comp.forecast.predicted_value == 190.0
    assert comp.absolute_error == 5.8  # |184.2 - 190.0|
    assert comp.relative_error == 0.0305  # |184.2 - 190.0| / 190.0
    assert comp.within_forecast_range is True
    assert comp.range_status == "within_range"
    assert "Metric 'Duration' post-deployment average was 184.2 Milliseconds vs baseline 175.0 Milliseconds" in comp.message


def test_forecast_comparison_zero_prediction_relative_error_safety():
    loop_mock = MagicMock(spec=TelemetryLoopService)

    act_win = TelemetryWindow(
        resource_id="r1",
        metric_name="Errors",
        namespace="AWS/Lambda",
        window_type=WindowType.POST_DEPLOYMENT,
        start_time="...",
        end_time="...",
        datapoints=[Datapoint(timestamp="...", value=2.0)],
        aggregation="sum",
        value=2.0,
        datapoint_count=1,
    )
    base_win = TelemetryWindow(
        resource_id="r1",
        metric_name="Errors",
        namespace="AWS/Lambda",
        window_type=WindowType.PRE_DEPLOYMENT,
        start_time="...",
        end_time="...",
        datapoints=[],
        aggregation="sum",
        value=0.0,
        datapoint_count=0,
    )

    # Forecast predicted_value = 0.0 (Zero division risk)
    forecast = MetricForecast(predicted_value=0.0)

    service = ForecastVsActualService(loop_service=loop_mock)
    comp = service.compare_metric(forecast=forecast, actual_window=act_win, baseline_window=base_win)

    assert comp.absolute_error == 2.0
    assert comp.relative_error is None  # Safe handling of division by zero!


def test_forecast_comparison_no_actual_data_handling():
    loop_mock = MagicMock(spec=TelemetryLoopService)

    no_data_win = TelemetryWindow(
        resource_id="r1",
        metric_name="Throttles",
        namespace="AWS/Lambda",
        window_type=WindowType.POST_DEPLOYMENT,
        start_time="...",
        end_time="...",
        datapoints=[],
        aggregation="sum",
        value=None,  # Explicitly None
        datapoint_count=0,
        status="no_data",
    )
    base_win = TelemetryWindow(
        resource_id="r1",
        metric_name="Throttles",
        namespace="AWS/Lambda",
        window_type=WindowType.PRE_DEPLOYMENT,
        start_time="...",
        end_time="...",
        datapoints=[],
        aggregation="sum",
        value=None,
        datapoint_count=0,
    )

    forecast = MetricForecast(predicted_value=0.0)
    service = ForecastVsActualService(loop_service=loop_mock)

    comp = service.compare_metric(forecast=forecast, actual_window=no_data_win, baseline_window=base_win)

    assert comp.status == ComparisonStatus.NO_ACTUAL_DATA
    assert comp.absolute_error is None
    assert comp.relative_error is None
    assert comp.within_forecast_range is None
    assert comp.range_status == "no_actual_data"


def test_full_deployment_comparison_flow():
    loop_mock = MagicMock(spec=TelemetryLoopService)

    loop_mock.get_pre_deployment_baseline.return_value = TelemetryWindow(
        resource_id="arn:aws:lambda:us-east-1:123:function:orders-fn",
        metric_name="Invocations",
        namespace="AWS/Lambda",
        window_type=WindowType.PRE_DEPLOYMENT,
        start_time="...",
        end_time="...",
        datapoints=[Datapoint(timestamp="...", value=100.0)],
        aggregation="sum",
        value=100.0,
        datapoint_count=1,
    )
    loop_mock.get_post_deployment_telemetry.return_value = TelemetryWindow(
        resource_id="arn:aws:lambda:us-east-1:123:function:orders-fn",
        metric_name="Invocations",
        namespace="AWS/Lambda",
        window_type=WindowType.POST_DEPLOYMENT,
        start_time="...",
        end_time="...",
        datapoints=[Datapoint(timestamp="...", value=120.0)],
        aggregation="sum",
        value=120.0,
        datapoint_count=1,
    )

    snapshot = DeploymentSnapshot(
        snapshot_id="snap-deploy-1",
        deployment_id="deploy-1",
        change_id="PR-99",
        commit_sha="a99",
        environment=DeploymentEnvironment.STAGING,
        status=DeploymentStatus.COMPLETED,
        completed_at="2026-09-19T16:00:00Z",
        resources=[
            DeployedResource(resource_id="arn:aws:lambda:us-east-1:123:function:orders-fn", resource_type=ResourceType.LAMBDA)
        ],
        telemetry_anchor_timestamp="2026-09-19T16:00:00Z",
    )

    forecast_input = ResourceForecastInput(
        resource_id="arn:aws:lambda:us-east-1:123:function:orders-fn",
        metric_forecasts={
            "Invocations": MetricForecast(predicted_value=125.0, lower_bound=110.0, upper_bound=140.0)
        },
    )

    service = ForecastVsActualService(loop_service=loop_mock)
    result = service.compare_deployment_telemetry(snapshot=snapshot, forecasts=[forecast_input])

    assert result.deployment_id == "deploy-1"
    assert result.status == "completed"
    assert len(result.resources) == 1

    res_comp = result.resources[0]
    assert res_comp.resource_name == "orders-fn"
    assert len(res_comp.comparisons) == len(LambdaMetrics.ALL_DEFAULT)
