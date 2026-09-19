"""
Unit tests for AWS DependencyDiscovery orchestrator and graph generation module.
"""

from unittest.mock import MagicMock
from aws.config.aws_config import AWSClientFactory, AWSConfig
from aws.discovery.dependency_discovery import DependencyDiscovery
from aws.models.aws_models import (
    ResourceType,
    ConfidenceLevel,
    EvidenceType,
    RelationshipType,
    NormalizedResource,
    NormalizedDependency,
    APIGatewayMetadata,
    LambdaMetadata,
    DynamoDBMetadata,
    TelemetrySeries,
)



def test_dependency_discovery_full_flow():
    mock_config = AWSConfig(region_name="us-east-1")

    apigw_client = MagicMock()
    apigw2_client = MagicMock()
    lambda_client = MagicMock()
    ddb_client = MagicMock()
    xray_client = MagicMock()
    cw_client = MagicMock()

    # 1. API Gateway v1 mock
    paginator_apigw = MagicMock()
    paginator_apigw.paginate.return_value = [
        {"items": [{"id": "api1", "name": "orders-api", "endpointConfiguration": {"types": ["REGIONAL"]}}]}
    ]
    apigw_client.get_paginator.return_value = paginator_apigw
    apigw_client.get_stages.return_value = {"item": [{"stageName": "prod"}]}
    apigw_client.get_resources.return_value = {
        "items": [
            {
                "id": "res1",
                "path": "/orders",
                "resourceMethods": {"POST": {}},
            }
        ]
    }
    apigw_client.get_integration.return_value = {
        "type": "AWS_PROXY",
        "uri": "arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:123456789012:function:create-order-fn/invocations",
    }

    # 2. API Gateway v2 mock (empty)
    apigw2_client.get_apis.return_value = {"Items": []}

    # 3. Lambda mock
    paginator_lambda = MagicMock()
    paginator_lambda.paginate.return_value = [
        {
            "Functions": [
                {
                    "FunctionName": "create-order-fn",
                    "FunctionArn": "arn:aws:lambda:us-east-1:123456789012:function:create-order-fn",
                    "Runtime": "python3.12",
                    "Environment": {
                        "Variables": {
                            "ORDERS_TABLE": "OrdersTable",
                        }
                    },
                }
            ]
        }
    ]
    lambda_client.get_paginator.return_value = paginator_lambda
    lambda_client.get_function.return_value = {
        "Configuration": {
            "FunctionName": "create-order-fn",
            "FunctionArn": "arn:aws:lambda:us-east-1:123456789012:function:create-order-fn",
            "Runtime": "python3.12",
            "Environment": {"Variables": {"ORDERS_TABLE": "OrdersTable"}},
        },
        "Tags": {},
    }

    # 4. DynamoDB mock
    paginator_ddb = MagicMock()
    paginator_ddb.paginate.return_value = [{"TableNames": ["OrdersTable"]}]
    ddb_client.get_paginator.return_value = paginator_ddb
    ddb_client.describe_table.return_value = {
        "Table": {
            "TableName": "OrdersTable",
            "TableArn": "arn:aws:dynamodb:us-east-1:123456789012:table/OrdersTable",
            "TableStatus": "ACTIVE",
            "ItemCount": 100,
        }
    }

    # 5. X-Ray mock (empty so inferred relationship is tested)
    xray_client.get_service_graph.return_value = {"Services": []}
    xray_client.get_trace_summaries.return_value = {"TraceSummaries": []}

    factory = AWSClientFactory(
        config=mock_config,
        custom_clients={
            "apigateway": apigw_client,
            "apigatewayv2": apigw2_client,
            "lambda": lambda_client,
            "dynamodb": ddb_client,
            "xray": xray_client,
            "cloudwatch": cw_client,
        },
    )

    orchestrator = DependencyDiscovery(client_factory=factory)
    result = orchestrator.discover_dependencies()

    assert len(result.dependencies) == 2
    assert result.evidence_status == ConfidenceLevel.OBSERVED  # API Gateway dependency is observed

    # Check API Gateway → Lambda observed dependency
    dep_apigw = next(d for d in result.dependencies if d.source_type == ResourceType.API_GATEWAY)
    assert dep_apigw.relationship == RelationshipType.ROUTES_TO
    assert dep_apigw.evidence_type == EvidenceType.AWS_CONFIGURATION
    assert dep_apigw.confidence == ConfidenceLevel.OBSERVED
    assert dep_apigw.target_resource_id == "arn:aws:lambda:us-east-1:123456789012:function:create-order-fn"

    # Check Lambda → DynamoDB inferred dependency
    dep_lambda = next(d for d in result.dependencies if d.source_type == ResourceType.LAMBDA)
    assert dep_lambda.relationship == RelationshipType.ACCESSES
    assert dep_lambda.confidence == ConfidenceLevel.INFERRED
    assert "OrdersTable" in dep_lambda.target_resource_id

    # Check Dependency Graph
    graph = result.graph
    assert len(graph.nodes) >= 3
    assert len(graph.edges) == 2


def test_observed_over_inferred_precedence():
    mock_config = AWSConfig(region_name="us-east-1")
    orchestrator = DependencyDiscovery(config=mock_config)

    inferred_dep = NormalizedDependency(
        source_resource_id="arn:aws:lambda:us-east-1:123:function:orders",
        source_type=ResourceType.LAMBDA,
        target_resource_id="arn:aws:dynamodb:us-east-1:123:table/Orders",
        target_type=ResourceType.DYNAMODB,
        relationship=RelationshipType.ACCESSES,
        evidence_type=EvidenceType.APPLICATION_METADATA,
        confidence=ConfidenceLevel.INFERRED,
    )

    observed_dep = NormalizedDependency(
        source_resource_id="arn:aws:lambda:us-east-1:123:function:orders",
        source_type=ResourceType.LAMBDA,
        target_resource_id="arn:aws:dynamodb:us-east-1:123:table/Orders",
        target_type=ResourceType.DYNAMODB,
        relationship=RelationshipType.ACCESSES,
        evidence_type=EvidenceType.XRAY,
        confidence=ConfidenceLevel.OBSERVED,
        metadata={"trace_id": "1-abc"},
    )

    merged = orchestrator._merge_dependencies([inferred_dep, observed_dep])

    assert len(merged) == 1
    assert merged[0].confidence == ConfidenceLevel.OBSERVED
    assert merged[0].evidence_type == EvidenceType.XRAY
    assert merged[0].metadata["trace_id"] == "1-abc"


def test_empty_dependency_graph_and_telemetry_connection():
    mock_config = AWSConfig(region_name="us-east-1")
    apigw_client = MagicMock()
    apigw2_client = MagicMock()
    lambda_client = MagicMock()
    ddb_client = MagicMock()
    xray_client = MagicMock()
    cw_client = MagicMock()

    # Return empty lists
    apigw_client.get_paginator.return_value.paginate.return_value = [{"items": []}]
    apigw2_client.get_apis.return_value = {"Items": []}
    lambda_client.get_paginator.return_value.paginate.return_value = [{"Functions": []}]
    ddb_client.get_paginator.return_value.paginate.return_value = [{"TableNames": []}]
    xray_client.get_service_graph.return_value = {"Services": []}
    xray_client.get_trace_summaries.return_value = {"TraceSummaries": []}

    cw_client.get_metric_statistics.return_value = {"Datapoints": []}

    factory = AWSClientFactory(
        config=mock_config,
        custom_clients={
            "apigateway": apigw_client,
            "apigatewayv2": apigw2_client,
            "lambda": lambda_client,
            "dynamodb": ddb_client,
            "xray": xray_client,
            "cloudwatch": cw_client,
        },
    )

    orchestrator = DependencyDiscovery(client_factory=factory)
    result = orchestrator.discover_dependencies()

    assert result.dependencies == []
    assert result.graph.nodes == []
    assert result.graph.edges == []
    assert result.evidence_status == ConfidenceLevel.UNAVAILABLE

    # Test historical telemetry fetching for node without duplication
    dummy_node = orchestrator._build_dependency_graph(
        [],
        [
            NormalizedDependency(
                source_resource_id="arn:aws:lambda:us-east-1:123:function:orders",
                source_type=ResourceType.LAMBDA,
                target_resource_id="arn:aws:dynamodb:us-east-1:123:table/Orders",
                target_type=ResourceType.DYNAMODB,
                relationship=RelationshipType.ACCESSES,
                evidence_type=EvidenceType.XRAY,
                confidence=ConfidenceLevel.OBSERVED,
            )
        ],
    ).nodes[0]

    telemetry_series = orchestrator.get_resource_telemetry(dummy_node, "Invocations")
    assert isinstance(telemetry_series, TelemetrySeries)
    assert telemetry_series.metric_name == "Invocations"
    assert telemetry_series.datapoints == []
