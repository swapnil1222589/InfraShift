"""
Unit tests for AWS Code Change → AWS Resource Impact Mapping module.
"""

from unittest.mock import MagicMock
from aws.config.aws_config import AWSClientFactory, AWSConfig
from aws.discovery.dependency_discovery import DependencyDiscovery
from aws.impact.code_change_models import (
    CodeChangeInput,
    FileChange,
    FileChangeStatus,
    ImpactType,
    ChangeImpactEvidence,
)
from aws.impact.component_mapper import FileToComponentMapper
from aws.impact.impact_mapping import ImpactMappingService
from aws.models.aws_models import (
    ResourceType,
    EvidenceType,
    ConfidenceLevel,
    RelationshipType,
    NormalizedResource,
    DependencyGraph,
    DependencyGraphNode,
    DependencyGraphEdge,
    DependencyDiscoveryResult,
    NormalizedDependency,
)


def test_file_to_component_mapper_deterministic():
    resources = [
        NormalizedResource(
            resource_id="arn:aws:lambda:us-east-1:123:function:orders-handler",
            resource_type=ResourceType.LAMBDA,
            resource_name="orders-handler",
            region="us-east-1",
            metadata={"handler": "src/orders/handler.lambda_handler"},
        ),
        NormalizedResource(
            resource_id="arn:aws:dynamodb:us-east-1:123:table/OrdersTable",
            resource_type=ResourceType.DYNAMODB,
            resource_name="OrdersTable",
            region="us-east-1",
            metadata={"table_name": "OrdersTable"},
        ),
    ]

    mapper = FileToComponentMapper(custom_mappings={"src/custom/path.py": "OrdersTable"})

    # 1. Lambda Handler match
    m1 = mapper.map_file_to_resource("src/orders/handler.py", resources)
    assert m1.status == "mapped"
    assert m1.component_name == "orders-handler"
    assert m1.resource_id == "arn:aws:lambda:us-east-1:123:function:orders-handler"
    assert m1.confidence == ConfidenceLevel.OBSERVED

    # 2. Custom Mapping match
    m2 = mapper.map_file_to_resource("src/custom/path.py", resources)
    assert m2.status == "mapped"
    assert m2.component_name == "OrdersTable"
    assert m2.resource_id == "arn:aws:dynamodb:us-east-1:123:table/OrdersTable"

    # 3. Unmappable file (NO GUESSING)
    m3 = mapper.map_file_to_resource("docs/architecture.md", resources)
    assert m3.status == "unknown"
    assert m3.resource_id is None
    assert "No application component mapping available." in m3.reason


def test_impact_mapping_direct_downstream_upstream():
    mock_config = AWSConfig(region_name="us-east-1")
    discovery_mock = MagicMock()

    # Discovered resources
    res_api = NormalizedResource(
        resource_id="arn:aws:apigateway:us-east-1::/restapis/api123",
        resource_type=ResourceType.API_GATEWAY,
        resource_name="orders-api",
        region="us-east-1",
    )
    res_lambda = NormalizedResource(
        resource_id="arn:aws:lambda:us-east-1:123:function:create-order-fn",
        resource_type=ResourceType.LAMBDA,
        resource_name="create-order-fn",
        region="us-east-1",
        metadata={"handler": "src/orders/service.handler"},
    )
    res_ddb = NormalizedResource(
        resource_id="arn:aws:dynamodb:us-east-1:123:table/OrdersTable",
        resource_type=ResourceType.DYNAMODB,
        resource_name="OrdersTable",
        region="us-east-1",
    )

    discovery_mock.resource_discovery.discover_all.return_value = [res_api, res_lambda, res_ddb]


    # Graph with API Gateway -> Lambda -> DynamoDB
    graph = DependencyGraph(
        nodes=[
            DependencyGraphNode(id=res_api.resource_id, type=ResourceType.API_GATEWAY, name="orders-api"),
            DependencyGraphNode(id=res_lambda.resource_id, type=ResourceType.LAMBDA, name="create-order-fn"),
            DependencyGraphNode(id=res_ddb.resource_id, type=ResourceType.DYNAMODB, name="OrdersTable"),
        ],
        edges=[
            DependencyGraphEdge(
                source=res_api.resource_id,
                target=res_lambda.resource_id,
                relationship=RelationshipType.ROUTES_TO,
                evidence=EvidenceType.AWS_CONFIGURATION,
                confidence=ConfidenceLevel.OBSERVED,
            ),
            DependencyGraphEdge(
                source=res_lambda.resource_id,
                target=res_ddb.resource_id,
                relationship=RelationshipType.ACCESSES,
                evidence=EvidenceType.XRAY,
                confidence=ConfidenceLevel.OBSERVED,
            ),
        ],
    )

    discovery_mock.discover_dependencies.return_value = DependencyDiscoveryResult(
        dependencies=[],
        graph=graph,
        evidence_status=ConfidenceLevel.OBSERVED,
    )

    service = ImpactMappingService(dependency_discovery=discovery_mock)

    # Change modifying src/orders/service.py (maps directly to create-order-fn)
    change = CodeChangeInput(
        change_id="PR-42",
        commit_sha="abc123def",
        files_changed=[
            FileChange(path="src/orders/service.py", status=FileChangeStatus.MODIFIED, additions=10, deletions=2),
            FileChange(path="unknown/random_script.py", status=FileChangeStatus.ADDED, additions=5, deletions=0),
        ],
    )

    evidence_pkg: ChangeImpactEvidence = service.analyze_change_impact(change)

    assert evidence_pkg.change_id == "PR-42"
    assert evidence_pkg.status == "partially_mapped"
    assert len(evidence_pkg.changed_files) == 2
    assert len(evidence_pkg.unresolved_items) == 1
    assert evidence_pkg.unresolved_items[0].file_path == "unknown/random_script.py"

    # Verify Impacted Resources
    impacted_ids = {r.resource_id: r for r in evidence_pkg.impacted_resources}
    assert len(impacted_ids) == 3

    # Direct: Lambda
    lambda_impact = impacted_ids[res_lambda.resource_id]
    assert lambda_impact.impact == ImpactType.DIRECT
    assert lambda_impact.confidence == ConfidenceLevel.OBSERVED
    assert "Invocations" in lambda_impact.telemetry_metrics
    assert "Duration" in lambda_impact.telemetry_metrics

    # Downstream: DynamoDB
    ddb_impact = impacted_ids[res_ddb.resource_id]
    assert ddb_impact.impact == ImpactType.DOWNSTREAM
    assert ddb_impact.confidence == ConfidenceLevel.OBSERVED
    assert "ConsumedReadCapacityUnits" in ddb_impact.telemetry_metrics

    # Upstream: API Gateway
    api_impact = impacted_ids[res_api.resource_id]
    assert api_impact.impact == ImpactType.UPSTREAM
    assert api_impact.confidence == ConfidenceLevel.OBSERVED

    # Check Impact Paths
    assert len(evidence_pkg.impact_paths) == 2

    # Check Telemetry References
    telemetry_map = {tr.resource_id: tr for tr in evidence_pkg.telemetry_references}
    assert telemetry_map[res_lambda.resource_id].namespace == "AWS/Lambda"
    assert telemetry_map[res_ddb.resource_id].namespace == "AWS/DynamoDB"


def test_graph_traversal_cycle_prevention():
    mock_config = AWSConfig(region_name="us-east-1")
    discovery_mock = MagicMock()

    fn1_arn = "arn:aws:lambda:us-east-1:123:function:fn1"
    fn2_arn = "arn:aws:lambda:us-east-1:123:function:fn2"


    res_fn1 = NormalizedResource(
        resource_id=fn1_arn,
        resource_type=ResourceType.LAMBDA,
        resource_name="fn1",
        region="us-east-1",
        metadata={"handler": "fn1.handler"},
    )

    discovery_mock.resource_discovery.discover_all.return_value = [res_fn1]

    # Cyclic graph: fn1 -> fn2 -> fn1
    graph = DependencyGraph(
        nodes=[
            DependencyGraphNode(id=fn1_arn, type=ResourceType.LAMBDA, name="fn1"),
            DependencyGraphNode(id=fn2_arn, type=ResourceType.LAMBDA, name="fn2"),
        ],
        edges=[
            DependencyGraphEdge(
                source=fn1_arn,
                target=fn2_arn,
                relationship=RelationshipType.INVOKES,
                evidence=EvidenceType.AWS_CONFIGURATION,
                confidence=ConfidenceLevel.OBSERVED,
            ),
            DependencyGraphEdge(
                source=fn2_arn,
                target=fn1_arn,
                relationship=RelationshipType.INVOKES,
                evidence=EvidenceType.AWS_CONFIGURATION,
                confidence=ConfidenceLevel.OBSERVED,
            ),
        ],
    )

    discovery_mock.discover_dependencies.return_value = DependencyDiscoveryResult(
        dependencies=[],
        graph=graph,
        evidence_status=ConfidenceLevel.OBSERVED,
    )

    service = ImpactMappingService(dependency_discovery=discovery_mock)
    change = CodeChangeInput(
        change_id="PR-CYCLE",
        files_changed=[FileChange(path="fn1.py")],
    )

    # Must complete without infinite loop recursion or stack overflow!
    evidence_pkg = service.analyze_change_impact(change)

    assert evidence_pkg.status == "completed"
    assert len(evidence_pkg.impacted_resources) == 2
