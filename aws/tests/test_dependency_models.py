"""
Unit tests for normalized AWS dependency, evidence, and graph models.
"""

from datetime import datetime
from aws.models.aws_models import (
    ResourceType,
    EvidenceType,
    ConfidenceLevel,
    RelationshipType,
    NormalizedDependency,
    XRayTraceEvidence,
    DependencyGraphNode,
    DependencyGraphEdge,
    DependencyGraph,
    DependencyDiscoveryResult,
)


def test_normalized_dependency_model():
    dep = NormalizedDependency(
        source_resource_id="arn:aws:apigateway:us-east-1::/restapis/api123",
        source_type=ResourceType.API_GATEWAY,
        target_resource_id="arn:aws:lambda:us-east-1:123456789012:function:orders-fn",
        target_type=ResourceType.LAMBDA,
        relationship=RelationshipType.ROUTES_TO,
        evidence_type=EvidenceType.AWS_CONFIGURATION,
        confidence=ConfidenceLevel.OBSERVED,
        metadata={"route": "/orders"},
    )

    assert dep.source_resource_id == "arn:aws:apigateway:us-east-1::/restapis/api123"
    assert dep.source_type == ResourceType.API_GATEWAY
    assert dep.target_type == ResourceType.LAMBDA
    assert dep.relationship == RelationshipType.ROUTES_TO
    assert dep.evidence_type == EvidenceType.AWS_CONFIGURATION
    assert dep.confidence == ConfidenceLevel.OBSERVED
    assert dep.metadata["route"] == "/orders"
    assert isinstance(dep.observed_at, str)


def test_xray_trace_evidence_model():
    evidence = XRayTraceEvidence(
        trace_id="1-5759e988-bd862e3fe1be46a994272793",
        timestamp=datetime.now().isoformat(),
        source={"type": "lambda", "resource_id": "arn:aws:lambda:us-east-1:123:function:orders"},
        target={"type": "dynamodb", "resource_id": "arn:aws:dynamodb:us-east-1:123:table/OrdersTable"},
        duration_ms=45.2,
        error=False,
        fault=False,
    )

    assert evidence.trace_id == "1-5759e988-bd862e3fe1be46a994272793"
    assert evidence.duration_ms == 45.2
    assert evidence.evidence_type == EvidenceType.XRAY
    assert evidence.confidence == ConfidenceLevel.OBSERVED


def test_dependency_graph_models():
    node1 = DependencyGraphNode(
        id="api-1",
        type=ResourceType.API_GATEWAY,
        name="orders-api",
    )
    node2 = DependencyGraphNode(
        id="lambda-1",
        type=ResourceType.LAMBDA,
        name="orders-function",
    )
    node3 = DependencyGraphNode(
        id="ddb-1",
        type=ResourceType.DYNAMODB,
        name="orders-table",
    )

    edge1 = DependencyGraphEdge(
        source="api-1",
        target="lambda-1",
        relationship=RelationshipType.ROUTES_TO,
        evidence=EvidenceType.AWS_CONFIGURATION,
        confidence=ConfidenceLevel.OBSERVED,
    )
    edge2 = DependencyGraphEdge(
        source="lambda-1",
        target="ddb-1",
        relationship=RelationshipType.ACCESSES,
        evidence=EvidenceType.XRAY,
        confidence=ConfidenceLevel.OBSERVED,
    )

    graph = DependencyGraph(
        nodes=[node1, node2, node3],
        edges=[edge1, edge2],
    )

    assert len(graph.nodes) == 3
    assert len(graph.edges) == 2

    # Dump dict and check structure
    data = graph.model_dump()
    assert data["nodes"][0]["name"] == "orders-api"
    assert data["edges"][0]["relationship"] == "routes_to"
    assert data["edges"][1]["evidence"] == "xray"


def test_dependency_discovery_result():
    res = DependencyDiscoveryResult(
        dependencies=[],
        graph=DependencyGraph(),
        evidence_status=ConfidenceLevel.UNAVAILABLE,
        reason="No X-Ray traces found for the requested time window.",
    )

    assert res.dependencies == []
    assert res.evidence_status == ConfidenceLevel.UNAVAILABLE
    assert "No X-Ray traces" in res.reason
