"""
AWS Resource Impact Mapping Engine.
Analyzes code change inputs, maps changed files to AWS resources, traverses dependency graphs
to identify direct, downstream, and upstream impacts, and attaches historical CloudWatch telemetry references.
Outputs a normalized ChangeImpactEvidence package for downstream AI reasoning.
"""

import logging
from typing import List, Dict, Set, Optional, Tuple, Any

from aws.config.aws_config import AWSClientFactory, AWSConfig
from aws.models.aws_models import (
    ResourceType,
    EvidenceType,
    ConfidenceLevel,
    RelationshipType,
    DependencyGraph,
    DependencyGraphNode,
    DependencyGraphEdge,
    DependencyDiscoveryResult,
)
from aws.telemetry.metrics import LambdaMetrics, DynamoDBMetrics
from aws.discovery.dependency_discovery import DependencyDiscovery
from aws.impact.code_change_models import (
    ImpactType,
    FileChange,
    CodeChangeInput,
    ComponentMapping,
    ImpactedResource,
    ImpactPathStep,
    ImpactPath,
    ResourceTelemetryReference,
    UnresolvedMapping,
    ChangeImpactEvidence,
)
from aws.impact.component_mapper import FileToComponentMapper

logger = logging.getLogger("infrashift.aws.impact.mapping")


# Telemetry metrics dictionary mapping resource types to metric lists
RESOURCE_TELEMETRY_MAP: Dict[ResourceType, Tuple[str, List[str]]] = {
    ResourceType.LAMBDA: ("AWS/Lambda", LambdaMetrics.ALL_DEFAULT),
    ResourceType.DYNAMODB: ("AWS/DynamoDB", DynamoDBMetrics.ALL_DEFAULT),
    ResourceType.API_GATEWAY: ("AWS/ApiGateway", ["Count", "Latency", "4XXError", "5XXError"]),
}


class ImpactMappingService:
    """
    Main service for computing code change impact on AWS infrastructure resources.
    """

    def __init__(
        self,
        dependency_discovery: Optional[DependencyDiscovery] = None,
        custom_mappings: Optional[Dict[str, str]] = None,
        client_factory: Optional[AWSClientFactory] = None,
        config: Optional[AWSConfig] = None,
    ):
        if dependency_discovery:
            self.discovery = dependency_discovery
        else:
            self.discovery = DependencyDiscovery(
                client_factory=client_factory,
                config=config or AWSConfig(),
            )

        self.mapper = FileToComponentMapper(custom_mappings=custom_mappings)

    def analyze_change_impact(
        self,
        change_input: CodeChangeInput,
    ) -> ChangeImpactEvidence:
        """
        Analyze a CodeChangeInput and return a normalized ChangeImpactEvidence package.

        :param change_input: CodeChangeInput detailing commit/PR and changed files.
        :return: ChangeImpactEvidence package containing mapped resources, impact paths, and telemetry refs.
        """
        logger.info("Starting AWS resource impact analysis for change: %s", change_input.change_id)

        # 1. Run AWS Resource & Dependency Discovery
        discovery_result: DependencyDiscoveryResult = self.discovery.discover_dependencies()
        graph: DependencyGraph = discovery_result.graph

        node_lookup: Dict[str, DependencyGraphNode] = {n.id: n for n in graph.nodes}

        mapped_components: List[ComponentMapping] = []
        unresolved_items: List[UnresolvedMapping] = []
        direct_resources: List[Tuple[ComponentMapping, DependencyGraphNode]] = []

        # Extract list of all discovered resources for mapper
        all_resources = self.discovery.resource_discovery.discover_all()

        # 2. Map Changed Files to AWS Resources
        for fc in change_input.files_changed:
            c_mapping = self.mapper.map_file_to_resource(fc.path, all_resources)
            if c_mapping.status == "mapped" and c_mapping.resource_id:
                mapped_components.append(c_mapping)
                # Find graph node or create dummy if missing from graph
                node = node_lookup.get(c_mapping.resource_id)
                if not node:
                    node = DependencyGraphNode(
                        id=c_mapping.resource_id,
                        type=c_mapping.resource_type or ResourceType.LAMBDA,
                        name=c_mapping.component_name or "unknown",
                        arn=c_mapping.resource_id,
                    )
                direct_resources.append((c_mapping, node))
            else:
                unresolved = UnresolvedMapping(
                    file_path=fc.path,
                    status="unknown",
                    reason=c_mapping.reason or "No application component mapping available.",
                )
                unresolved_items.append(unresolved)

        # 3. Traverse Dependency Graph for Direct, Downstream, and Upstream Impacts
        impacted_map: Dict[str, ImpactedResource] = {}
        impact_paths: List[ImpactPath] = []
        visited_edges: Set[Tuple[str, str, str]] = set()

        # Process Direct Impacts
        for c_mapping, node in direct_resources:
            if node.id not in impacted_map:
                metrics = self._get_telemetry_metrics_for_type(node.type)
                impacted_map[node.id] = ImpactedResource(
                    resource_id=node.id,
                    resource_type=node.type,
                    resource_name=node.name,
                    impact=ImpactType.DIRECT,
                    confidence=c_mapping.confidence,
                    evidence=[
                        {
                            "type": c_mapping.evidence_type.value,
                            "source": "file_mapping",
                            "file": c_mapping.file_path,
                        }
                    ],
                    telemetry_metrics=metrics,
                )

            # Traverse Downstream Dependencies (outgoing edges: source -> target)
            self._traverse_downstream(
                current_node=node,
                graph=graph,
                impacted_map=impacted_map,
                impact_paths=impact_paths,
                visited_edges=visited_edges,
                visited_nodes={node.id},
            )

            # Traverse Upstream Dependencies (incoming edges: source -> target where target == current_node)
            self._traverse_upstream(
                current_node=node,
                graph=graph,
                impacted_map=impacted_map,
                impact_paths=impact_paths,
                visited_edges=visited_edges,
                visited_nodes={node.id},
            )

        # 4. Generate Historical Telemetry References
        telemetry_refs: List[ResourceTelemetryReference] = []
        for res in impacted_map.values():
            namespace, metrics = RESOURCE_TELEMETRY_MAP.get(res.resource_type, ("AWS/Custom", []))
            ref = ResourceTelemetryReference(
                resource_id=res.resource_id,
                resource_type=res.resource_type,
                historical_metrics=metrics,
                namespace=namespace,
            )
            telemetry_refs.append(ref)

        # 5. Determine Overall Status
        if not mapped_components and unresolved_items:
            overall_status = "unmapped"
        elif unresolved_items:
            overall_status = "partially_mapped"
        else:
            overall_status = "completed"

        file_path_list = [fc.path for fc in change_input.files_changed]

        return ChangeImpactEvidence(
            change_id=change_input.change_id,
            status=overall_status,
            change=change_input,
            changed_files=file_path_list,
            mapped_components=mapped_components,
            impacted_resources=list(impacted_map.values()),
            impact_paths=impact_paths,
            telemetry_references=telemetry_refs,
            unresolved_items=unresolved_items,
        )

    def _traverse_downstream(
        self,
        current_node: DependencyGraphNode,
        graph: DependencyGraph,
        impacted_map: Dict[str, ImpactedResource],
        impact_paths: List[ImpactPath],
        visited_edges: Set[Tuple[str, str, str]],
        visited_nodes: Set[str],
    ) -> None:
        """Traverse outgoing edges to find downstream dependencies (e.g. Lambda -> DynamoDB)."""
        node_lookup = {n.id: n for n in graph.nodes}

        for edge in graph.edges:
            if edge.source == current_node.id:
                edge_key = (edge.source, edge.target, edge.relationship.value)
                if edge_key in visited_edges:
                    continue
                visited_edges.add(edge_key)

                target_node = node_lookup.get(edge.target)
                if not target_node:
                    target_name = edge.target.split(":")[-1]
                    target_node = DependencyGraphNode(
                        id=edge.target,
                        type=ResourceType.DYNAMODB if "dynamodb" in edge.target.lower() else ResourceType.LAMBDA,
                        name=target_name,
                        arn=edge.target,
                    )

                # Add target node as DOWNSTREAM impacted resource if not direct
                if target_node.id not in impacted_map:
                    metrics = self._get_telemetry_metrics_for_type(target_node.type)
                    impacted_map[target_node.id] = ImpactedResource(
                        resource_id=target_node.id,
                        resource_type=target_node.type,
                        resource_name=target_node.name,
                        impact=ImpactType.DOWNSTREAM,
                        confidence=edge.confidence,
                        evidence=[
                            {
                                "type": edge.evidence.value,
                                "source": "dependency_graph",
                                "relationship": edge.relationship.value,
                            }
                        ],
                        telemetry_metrics=metrics,
                    )

                # Record ImpactPath
                path_step_src = ImpactPathStep(
                    resource_id=current_node.id,
                    resource_type=current_node.type,
                    relationship=edge.relationship,
                    impact_type=ImpactType.DIRECT if current_node.id in impacted_map and impacted_map[current_node.id].impact == ImpactType.DIRECT else ImpactType.DOWNSTREAM,
                )
                path_step_tgt = ImpactPathStep(
                    resource_id=target_node.id,
                    resource_type=target_node.type,
                    relationship=edge.relationship,
                    impact_type=ImpactType.DOWNSTREAM,
                )

                impact_paths.append(
                    ImpactPath(
                        source_resource_id=current_node.id,
                        target_resource_id=target_node.id,
                        path=[path_step_src, path_step_tgt],
                        relationship=edge.relationship,
                        evidence=edge.evidence,
                        confidence=edge.confidence,
                    )
                )

                # Recurse downstream if not visited to prevent cycles
                if target_node.id not in visited_nodes:
                    visited_nodes.add(target_node.id)
                    self._traverse_downstream(
                        current_node=target_node,
                        graph=graph,
                        impacted_map=impacted_map,
                        impact_paths=impact_paths,
                        visited_edges=visited_edges,
                        visited_nodes=visited_nodes,
                    )

    def _traverse_upstream(
        self,
        current_node: DependencyGraphNode,
        graph: DependencyGraph,
        impacted_map: Dict[str, ImpactedResource],
        impact_paths: List[ImpactPath],
        visited_edges: Set[Tuple[str, str, str]],
        visited_nodes: Set[str],
    ) -> None:
        """Traverse incoming edges to find upstream dependencies (e.g. API Gateway -> Lambda)."""
        node_lookup = {n.id: n for n in graph.nodes}

        for edge in graph.edges:
            if edge.target == current_node.id:
                edge_key = (edge.source, edge.target, edge.relationship.value)
                if edge_key in visited_edges:
                    continue
                visited_edges.add(edge_key)

                source_node = node_lookup.get(edge.source)
                if not source_node:
                    src_name = edge.source.split(":")[-1]
                    source_node = DependencyGraphNode(
                        id=edge.source,
                        type=ResourceType.API_GATEWAY if "apigateway" in edge.source.lower() else ResourceType.LAMBDA,
                        name=src_name,
                        arn=edge.source,
                    )

                # Add source node as UPSTREAM impacted resource if not direct
                if source_node.id not in impacted_map:
                    metrics = self._get_telemetry_metrics_for_type(source_node.type)
                    impacted_map[source_node.id] = ImpactedResource(
                        resource_id=source_node.id,
                        resource_type=source_node.type,
                        resource_name=source_node.name,
                        impact=ImpactType.UPSTREAM,
                        confidence=edge.confidence,
                        evidence=[
                            {
                                "type": edge.evidence.value,
                                "source": "dependency_graph",
                                "relationship": edge.relationship.value,
                            }
                        ],
                        telemetry_metrics=metrics,
                    )

                # Record ImpactPath
                path_step_src = ImpactPathStep(
                    resource_id=source_node.id,
                    resource_type=source_node.type,
                    relationship=edge.relationship,
                    impact_type=ImpactType.UPSTREAM,
                )
                path_step_tgt = ImpactPathStep(
                    resource_id=current_node.id,
                    resource_type=current_node.type,
                    relationship=edge.relationship,
                    impact_type=ImpactType.DIRECT if current_node.id in impacted_map and impacted_map[current_node.id].impact == ImpactType.DIRECT else ImpactType.UPSTREAM,
                )

                impact_paths.append(
                    ImpactPath(
                        source_resource_id=source_node.id,
                        target_resource_id=current_node.id,
                        path=[path_step_src, path_step_tgt],
                        relationship=edge.relationship,
                        evidence=edge.evidence,
                        confidence=edge.confidence,
                    )
                )

                # Recurse upstream if not visited to prevent cycles
                if source_node.id not in visited_nodes:
                    visited_nodes.add(source_node.id)
                    self._traverse_upstream(
                        current_node=source_node,
                        graph=graph,
                        impacted_map=impacted_map,
                        impact_paths=impact_paths,
                        visited_edges=visited_edges,
                        visited_nodes=visited_nodes,
                    )

    def _get_telemetry_metrics_for_type(self, resource_type: ResourceType) -> List[str]:
        """Return standard historical CloudWatch metrics list for resource type."""
        _, metrics = RESOURCE_TELEMETRY_MAP.get(resource_type, ("AWS/Custom", []))
        return metrics
