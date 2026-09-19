"""
AWS Dependency Discovery Orchestrator.
Discovers relationships across API Gateway, Lambda, DynamoDB, and X-Ray traces.
Maintains strict separation between OBSERVED and INFERRED evidence.
Generates normalized dependency graphs and connects to CloudWatch telemetry.
"""

import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple, Union

from aws.config.aws_config import AWSClientFactory, AWSConfig
from aws.models.aws_models import (
    ResourceType,
    NormalizedResource,
    NormalizedDependency,
    EvidenceType,
    ConfidenceLevel,
    RelationshipType,
    DependencyGraph,
    DependencyGraphNode,
    DependencyGraphEdge,
    DependencyDiscoveryResult,
    TelemetrySeries,
)
from aws.discovery.resource_discovery import ResourceDiscovery
from aws.discovery.api_gateway_discovery import APIGatewayDiscovery
from aws.discovery.lambda_discovery import LambdaDiscovery
from aws.discovery.dynamodb_discovery import DynamoDBDiscovery
from aws.tracing.xray import XRayTracing
from aws.telemetry.cloudwatch import CloudWatchTelemetry

logger = logging.getLogger("infrashift.aws.discovery.dependency")


class DependencyDiscovery:
    """Orchestrates AWS dependency and runtime relationship discovery."""

    def __init__(
        self,
        client_factory: Optional[AWSClientFactory] = None,
        config: Optional[AWSConfig] = None,
    ):
        if client_factory:
            self.factory = client_factory
        else:
            self.factory = AWSClientFactory(config=config or AWSConfig())

        self.resource_discovery = ResourceDiscovery(client_factory=self.factory)
        self.api_gateway_discovery = APIGatewayDiscovery(self.factory)
        self.lambda_discovery = LambdaDiscovery(self.factory)
        self.dynamodb_discovery = DynamoDBDiscovery(self.factory)
        self.xray_tracing = XRayTracing(client_factory=self.factory)
        self.telemetry = CloudWatchTelemetry(client_factory=self.factory)

    def discover_dependencies(
        self,
        start_time: Optional[Union[datetime, str]] = None,
        end_time: Optional[Union[datetime, str]] = None,
    ) -> DependencyDiscoveryResult:
        """
        Discover infrastructure and runtime dependencies across AWS API Gateway, Lambda, DynamoDB, and X-Ray.
        Returns a normalized DependencyDiscoveryResult containing graph and evidence status.
        """
        logger.info("Starting AWS dependency discovery in region: %s", self.factory.config.region_name)

        raw_deps: List[NormalizedDependency] = []
        evidence_status = ConfidenceLevel.OBSERVED
        failure_reasons: List[str] = []

        # 1. Discover base resources (Nodes)
        discovered_resources: List[NormalizedResource] = []
        try:
            discovered_resources = self.resource_discovery.discover_all()
        except Exception as e:
            logger.error("Error discovering base resources: %s", e)
            failure_reasons.append(f"Resource discovery error: {e}")

        # 2. Discover API Gateway → Lambda dependencies (OBSERVED via AWS Configuration)
        try:
            apigw_deps = self.api_gateway_discovery.discover_dependencies()
            logger.info("Discovered %d API Gateway → Lambda dependencies.", len(apigw_deps))
            raw_deps.extend(apigw_deps)
        except Exception as e:
            logger.error("Error discovering API Gateway dependencies: %s", e)
            failure_reasons.append(f"API Gateway dependency error: {e}")

        # 3. Discover Lambda → DynamoDB dependencies (OBSERVED via X-Ray traces)
        xray_evidences = []
        try:
            evs, xray_deps = self.xray_tracing.discover_trace_evidence(start_time, end_time)
            xray_evidences = evs
            logger.info("Discovered %d X-Ray trace dependencies.", len(xray_deps))
            raw_deps.extend(xray_deps)
        except Exception as e:
            logger.warning("X-Ray trace discovery encountered error/unavailable state: %s", e)
            failure_reasons.append(f"X-Ray evidence unavailable: {e}")

        # 4. Discover Lambda → DynamoDB dependencies (INFERRED via Lambda Environment Variables)
        try:
            inferred_deps = self.lambda_discovery.discover_inferred_dynamodb_dependencies()
            logger.info("Discovered %d inferred Lambda → DynamoDB dependencies.", len(inferred_deps))
            raw_deps.extend(inferred_deps)
        except Exception as e:
            logger.error("Error discovering inferred Lambda dependencies: %s", e)
            failure_reasons.append(f"Inferred dependency error: {e}")

        # 5. Deduplicate and merge dependencies (prefer OBSERVED over INFERRED)
        merged_deps = self._merge_dependencies(raw_deps)

        # 6. Build Dependency Graph
        graph = self._build_dependency_graph(discovered_resources, merged_deps)

        # Determine overall evidence status
        if not merged_deps and failure_reasons:
            evidence_status = ConfidenceLevel.UNAVAILABLE
            reason = "; ".join(failure_reasons)
        elif not merged_deps:
            evidence_status = ConfidenceLevel.UNAVAILABLE
            reason = "No dependencies found for the target environment/time window."
        elif all(d.confidence == ConfidenceLevel.INFERRED for d in merged_deps):
            evidence_status = ConfidenceLevel.INFERRED
            reason = "Dependencies inferred from configuration metadata only."
        else:
            evidence_status = ConfidenceLevel.OBSERVED
            reason = None

        return DependencyDiscoveryResult(
            dependencies=merged_deps,
            graph=graph,
            evidence_status=evidence_status,
            reason=reason,
        )

    def _merge_dependencies(
        self,
        dependencies: List[NormalizedDependency],
    ) -> List[NormalizedDependency]:
        """
        Deduplicate dependencies based on (source_resource_id, target_resource_id, relationship).
        If both OBSERVED and INFERRED exist for the same key, strictly prefer OBSERVED.
        """
        dep_map: Dict[Tuple[str, str, str], NormalizedDependency] = {}

        for dep in dependencies:
            key = (dep.source_resource_id, dep.target_resource_id, dep.relationship.value)
            if key not in dep_map:
                dep_map[key] = dep
            else:
                existing = dep_map[key]
                # If new dep is OBSERVED and existing is INFERRED, replace it
                if dep.confidence == ConfidenceLevel.OBSERVED and existing.confidence != ConfidenceLevel.OBSERVED:
                    dep_map[key] = dep
                # If both are OBSERVED or both INFERRED, merge metadata
                elif dep.confidence == existing.confidence:
                    existing.metadata.update(dep.metadata)

        return list(dep_map.values())

    def _build_dependency_graph(
        self,
        discovered_resources: List[NormalizedResource],
        dependencies: List[NormalizedDependency],
    ) -> DependencyGraph:
        """Construct normalized DependencyGraph from discovered resources and deduplicated edges."""
        node_map: Dict[str, DependencyGraphNode] = {}

        # Add known discovered resources as nodes
        for res in discovered_resources:
            node_map[res.resource_id] = DependencyGraphNode(
                id=res.resource_id,
                type=res.resource_type,
                name=res.resource_name,
                arn=res.resource_id,
                metadata=res.metadata,
            )

        edges: List[DependencyGraphEdge] = []

        for dep in dependencies:
            # Ensure source node exists
            if dep.source_resource_id not in node_map:
                src_name = self._extract_resource_name(dep.source_resource_id)
                node_map[dep.source_resource_id] = DependencyGraphNode(
                    id=dep.source_resource_id,
                    type=dep.source_type,
                    name=src_name,
                    arn=dep.source_resource_id,
                )

            # Ensure target node exists
            if dep.target_resource_id not in node_map:
                tgt_name = self._extract_resource_name(dep.target_resource_id)
                node_map[dep.target_resource_id] = DependencyGraphNode(
                    id=dep.target_resource_id,
                    type=dep.target_type,
                    name=tgt_name,
                    arn=dep.target_resource_id,
                )

            edge = DependencyGraphEdge(
                source=dep.source_resource_id,
                target=dep.target_resource_id,
                relationship=dep.relationship,
                evidence=dep.evidence_type,
                confidence=dep.confidence,
                metadata=dep.metadata,
            )
            edges.append(edge)

        return DependencyGraph(
            nodes=list(node_map.values()),
            edges=edges,
        )

    def _extract_resource_name(self, resource_id: str) -> str:
        """Extract user-friendly resource name from ARN or ID."""
        if ":" in resource_id or "/" in resource_id:
            parts = resource_id.replace("/", ":").split(":")
            return parts[-1]
        return resource_id

    def get_resource_telemetry(
        self,
        node: DependencyGraphNode,
        metric_name: str,
        start_time: Optional[Union[datetime, str]] = None,
        end_time: Optional[Union[datetime, str]] = None,
    ) -> TelemetrySeries:
        """
        Reuses existing CloudWatchTelemetry service to fetch historical telemetry for a graph node.
        Does NOT duplicate CloudWatch retrieval logic.
        """
        namespace = "AWS/Lambda"
        if node.type == ResourceType.DYNAMODB:
            namespace = "AWS/DynamoDB"
        elif node.type == ResourceType.API_GATEWAY:
            namespace = "AWS/ApiGateway"

        return self.telemetry.get_metric_series(
            resource_id=node.id,
            resource_type=node.type,
            resource_name=node.name,
            metric_name=metric_name,
            namespace=namespace,
            start_time=start_time,
            end_time=end_time,
        )
