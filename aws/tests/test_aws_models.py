"""
Unit tests for Normalized AWS Pydantic Data Models.
"""

from aws.models.aws_models import (
    NormalizedResource,
    ResourceType,
    LambdaMetadata,
    DynamoDBMetadata,
    APIGatewayMetadata,
    Datapoint,
    TelemetrySeries,
)


def test_normalized_resource_lambda():
    meta = LambdaMetadata(
        function_arn="arn:aws:lambda:ap-south-1:123456789012:function:order-api",
        function_name="order-api",
        runtime="python3.12",
        memory_mb=512,
        timeout_seconds=30,
        environment_keys=["DATABASE_URL", "API_KEY"],
    )

    res = NormalizedResource(
        resource_id=meta.function_arn,
        resource_type=ResourceType.LAMBDA,
        resource_name="order-api",
        region="ap-south-1",
        account_id="123456789012",
        metadata=meta.model_dump(),
        is_inferred=False,
    )

    assert res.resource_id == meta.function_arn
    assert res.resource_type == ResourceType.LAMBDA
    assert res.metadata["runtime"] == "python3.12"
    assert res.metadata["memory_mb"] == 512
    assert "DATABASE_URL" in res.metadata["environment_keys"]
    assert res.is_inferred is False


def test_normalized_resource_dynamodb():
    meta = DynamoDBMetadata(
        table_arn="arn:aws:dynamodb:us-east-1:123456789012:table/Orders",
        table_name="Orders",
        table_status="ACTIVE",
        billing_mode="PAY_PER_REQUEST",
        item_count=1500,
        partition_key="order_id",
    )

    res = NormalizedResource(
        resource_id=meta.table_arn,
        resource_type=ResourceType.DYNAMODB,
        resource_name="Orders",
        region="us-east-1",
        metadata=meta.model_dump(),
    )

    assert res.resource_type == ResourceType.DYNAMODB
    assert res.metadata["table_status"] == "ACTIVE"
    assert res.metadata["partition_key"] == "order_id"
    assert res.is_inferred is False


def test_telemetry_series_empty_datapoints():
    series = TelemetrySeries(
        resource_id="arn:aws:lambda:ap-south-1:123456789012:function:order-api",
        metric_name="Invocations",
        namespace="AWS/Lambda",
        statistic="Sum",
        start_time="2026-09-19T00:00:00Z",
        end_time="2026-09-19T01:00:00Z",
        period_seconds=300,
        datapoints=[],
        is_inferred=False,
    )

    assert len(series.datapoints) == 0
    assert series.is_inferred is False
    assert series.metric_name == "Invocations"


def test_telemetry_series_with_datapoints():
    dp = Datapoint(timestamp="2026-09-19T00:05:00Z", value=42.0, unit="Count")
    series = TelemetrySeries(
        resource_id="arn:aws:lambda:ap-south-1:123456789012:function:order-api",
        metric_name="Invocations",
        namespace="AWS/Lambda",
        statistic="Sum",
        start_time="2026-09-19T00:00:00Z",
        end_time="2026-09-19T01:00:00Z",
        period_seconds=300,
        datapoints=[dp],
    )

    assert len(series.datapoints) == 1
    assert series.datapoints[0].value == 42.0
    assert series.datapoints[0].unit == "Count"
