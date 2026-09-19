"""
Unit and Integration Test Suite for Phase 7 AWS Evidence Integration Service.
Validates the end-to-end evidence pipeline:
Change -> Impact -> Deployment -> Telemetry Anchor -> Baseline -> Actual -> Forecast Comparison -> Unified Package.
Ensures strict read-only guarantee, non-causal reporting, missing-data preservation, and forecast immutability.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
import pytest

from aws.models.aws_models import (
    ResourceType,
    EvidenceType,
    ConfidenceLevel,
    RelationshipType,
    Datapoint,
    TelemetrySeries,
)
from aws.impact.code_change_models import (
    CodeChangeInput,
    FileChange,
    FileChangeStatus,
    ChangeImpactEvidence,
    ImpactedResource,
    ImpactType,
    ImpactPath,
    ImpactPathStep,
    UnresolvedMapping,
)
from aws.events.event_models import (
    DeploymentSnapshot,
    DeployedResource,
    DeploymentEnvironment,
    DeploymentStatus,
)
from aws.telemetry.metrics import LambdaMetrics, DynamoDBMetrics
from aws.telemetry.cloudwatch import CloudWatchTelemetry
from aws.telemetry.telemetry_loop import TelemetryLoopService, TelemetryWindow, WindowType
from aws.telemetry.forecast_comparison import (
    ForecastVsActualService,
    ResourceForecastInput,
    MetricForecast,
)
from aws.integration.evidence_models import AWSEvidencePackage, ResourceTraceability
from aws.integration.evidence_service import AWSEvidenceIntegrationService


@pytest.fixture
def mock_cloudwatch():
    """Mocked CloudWatchTelemetry provider."""
    mock = MagicMock(spec=CloudWatchTelemetry)
    return mock


@pytest.fixture
def integration_service(mock_cloudwatch):
    """AWSEvidenceIntegrationService with mocked telemetry."""
    loop_service = TelemetryLoopService(telemetry=mock_cloudwatch)
    comparison_service = ForecastVsActualService(loop_service=loop_service)
    return AWSEvidenceIntegrationService(
        telemetry_loop_service=loop_service,
        forecast_comparison_service=comparison_service,
    )


@pytest.fixture
def sample_anchor_dt():
    return datetime(2026, 9, 19, 20, 0, 0, tzinfo=timezone.utc)


def create_sample_series(
    resource_id: str,
    metric_name: str,
    namespace: str,
    val_list: list,
    start_dt: datetime,
) -> TelemetrySeries:
    dps = []
    for idx, v in enumerate(val_list):
        ts = (start_dt + timedelta(minutes=idx * 5)).isoformat()
        dps.append(Datapoint(timestamp=ts, value=v, unit="Milliseconds" if "Duration" in metric_name else "Count"))
    return TelemetrySeries(
        resource_id=resource_id,
        metric_name=metric_name,
        namespace=namespace,
        statistic="Sum" if "Duration" not in metric_name else "Average",
        start_time=start_dt.isoformat(),
        end_time=(start_dt + timedelta(minutes=60)).isoformat(),
        period_seconds=300,
        datapoints=dps,
    )


# ============================================================================
# TEST 1: Change -> Lambda -> Deployment -> Baseline -> Actual -> Forecast Comparison
# ============================================================================
def test_end_to_end_single_lambda(integration_service, mock_cloudwatch, sample_anchor_dt):
    lambda_arn = "arn:aws:lambda:us-east-1:123456789012:function:orders-handler"

    def get_series_side_effect(**kwargs):
        m_name = kwargs.get("metric_name")
        start_t = kwargs.get("start_time")
        if m_name == "Duration":
            return create_sample_series(lambda_arn, "Duration", "AWS/Lambda", [180.0, 184.0, 188.0], start_t)
        return create_sample_series(lambda_arn, m_name, "AWS/Lambda", [10.0, 15.0, 20.0], start_t)

    mock_cloudwatch.get_metric_series.side_effect = get_series_side_effect

    change_input = CodeChangeInput(
        change_id="PR-101",
        files_changed=[FileChange(path="src/orders/handler.py", status=FileChangeStatus.MODIFIED)],
    )
    change_impact = ChangeImpactEvidence(
        change_id="PR-101",
        status="completed",
        change=change_input,
        impacted_resources=[
            ImpactedResource(
                resource_id=lambda_arn,
                resource_type=ResourceType.LAMBDA,
                resource_name="orders-handler",
                impact=ImpactType.DIRECT,
                confidence=ConfidenceLevel.OBSERVED,
                evidence=[{"evidence_type": "aws_configuration", "confidence": "observed"}],
            )
        ],
    )

    snapshot = DeploymentSnapshot(
        snapshot_id="snap-101",
        deployment_id="dep-101",
        change_id="PR-101",
        environment=DeploymentEnvironment.SANDBOX,
        status=DeploymentStatus.COMPLETED,
        telemetry_anchor_timestamp=sample_anchor_dt.isoformat(),
        completed_at=sample_anchor_dt.isoformat(),
        resources=[
            DeployedResource(
                resource_id=lambda_arn,
                resource_type=ResourceType.LAMBDA,
                resource_name="orders-handler",
            )
        ],
    )

    forecasts = [
        ResourceForecastInput(
            resource_id=lambda_arn,
            metric_forecasts={
                "Duration": MetricForecast(predicted_value=190.0, lower_bound=175.0, upper_bound=210.0, unit="Milliseconds")
            },
        )
    ]

    pkg = integration_service.assemble_evidence_package(
        change_impact=change_impact,
        snapshot=snapshot,
        forecasts=forecasts,
    )

    assert pkg.change_id == "PR-101"
    assert pkg.deployment_id == "dep-101"
    assert pkg.environment == "sandbox"
    assert pkg.forecast_status == "provided"
    assert pkg.status == "usable"
    assert len(pkg.impacted_resources) == 1
    assert len(pkg.baseline_observations) > 0
    assert len(pkg.post_deployment_observations) > 0
    assert pkg.forecast_comparisons is not None

    comp_res = pkg.forecast_comparisons.resources[0]
    duration_comp = next(c for c in comp_res.comparisons if c.metric_name == "Duration")
    assert duration_comp.actual.value == 184.0
    assert duration_comp.forecast.predicted_value == 190.0
    assert duration_comp.absolute_error == 6.0
    assert duration_comp.within_forecast_range is True
    assert duration_comp.status == "usable"


# ============================================================================
# TEST 2: Multi-Resource Dependency Chain (Lambda -> DynamoDB)
# ============================================================================
def test_multi_resource_dependency_chain(integration_service, mock_cloudwatch, sample_anchor_dt):
    lambda_arn = "arn:aws:lambda:us-east-1:123456789012:function:orders-handler"
    dynamo_arn = "arn:aws:dynamodb:us-east-1:123456789012:table/Orders"

    def get_series_side_effect(**kwargs):
        r_id = kwargs.get("resource_id")
        m_name = kwargs.get("metric_name")
        start_t = kwargs.get("start_time")
        ns = "AWS/Lambda" if r_id == lambda_arn else "AWS/DynamoDB"
        return create_sample_series(r_id, m_name, ns, [5.0, 10.0], start_t)

    mock_cloudwatch.get_metric_series.side_effect = get_series_side_effect

    change_impact = ChangeImpactEvidence(
        change_id="PR-102",
        status="completed",
        change=CodeChangeInput(change_id="PR-102"),
        impacted_resources=[
            ImpactedResource(
                resource_id=lambda_arn,
                resource_type=ResourceType.LAMBDA,
                resource_name="orders-handler",
                impact=ImpactType.DIRECT,
                confidence=ConfidenceLevel.OBSERVED,
            ),
            ImpactedResource(
                resource_id=dynamo_arn,
                resource_type=ResourceType.DYNAMODB,
                resource_name="Orders",
                impact=ImpactType.DOWNSTREAM,
                confidence=ConfidenceLevel.OBSERVED,
            ),
        ],
        impact_paths=[
            ImpactPath(
                source_resource_id=lambda_arn,
                target_resource_id=dynamo_arn,
                relationship=RelationshipType.ACCESSES,
                evidence=EvidenceType.AWS_CONFIGURATION,
                confidence=ConfidenceLevel.OBSERVED,
                path=[
                    ImpactPathStep(
                        resource_id=lambda_arn,
                        resource_type=ResourceType.LAMBDA,
                        relationship=RelationshipType.ACCESSES,
                        impact_type=ImpactType.DIRECT,
                    ),
                    ImpactPathStep(
                        resource_id=dynamo_arn,
                        resource_type=ResourceType.DYNAMODB,
                        relationship=RelationshipType.ACCESSES,
                        impact_type=ImpactType.DOWNSTREAM,
                    ),
                ],
            )
        ],
    )

    snapshot = DeploymentSnapshot(
        snapshot_id="snap-102",
        deployment_id="dep-102",
        change_id="PR-102",
        environment=DeploymentEnvironment.SANDBOX,
        status=DeploymentStatus.COMPLETED,
        telemetry_anchor_timestamp=sample_anchor_dt.isoformat(),
        resources=[
            DeployedResource(resource_id=lambda_arn, resource_type=ResourceType.LAMBDA, resource_name="orders-handler"),
            DeployedResource(resource_id=dynamo_arn, resource_type=ResourceType.DYNAMODB, resource_name="Orders"),
        ],
    )

    pkg = integration_service.assemble_evidence_package(change_impact=change_impact, snapshot=snapshot)

    assert len(pkg.impacted_resources) == 2
    assert len(pkg.dependency_paths) == 1
    assert len(pkg.traceability) == 2

    l_trace = next(t for t in pkg.traceability if t.resource_id == lambda_arn)
    d_trace = next(t for t in pkg.traceability if t.resource_id == dynamo_arn)

    assert l_trace.impact_classification == "direct"
    assert d_trace.impact_classification == "downstream"
    assert d_trace.dependency_evidence == EvidenceType.AWS_CONFIGURATION


# ============================================================================
# TEST 3: No Post-Deployment Telemetry Data
# ============================================================================
def test_no_post_deployment_telemetry(integration_service, mock_cloudwatch, sample_anchor_dt):
    lambda_arn = "arn:aws:lambda:us-east-1:123456789012:function:quiet-handler"

    def get_series_side_effect(**kwargs):
        start_t = kwargs.get("start_time")
        if start_t.isoformat() < sample_anchor_dt.isoformat():
            return create_sample_series(lambda_arn, "Duration", "AWS/Lambda", [100.0], start_t)
        return TelemetrySeries(
            resource_id=lambda_arn,
            metric_name=kwargs.get("metric_name"),
            namespace="AWS/Lambda",
            statistic="Sum",
            start_time=start_t.isoformat(),
            end_time=(start_t + timedelta(minutes=60)).isoformat(),
            period_seconds=300,
            datapoints=[],
        )

    mock_cloudwatch.get_metric_series.side_effect = get_series_side_effect

    change_impact = ChangeImpactEvidence(
        change_id="PR-103",
        status="completed",
        change=CodeChangeInput(change_id="PR-103"),
        impacted_resources=[
            ImpactedResource(
                resource_id=lambda_arn,
                resource_type=ResourceType.LAMBDA,
                resource_name="quiet-handler",
                impact=ImpactType.DIRECT,
                confidence=ConfidenceLevel.OBSERVED,
            )
        ],
    )

    snapshot = DeploymentSnapshot(
        snapshot_id="snap-103",
        deployment_id="dep-103",
        change_id="PR-103",
        environment=DeploymentEnvironment.SANDBOX,
        status=DeploymentStatus.COMPLETED,
        telemetry_anchor_timestamp=sample_anchor_dt.isoformat(),
        resources=[DeployedResource(resource_id=lambda_arn, resource_type=ResourceType.LAMBDA, resource_name="quiet-handler")],
    )

    pkg = integration_service.assemble_evidence_package(change_impact=change_impact, snapshot=snapshot)

    assert pkg.status == "no_actual_data"
    post_win = pkg.post_deployment_observations[0]
    assert post_win.status == "no_data"
    assert post_win.value is None


# ============================================================================
# TEST 4: No Forecast Supplied (forecast_status = "not_provided")
# ============================================================================
def test_no_forecast_supplied(integration_service, mock_cloudwatch, sample_anchor_dt):
    lambda_arn = "arn:aws:lambda:us-east-1:123456789012:function:handler"

    mock_cloudwatch.get_metric_series.return_value = create_sample_series(
        lambda_arn, "Invocations", "AWS/Lambda", [50.0], sample_anchor_dt
    )

    change_impact = ChangeImpactEvidence(
        change_id="PR-104",
        status="completed",
        change=CodeChangeInput(change_id="PR-104"),
        impacted_resources=[
            ImpactedResource(
                resource_id=lambda_arn,
                resource_type=ResourceType.LAMBDA,
                resource_name="handler",
                impact=ImpactType.DIRECT,
                confidence=ConfidenceLevel.OBSERVED,
            )
        ],
    )

    snapshot = DeploymentSnapshot(
        snapshot_id="snap-104",
        deployment_id="dep-104",
        change_id="PR-104",
        environment=DeploymentEnvironment.SANDBOX,
        status=DeploymentStatus.COMPLETED,
        telemetry_anchor_timestamp=sample_anchor_dt.isoformat(),
        resources=[DeployedResource(resource_id=lambda_arn, resource_type=ResourceType.LAMBDA, resource_name="handler")],
    )

    pkg = integration_service.assemble_evidence_package(
        change_impact=change_impact,
        snapshot=snapshot,
        forecasts=None,
    )

    assert pkg.forecast_status == "not_provided"
    assert pkg.forecast_comparisons is None
    assert pkg.traceability[0].forecast_comparison_status == "not_provided"


# ============================================================================
# TEST 5: No X-Ray Data (Explicit Confidence Preserved)
# ============================================================================
def test_no_xray_data_preserved(integration_service, mock_cloudwatch, sample_anchor_dt):
    lambda_arn = "arn:aws:lambda:us-east-1:123456789012:function:no-trace-func"

    mock_cloudwatch.get_metric_series.return_value = create_sample_series(
        lambda_arn, "Invocations", "AWS/Lambda", [1.0], sample_anchor_dt
    )

    change_impact = ChangeImpactEvidence(
        change_id="PR-105",
        status="completed",
        change=CodeChangeInput(change_id="PR-105"),
        impacted_resources=[
            ImpactedResource(
                resource_id=lambda_arn,
                resource_type=ResourceType.LAMBDA,
                resource_name="no-trace-func",
                impact=ImpactType.DIRECT,
                confidence=ConfidenceLevel.OBSERVED,
            )
        ],
        impact_paths=[
            ImpactPath(
                source_resource_id=lambda_arn,
                target_resource_id="arn:aws:dynamodb:us-east-1:123456789012:table/UnknownTable",
                relationship=RelationshipType.ACCESSES,
                evidence=EvidenceType.UNKNOWN,
                confidence=ConfidenceLevel.UNAVAILABLE,
            )
        ],
    )

    snapshot = DeploymentSnapshot(
        snapshot_id="snap-105",
        deployment_id="dep-105",
        change_id="PR-105",
        environment=DeploymentEnvironment.SANDBOX,
        status=DeploymentStatus.COMPLETED,
        telemetry_anchor_timestamp=sample_anchor_dt.isoformat(),
        resources=[DeployedResource(resource_id=lambda_arn, resource_type=ResourceType.LAMBDA, resource_name="no-trace-func")],
    )

    pkg = integration_service.assemble_evidence_package(change_impact=change_impact, snapshot=snapshot)

    assert pkg.status == "usable"
    assert pkg.dependency_paths[0].evidence == EvidenceType.UNKNOWN
    assert pkg.dependency_paths[0].confidence == ConfidenceLevel.UNAVAILABLE


# ============================================================================
# TEST 6: Unmapped / Unknown Resource Handled Explicitly
# ============================================================================
def test_unmapped_unknown_resource_handling(integration_service, mock_cloudwatch, sample_anchor_dt):
    change_impact = ChangeImpactEvidence(
        change_id="PR-106",
        status="partially_mapped",
        change=CodeChangeInput(change_id="PR-106"),
        impacted_resources=[],
        unresolved_items=[
            UnresolvedMapping(file_path="docs/README.md", status="unknown", reason="Documentation file unmapped.")
        ],
    )

    snapshot = DeploymentSnapshot(
        snapshot_id="snap-106",
        deployment_id="dep-106",
        change_id="PR-106",
        environment=DeploymentEnvironment.SANDBOX,
        status=DeploymentStatus.COMPLETED,
        telemetry_anchor_timestamp=sample_anchor_dt.isoformat(),
        resources=[],
    )

    pkg = integration_service.assemble_evidence_package(change_impact=change_impact, snapshot=snapshot)

    assert pkg.status == "partially_mapped"
    assert len(pkg.unresolved_items) == 1
    assert pkg.unresolved_items[0].file_path == "docs/README.md"


# ============================================================================
# TEST 7: Multiple Impacted Resources Get Relevant Telemetry
# ============================================================================
def test_multiple_resources_distinct_telemetry(integration_service, mock_cloudwatch, sample_anchor_dt):
    lambda_arn = "arn:aws:lambda:us-east-1:123456789012:function:api-handler"
    dynamo_arn = "arn:aws:dynamodb:us-east-1:123456789012:table/Users"

    def get_series_side_effect(**kwargs):
        r_id = kwargs.get("resource_id")
        m_name = kwargs.get("metric_name")
        start_t = kwargs.get("start_time")
        if r_id == lambda_arn:
            return create_sample_series(r_id, m_name, "AWS/Lambda", [100.0], start_t)
        else:
            return create_sample_series(r_id, m_name, "AWS/DynamoDB", [5.0], start_t)

    mock_cloudwatch.get_metric_series.side_effect = get_series_side_effect

    change_impact = ChangeImpactEvidence(
        change_id="PR-107",
        status="completed",
        change=CodeChangeInput(change_id="PR-107"),
        impacted_resources=[
            ImpactedResource(resource_id=lambda_arn, resource_type=ResourceType.LAMBDA, resource_name="api-handler", impact=ImpactType.DIRECT, confidence=ConfidenceLevel.OBSERVED),
            ImpactedResource(resource_id=dynamo_arn, resource_type=ResourceType.DYNAMODB, resource_name="Users", impact=ImpactType.DOWNSTREAM, confidence=ConfidenceLevel.OBSERVED),
        ],
    )

    snapshot = DeploymentSnapshot(
        snapshot_id="snap-107",
        deployment_id="dep-107",
        change_id="PR-107",
        environment=DeploymentEnvironment.SANDBOX,
        status=DeploymentStatus.COMPLETED,
        telemetry_anchor_timestamp=sample_anchor_dt.isoformat(),
        resources=[
            DeployedResource(resource_id=lambda_arn, resource_type=ResourceType.LAMBDA, resource_name="api-handler"),
            DeployedResource(resource_id=dynamo_arn, resource_type=ResourceType.DYNAMODB, resource_name="Users"),
        ],
    )

    pkg = integration_service.assemble_evidence_package(change_impact=change_impact, snapshot=snapshot)

    lambda_obs = [w for w in pkg.post_deployment_observations if w.resource_id == lambda_arn]
    dynamo_obs = [w for w in pkg.post_deployment_observations if w.resource_id == dynamo_arn]

    assert len(lambda_obs) == 4
    assert len(dynamo_obs) == 4
    assert lambda_obs[0].namespace == "AWS/Lambda"
    assert dynamo_obs[0].namespace == "AWS/DynamoDB"


# ============================================================================
# TEST 8: Preserved Telemetry Anchor Timestamp
# ============================================================================
def test_telemetry_anchor_timestamp_preserved(integration_service, mock_cloudwatch, sample_anchor_dt):
    lambda_arn = "arn:aws:lambda:us-east-1:123456789012:function:handler"

    mock_cloudwatch.get_metric_series.return_value = create_sample_series(
        lambda_arn, "Duration", "AWS/Lambda", [150.0], sample_anchor_dt
    )

    change_impact = ChangeImpactEvidence(
        change_id="PR-108",
        status="completed",
        change=CodeChangeInput(change_id="PR-108"),
        impacted_resources=[ImpactedResource(resource_id=lambda_arn, resource_type=ResourceType.LAMBDA, resource_name="handler", impact=ImpactType.DIRECT, confidence=ConfidenceLevel.OBSERVED)],
    )

    snapshot = DeploymentSnapshot(
        snapshot_id="snap-108",
        deployment_id="dep-108",
        change_id="PR-108",
        environment=DeploymentEnvironment.SANDBOX,
        status=DeploymentStatus.COMPLETED,
        telemetry_anchor_timestamp=sample_anchor_dt.isoformat(),
        resources=[DeployedResource(resource_id=lambda_arn, resource_type=ResourceType.LAMBDA, resource_name="handler")],
    )

    pkg = integration_service.assemble_evidence_package(change_impact=change_impact, snapshot=snapshot)

    assert pkg.telemetry_anchor_timestamp == sample_anchor_dt.isoformat()
    base_win = pkg.baseline_observations[0]
    post_win = pkg.post_deployment_observations[0]

    assert base_win.end_time == sample_anchor_dt.isoformat()
    assert post_win.start_time == sample_anchor_dt.isoformat()


# ============================================================================
# TEST 9: Forecast Values Passed Through Without Modification
# ============================================================================
def test_forecast_values_immutability(integration_service, mock_cloudwatch, sample_anchor_dt):
    lambda_arn = "arn:aws:lambda:us-east-1:123456789012:function:handler"

    mock_cloudwatch.get_metric_series.return_value = create_sample_series(
        lambda_arn, "Duration", "AWS/Lambda", [180.0], sample_anchor_dt
    )

    change_impact = ChangeImpactEvidence(
        change_id="PR-109",
        status="completed",
        change=CodeChangeInput(change_id="PR-109"),
        impacted_resources=[ImpactedResource(resource_id=lambda_arn, resource_type=ResourceType.LAMBDA, resource_name="handler", impact=ImpactType.DIRECT, confidence=ConfidenceLevel.OBSERVED)],
    )

    snapshot = DeploymentSnapshot(
        snapshot_id="snap-109",
        deployment_id="dep-109",
        change_id="PR-109",
        environment=DeploymentEnvironment.SANDBOX,
        status=DeploymentStatus.COMPLETED,
        telemetry_anchor_timestamp=sample_anchor_dt.isoformat(),
        resources=[DeployedResource(resource_id=lambda_arn, resource_type=ResourceType.LAMBDA, resource_name="handler")],
    )

    forecast_input = ResourceForecastInput(
        resource_id=lambda_arn,
        metric_forecasts={
            "Duration": MetricForecast(predicted_value=175.5, lower_bound=160.0, upper_bound=190.0, unit="Milliseconds")
        },
    )

    pkg = integration_service.assemble_evidence_package(
        change_impact=change_impact,
        snapshot=snapshot,
        forecasts=[forecast_input],
    )

    duration_comp = next(c for c in pkg.forecast_comparisons.resources[0].comparisons if c.metric_name == "Duration")
    assert duration_comp.forecast.predicted_value == 175.5
    assert duration_comp.forecast.lower_bound == 160.0
    assert duration_comp.forecast.upper_bound == 190.0


# ============================================================================
# TEST 10: Read-Only Guarantee (No Mutating Calls Executed)
# ============================================================================
def test_read_only_aws_guarantee(integration_service, mock_cloudwatch, sample_anchor_dt):
    lambda_arn = "arn:aws:lambda:us-east-1:123456789012:function:handler"

    mock_cloudwatch.get_metric_series.return_value = create_sample_series(
        lambda_arn, "Invocations", "AWS/Lambda", [10.0], sample_anchor_dt
    )

    change_impact = ChangeImpactEvidence(
        change_id="PR-110",
        status="completed",
        change=CodeChangeInput(change_id="PR-110"),
        impacted_resources=[ImpactedResource(resource_id=lambda_arn, resource_type=ResourceType.LAMBDA, resource_name="handler", impact=ImpactType.DIRECT, confidence=ConfidenceLevel.OBSERVED)],
    )

    snapshot = DeploymentSnapshot(
        snapshot_id="snap-110",
        deployment_id="dep-110",
        change_id="PR-110",
        environment=DeploymentEnvironment.SANDBOX,
        status=DeploymentStatus.COMPLETED,
        telemetry_anchor_timestamp=sample_anchor_dt.isoformat(),
        resources=[DeployedResource(resource_id=lambda_arn, resource_type=ResourceType.LAMBDA, resource_name="handler")],
    )

    pkg = integration_service.assemble_evidence_package(change_impact=change_impact, snapshot=snapshot)

    assert pkg.read_only_verified is True
    for call in mock_cloudwatch.mock_calls:
        name = call[0]
        assert "put_" not in name.lower()
        assert "delete_" not in name.lower()
        assert "create_" not in name.lower()
        assert "update_" not in name.lower()
