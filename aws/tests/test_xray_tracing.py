"""
Unit tests for AWS X-Ray Tracing evidence extraction module.
"""

import json
from unittest.mock import MagicMock
from botocore.exceptions import ClientError
from aws.config.aws_config import AWSClientFactory, AWSConfig
from aws.tracing.xray import XRayTracing
from aws.models.aws_models import ResourceType, ConfidenceLevel, EvidenceType


def test_xray_service_graph_parsing():
    mock_config = AWSConfig(region_name="us-east-1")
    xray_client = MagicMock()

    xray_client.get_service_graph.return_value = {
        "Services": [
            {
                "ReferenceId": 1,
                "Name": "orders-api",
                "Type": "AWS::ApiGateway",
                "Edges": [{"TargetId": 2}],
            },
            {
                "ReferenceId": 2,
                "Name": "order-processor-fn",
                "Type": "AWS::Lambda::Function",
                "Edges": [{"TargetId": 3}],
            },
            {
                "ReferenceId": 3,
                "Name": "OrdersTable",
                "Type": "AWS::DynamoDB::Table",
                "Edges": [],
            },
        ]
    }
    xray_client.get_trace_summaries.return_value = {"TraceSummaries": []}

    factory = AWSClientFactory(
        config=mock_config,
        custom_clients={"xray": xray_client},
    )
    xray = XRayTracing(factory)

    evidences, deps = xray.discover_trace_evidence("2026-09-19T00:00:00Z", "2026-09-19T01:00:00Z")

    assert len(deps) == 2
    d1, d2 = deps[0], deps[1]

    assert d1.source_type == ResourceType.API_GATEWAY
    assert d1.target_type == ResourceType.LAMBDA
    assert d1.relationship == "invokes"
    assert d1.confidence == ConfidenceLevel.OBSERVED

    assert d2.source_type == ResourceType.LAMBDA
    assert d2.target_type == ResourceType.DYNAMODB
    assert d2.relationship == "accesses"
    assert d2.confidence == ConfidenceLevel.OBSERVED


def test_xray_batch_trace_segment_parsing():
    mock_config = AWSConfig(region_name="us-east-1")
    xray_client = MagicMock()

    xray_client.get_service_graph.return_value = {"Services": []}
    xray_client.get_trace_summaries.return_value = {
        "TraceSummaries": [{"Id": "1-5759e988-bd862e3fe1be46a994272793"}]
    }

    doc_segment = {
        "name": "arn:aws:lambda:us-east-1:123456789012:function:order-api",
        "origin": "AWS::Lambda::Function",
        "start_time": 1700000000.0,
        "end_time": 1700000000.05,
        "error": False,
        "fault": False,
        "subsegments": [
            {
                "name": "DynamoDB",
                "namespace": "aws",
                "start_time": 1700000000.01,
                "end_time": 1700000000.04,
                "aws": {
                    "table_name": "OrdersTable",
                    "operation": "PutItem",
                },
                "error": False,
                "fault": False,
            }
        ],
    }

    xray_client.batch_get_traces.return_value = {
        "Traces": [
            {
                "Id": "1-5759e988-bd862e3fe1be46a994272793",
                "Segments": [{"Document": json.dumps(doc_segment)}],
            }
        ]
    }

    factory = AWSClientFactory(
        config=mock_config,
        custom_clients={"xray": xray_client},
    )
    xray = XRayTracing(factory)

    evidences, deps = xray.discover_trace_evidence()

    assert len(evidences) == 1
    assert len(deps) == 1

    ev = evidences[0]
    assert ev.trace_id == "1-5759e988-bd862e3fe1be46a994272793"
    assert ev.source["resource_id"] == "arn:aws:lambda:us-east-1:123456789012:function:order-api"
    assert "OrdersTable" in ev.target["resource_id"]
    assert ev.evidence_type == EvidenceType.XRAY
    assert ev.confidence == ConfidenceLevel.OBSERVED
    assert ev.duration_ms == 30.0

    dep = deps[0]
    assert dep.source_type == ResourceType.LAMBDA
    assert dep.target_type == ResourceType.DYNAMODB
    assert dep.relationship == "accesses"
    assert dep.confidence == ConfidenceLevel.OBSERVED


def test_xray_missing_trace_data_and_permission_denied():
    mock_config = AWSConfig(region_name="us-west-2")
    xray_client = MagicMock()

    error_resp = {"Error": {"Code": "AccessDeniedException", "Message": "User is not authorized to perform: xray:GetServiceGraph"}}
    xray_client.get_service_graph.side_effect = ClientError(error_resp, "GetServiceGraph")
    xray_client.get_trace_summaries.side_effect = ClientError(error_resp, "GetTraceSummaries")

    factory = AWSClientFactory(
        config=mock_config,
        custom_clients={"xray": xray_client},
    )
    xray = XRayTracing(factory)

    evidences, deps = xray.discover_trace_evidence()

    assert evidences == []
    assert deps == []
