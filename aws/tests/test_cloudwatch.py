"""
Unit tests for CloudWatch Telemetry collection.
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock
from botocore.exceptions import ClientError

from aws.config.aws_config import AWSClientFactory, AWSConfig
from aws.models.aws_models import ResourceType
from aws.telemetry.cloudwatch import CloudWatchTelemetry
from aws.telemetry.metrics import LambdaMetrics, DynamoDBMetrics


def test_cloudwatch_telemetry_with_datapoints():
    mock_config = AWSConfig(region_name="ap-south-1")
    cw_client = MagicMock()

    dt1 = datetime(2026, 9, 19, 10, 0, tzinfo=timezone.utc)
    dt2 = datetime(2026, 9, 19, 10, 5, tzinfo=timezone.utc)

    cw_client.get_metric_statistics.return_value = {
        "Datapoints": [
            {"Timestamp": dt1, "Sum": 150.0, "Unit": "Count"},
            {"Timestamp": dt2, "Sum": 230.0, "Unit": "Count"},
        ]
    }

    factory = AWSClientFactory(config=mock_config, custom_clients={"cloudwatch": cw_client})
    telemetry = CloudWatchTelemetry(factory)

    series = telemetry.get_metric_series(
        resource_id="arn:aws:lambda:ap-south-1:123456789012:function:order-api",
        resource_type=ResourceType.LAMBDA,
        resource_name="order-api",
        metric_name=LambdaMetrics.INVOCATIONS,
        namespace="AWS/Lambda",
        statistic="Sum",
    )

    assert series.metric_name == "Invocations"
    assert series.namespace == "AWS/Lambda"
    assert series.statistic == "Sum"
    assert len(series.datapoints) == 2
    assert series.datapoints[0].value == 150.0
    assert series.datapoints[1].value == 230.0
    assert series.is_inferred is False


def test_cloudwatch_telemetry_empty_datapoints():
    """
    CRITICAL TEST: Ensures that if AWS CloudWatch has no datapoints,
    an explicit empty list [] is returned and NO fake data is invented.
    """
    mock_config = AWSConfig(region_name="ap-south-1")
    cw_client = MagicMock()

    cw_client.get_metric_statistics.return_value = {"Datapoints": []}

    factory = AWSClientFactory(config=mock_config, custom_clients={"cloudwatch": cw_client})
    telemetry = CloudWatchTelemetry(factory)

    series = telemetry.get_metric_series(
        resource_id="arn:aws:lambda:ap-south-1:123456789012:function:order-api",
        resource_type=ResourceType.LAMBDA,
        resource_name="order-api",
        metric_name=LambdaMetrics.ERRORS,
        namespace="AWS/Lambda",
    )

    assert series.metric_name == "Errors"
    assert series.datapoints == []
    assert len(series.datapoints) == 0
    assert series.is_inferred is False


def test_lambda_telemetry_collector():
    mock_config = AWSConfig(region_name="ap-south-1")
    cw_client = MagicMock()
    cw_client.get_metric_statistics.return_value = {"Datapoints": []}

    factory = AWSClientFactory(config=mock_config, custom_clients={"cloudwatch": cw_client})
    telemetry = CloudWatchTelemetry(factory)

    series_list = telemetry.get_lambda_telemetry(
        function_arn="arn:aws:lambda:ap-south-1:123456789012:function:order-api",
        function_name="order-api",
    )

    # Standard Lambda metrics: Invocations, Duration, Errors, Throttles
    assert len(series_list) == 4
    metric_names = [s.metric_name for s in series_list]
    assert set(metric_names) == {"Invocations", "Duration", "Errors", "Throttles"}


def test_dynamodb_telemetry_collector():
    mock_config = AWSConfig(region_name="ap-south-1")
    cw_client = MagicMock()
    cw_client.get_metric_statistics.return_value = {"Datapoints": []}

    factory = AWSClientFactory(config=mock_config, custom_clients={"cloudwatch": cw_client})
    telemetry = CloudWatchTelemetry(factory)

    series_list = telemetry.get_dynamodb_telemetry(
        table_arn="arn:aws:dynamodb:ap-south-1:123456789012:table/Orders",
        table_name="Orders",
    )

    # Standard DynamoDB metrics: ConsumedReadCapacityUnits, ConsumedWriteCapacityUnits, ReadThrottleEvents, WriteThrottleEvents
    assert len(series_list) == 4
    metric_names = [s.metric_name for s in series_list]
    assert "ConsumedReadCapacityUnits" in metric_names
    assert "ConsumedWriteCapacityUnits" in metric_names


def test_cloudwatch_api_failure_handling():
    mock_config = AWSConfig(region_name="us-east-1")
    cw_client = MagicMock()

    error_resp = {"Error": {"Code": "InvalidParameterCombination", "Message": "Invalid metric request"}}
    cw_client.get_metric_statistics.side_effect = ClientError(error_resp, "GetMetricStatistics")

    factory = AWSClientFactory(config=mock_config, custom_clients={"cloudwatch": cw_client})
    telemetry = CloudWatchTelemetry(factory)

    series = telemetry.get_metric_series(
        resource_id="arn:aws:lambda:us-east-1:123456789012:function:test",
        resource_type=ResourceType.LAMBDA,
        resource_name="test",
        metric_name="Invocations",
        namespace="AWS/Lambda",
    )

    # Gracefully returns series with empty datapoints on ClientError
    assert series.datapoints == []
