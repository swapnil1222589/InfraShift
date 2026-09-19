"""
Unit tests for AWS Deployment & Event Tracking layer.
"""

from unittest.mock import MagicMock
from botocore.exceptions import ClientError
from aws.config.aws_config import AWSClientFactory, AWSConfig
from aws.models.aws_models import ResourceType, ConfidenceLevel
from aws.impact.code_change_models import (

    CodeChangeInput,
    FileChange,
    ImpactedResource,
    ImpactType,
    ChangeImpactEvidence,
)
from aws.events.event_models import (
    DeploymentEvent,
    DeploymentStatus,
    DeploymentEnvironment,
    DeployedResource,
    DeploymentSnapshot,
)
from aws.events.eventbridge import EventBridgeIntegration
from aws.events.deployment_tracking import (
    DeploymentRepository,
    DeploymentTrackingService,
)


def test_deployment_event_normalization_and_timestamps():
    event = DeploymentEvent(
        event_id="evt-101",
        deployment_id="deploy-123",
        change_id="PR-102",
        commit_sha="a1b2c3d4",
        environment=DeploymentEnvironment.SANDBOX,
        status=DeploymentStatus.STARTED,
        started_at="2026-09-19T16:00:00Z",
        completed_at=None,
    )

    assert event.deployment_id == "deploy-123"
    assert event.status == DeploymentStatus.STARTED
    assert event.environment == DeploymentEnvironment.SANDBOX
    assert event.started_at == "2026-09-19T16:00:00Z"
    assert event.completed_at is None  # Strict null preservation


def test_eventbridge_payload_parser():
    mock_config = AWSConfig(region_name="us-east-1")
    factory = AWSClientFactory(config=mock_config)
    eb = EventBridgeIntegration(client_factory=factory)

    raw_payload = {
        "id": "eb-evt-999",
        "region": "us-east-1",
        "detail": {
            "deploymentId": "deploy-456",
            "git_sha": "f6e5d4c3",
            "pull_request_id": "PR-55",
            "env": "STAGING",
            "state": "SUCCEEDED",
            "startTime": "2026-09-19T16:00:00Z",
            "endTime": "2026-09-19T16:02:00Z",
            "resources": [
                "arn:aws:lambda:us-east-1:123:function:orders-fn",
                "arn:aws:dynamodb:us-east-1:123:table/OrdersTable",
            ],
        },
    }

    event = eb.parse_eventbridge_payload(raw_payload)

    assert event is not None
    assert event.event_id == "eb-evt-999"
    assert event.deployment_id == "deploy-456"
    assert event.commit_sha == "f6e5d4c3"
    assert event.change_id == "PR-55"
    assert event.environment == DeploymentEnvironment.STAGING
    assert event.status == DeploymentStatus.COMPLETED
    assert len(event.resources) == 2
    assert event.resources[0].resource_type == ResourceType.LAMBDA
    assert event.resources[1].resource_type == ResourceType.DYNAMODB


def test_eventbridge_invalid_payload_handling():
    mock_config = AWSConfig(region_name="us-east-1")
    factory = AWSClientFactory(config=mock_config)
    eb = EventBridgeIntegration(client_factory=factory)

    # Missing deployment_id
    assert eb.parse_eventbridge_payload({"id": "evt-1"}) is None
    # Empty payload
    assert eb.parse_eventbridge_payload({}) is None


def test_eventbridge_put_deployment_event():
    mock_config = AWSConfig(region_name="us-east-1")
    events_client = MagicMock()
    events_client.put_events.return_value = {"FailedEntryCount": 0}

    factory = AWSClientFactory(
        config=mock_config,
        custom_clients={"events": events_client},
    )
    eb = EventBridgeIntegration(client_factory=factory)

    event = DeploymentEvent(
        event_id="evt-300",
        deployment_id="deploy-300",
        status=DeploymentStatus.COMPLETED,
    )

    res = eb.put_deployment_event(event)

    assert res["status"] == "success"
    assert events_client.put_events.called


def test_deployment_lifecycle_transitions():
    service = DeploymentTrackingService()

    # 1. Pending -> Started
    e1 = DeploymentEvent(
        event_id="evt-1",
        deployment_id="d-100",
        status=DeploymentStatus.PENDING,
        started_at="2026-09-19T16:00:00Z",
    )
    snap1 = service.record_event(e1)
    assert snap1.status == DeploymentStatus.PENDING

    e2 = DeploymentEvent(
        event_id="evt-2",
        deployment_id="d-100",
        status=DeploymentStatus.STARTED,
        started_at="2026-09-19T16:00:05Z",
    )
    snap2 = service.record_event(e2)
    assert snap2.status == DeploymentStatus.STARTED

    # 2. Started -> Completed
    e3 = DeploymentEvent(
        event_id="evt-3",
        deployment_id="d-100",
        status=DeploymentStatus.COMPLETED,
        completed_at="2026-09-19T16:01:30Z",
    )
    snap3 = service.record_event(e3)
    assert snap3.status == DeploymentStatus.COMPLETED
    assert snap3.telemetry_anchor_timestamp == "2026-09-19T16:01:30Z"

    # 3. Invalid Transition: Completed -> Pending (Rejected)
    e4 = DeploymentEvent(
        event_id="evt-4",
        deployment_id="d-100",
        status=DeploymentStatus.PENDING,
    )
    snap4 = service.record_event(e4)
    assert snap4.status == DeploymentStatus.COMPLETED  # Preserves completed state


def test_event_deduplication():
    service = DeploymentTrackingService()

    event = DeploymentEvent(
        event_id="evt-dup",
        deployment_id="d-dup",
        status=DeploymentStatus.COMPLETED,
        completed_at="2026-09-19T16:05:00Z",
    )

    snap_first = service.record_event(event)
    snap_second = service.record_event(event)

    assert snap_first.snapshot_id == snap_second.snapshot_id
    assert snap_second.status == DeploymentStatus.COMPLETED


def test_code_change_and_resource_association_with_evidence():
    service = DeploymentTrackingService()

    # Simulated ChangeImpactEvidence package
    change_input = CodeChangeInput(
        change_id="PR-88",
        commit_sha="c88c88",
        files_changed=[FileChange(path="src/orders/service.py")],
    )

    evidence = ChangeImpactEvidence(
        change_id="PR-88",
        change=change_input,
        impacted_resources=[
            ImpactedResource(
                resource_id="arn:aws:lambda:us-east-1:123:function:orders-fn",
                resource_type=ResourceType.LAMBDA,
                resource_name="orders-fn",
                impact=ImpactType.DIRECT,
                confidence=ConfidenceLevel.OBSERVED,
            ),
            ImpactedResource(
                resource_id="arn:aws:dynamodb:us-east-1:123:table/OrdersTable",
                resource_type=ResourceType.DYNAMODB,
                resource_name="OrdersTable",
                impact=ImpactType.DOWNSTREAM,
                confidence=ConfidenceLevel.OBSERVED,
            ),
        ],
    )

    event = DeploymentEvent(
        event_id="evt-assoc",
        deployment_id="d-assoc",
        environment=DeploymentEnvironment.STAGING,
        status=DeploymentStatus.COMPLETED,
        completed_at="2026-09-19T16:10:00Z",
    )

    snapshot = service.record_event(event, evidence=evidence)

    assert snapshot.change_id == "PR-88"
    assert snapshot.commit_sha == "c88c88"
    assert len(snapshot.resources) == 2

    # Verify repository lookup
    by_change = service.find_by_change("PR-88")
    assert len(by_change) == 1
    assert by_change[0].deployment_id == "d-assoc"

    by_commit = service.find_by_commit("c88c88")
    assert len(by_commit) == 1
    assert by_commit[0].deployment_id == "d-assoc"
