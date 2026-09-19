"""
AWS Evidence Integration Orchestrator.
Assembles the complete end-to-end evidence package connecting code changes, AWS resource impact,
deployment tracking, CloudWatch telemetry windows, and forecast-vs-actual comparisons.
Strictly read-only, non-causal evidence pipeline.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Union, Any

from aws.models.aws_models import (
    ResourceType,
    EvidenceType,
    ConfidenceLevel,
)
from aws.impact.code_change_models import (
    CodeChangeInput,
    ChangeImpactEvidence,
    ImpactedResource,
)
from aws.impact.impact_mapping import ImpactMappingService
from aws.events.event_models import DeploymentSnapshot
from aws.events.deployment_tracking import DeploymentTrackingService
from aws.telemetry.telemetry_loop import TelemetryLoopService, TelemetryWindow
from aws.telemetry.forecast_comparison import (
    ForecastVsActualService,
    ResourceForecastInput,
    DeploymentForecastVsActualResult,
)
from aws.integration.evidence_models import (
    AWSEvidencePackage,
    ResourceTraceability,
)

logger = logging.getLogger("infrashift.aws.integration.service")


class AWSEvidenceIntegrationService:
    """
    Bounded orchestration service for assembling unified AWS Evidence Packages.
    Connects Phase 1-6 evidence modules into a single traceable pipeline for Person 1 & Person 3.
    """

    def __init__(
        self,
        impact_mapping_service: Optional[ImpactMappingService] = None,
        deployment_service: Optional[DeploymentTrackingService] = None,
        telemetry_loop_service: Optional[TelemetryLoopService] = None,
        forecast_comparison_service: Optional[ForecastVsActualService] = None,
    ):
        self.impact_service = impact_mapping_service or ImpactMappingService()
        self.deployment_service = deployment_service or DeploymentTrackingService()
        self.loop_service = telemetry_loop_service or TelemetryLoopService()
        self.comparison_service = forecast_comparison_service or ForecastVsActualService(
            loop_service=self.loop_service
        )

    def assemble_evidence_package(
        self,
        change_impact: ChangeImpactEvidence,
        snapshot: DeploymentSnapshot,
        forecasts: Optional[List[ResourceForecastInput]] = None,
        baseline_window_minutes: int = 60,
        post_window_minutes: int = 60,
        period_seconds: int = 300,
    ) -> AWSEvidencePackage:
        """
        Assemble a unified AWSEvidencePackage given change impact evidence and a deployment snapshot.

        :param change_impact: ChangeImpactEvidence object from Phase 4 impact mapping.
        :param snapshot: DeploymentSnapshot object from Phase 5 deployment tracking.
        :param forecasts: Optional external predictions provided by Person 1's AI forecasting layer.
        :param baseline_window_minutes: Duration of pre-deployment baseline window in minutes.
        :param post_window_minutes: Duration of post-deployment observation window in minutes.
        :param period_seconds: CloudWatch metric period in seconds.
        :return: AWSEvidencePackage object.
        """
        anchor_ts = snapshot.telemetry_anchor_timestamp or snapshot.completed_at
        logger.info(
            "Assembling AWS evidence package for change '%s', deployment '%s' (anchor: %s)",
            change_impact.change_id,
            snapshot.deployment_id,
            anchor_ts,
        )

        baseline_windows: List[TelemetryWindow] = []
        post_windows: List[TelemetryWindow] = []
        traceability_list: List[ResourceTraceability] = []

        # 1. Process Telemetry Windows for each impacted resource in snapshot
        if anchor_ts:
            for res in snapshot.resources:
                res_name = self._extract_resource_name(res.resource_id)
                metrics = self._get_metrics_for_type(res.resource_type)
                namespace = self._get_namespace_for_type(res.resource_type)

                res_baseline_status = "no_data"
                res_post_status = "no_data"

                for metric_name in metrics:
                    # Pre-deployment baseline window
                    base_win = self.loop_service.get_pre_deployment_baseline(
                        resource_id=res.resource_id,
                        resource_type=res.resource_type,
                        resource_name=res_name,
                        metric_name=metric_name,
                        namespace=namespace,
                        completed_at=anchor_ts,
                        baseline_window_minutes=baseline_window_minutes,
                        period_seconds=period_seconds,
                    )
                    baseline_windows.append(base_win)
                    if base_win.status == "usable":
                        res_baseline_status = "usable"

                    # Post-deployment actual window
                    post_win = self.loop_service.get_post_deployment_telemetry(
                        resource_id=res.resource_id,
                        resource_type=res.resource_type,
                        resource_name=res_name,
                        metric_name=metric_name,
                        namespace=namespace,
                        completed_at=anchor_ts,
                        post_window_minutes=post_window_minutes,
                        period_seconds=period_seconds,
                    )
                    post_windows.append(post_win)
                    if post_win.status == "usable":
                        res_post_status = "usable"

                # Match resource impact classification & evidence provenance
                impact_class = self._find_impact_classification(res.resource_id, change_impact)
                discovery_ev, discovery_conf = self._find_discovery_provenance(res.resource_id, change_impact)
                dep_ev, dep_conf = self._find_dependency_provenance(res.resource_id, change_impact)

                forecast_comp_status = "usable" if forecasts else "not_provided"

                traceability_list.append(
                    ResourceTraceability(
                        resource_id=res.resource_id,
                        resource_type=res.resource_type,
                        resource_name=res_name,
                        impact_classification=impact_class,
                        discovery_evidence=discovery_ev,
                        discovery_confidence=discovery_conf,
                        dependency_evidence=dep_ev,
                        dependency_confidence=dep_conf,
                        baseline_telemetry_status=res_baseline_status,
                        post_telemetry_status=res_post_status,
                        forecast_comparison_status=forecast_comp_status,
                    )
                )

        # 2. Run Forecast vs Actual Comparison (Pass-through external forecast without modification)
        comparison_result: Optional[DeploymentForecastVsActualResult] = None
        forecast_status = "not_provided"

        if forecasts:
            comparison_result = self.comparison_service.compare_deployment_telemetry(
                snapshot=snapshot,
                forecasts=forecasts,
                baseline_window_minutes=baseline_window_minutes,
                post_window_minutes=post_window_minutes,
                period_seconds=period_seconds,
            )
            forecast_status = "provided"

        # 3. Overall Package Status Determination
        package_status = "usable"
        if not anchor_ts:
            package_status = "no_deployment_anchor"
        elif any(w.status == "no_data" for w in post_windows) and not any(w.status == "usable" for w in post_windows):
            package_status = "no_actual_data"
        elif change_impact.status == "partially_mapped":
            package_status = "partially_mapped"

        return AWSEvidencePackage(
            change_id=change_impact.change_id,
            commit_sha=change_impact.change.commit_sha,
            deployment_id=snapshot.deployment_id,
            environment=snapshot.environment.value,
            deployment_status=snapshot.status.value,
            telemetry_anchor_timestamp=anchor_ts,
            change_impact=change_impact,
            impacted_resources=change_impact.impacted_resources,
            dependency_paths=change_impact.impact_paths,
            unresolved_items=change_impact.unresolved_items,
            baseline_observations=baseline_windows,
            post_deployment_observations=post_windows,
            forecast_comparisons=comparison_result,
            forecast_status=forecast_status,
            traceability=traceability_list,
            evidence_references={
                "snapshot_resource_count": len(snapshot.resources),
                "impacted_resource_count": len(change_impact.impacted_resources),
                "unresolved_count": len(change_impact.unresolved_items),
                "baseline_window_minutes": baseline_window_minutes,
                "post_window_minutes": post_window_minutes,
            },
            status=package_status,
            read_only_verified=True,
        )

    def analyze_and_assemble(
        self,
        change_input: CodeChangeInput,
        deployment_id: str,
        forecasts: Optional[List[ResourceForecastInput]] = None,
        baseline_window_minutes: int = 60,
        post_window_minutes: int = 60,
        period_seconds: int = 300,
    ) -> AWSEvidencePackage:
        """
        Convenience entrypoint for Person 3's backend API layer.
        Performs change impact analysis, looks up deployment snapshot, and returns AWSEvidencePackage.

        :param change_input: CodeChangeInput describing modified files and change ID.
        :param deployment_id: Active deployment tracking ID.
        :param forecasts: Optional forecasts supplied by Person 1.
        :return: AWSEvidencePackage object.
        """
        # 1. Analyze Code Change Impact
        impact_evidence = self.impact_service.analyze_change_impact(change_input)

        # 2. Lookup Deployment Snapshot
        snapshot = self.deployment_service.get_deployment_snapshot(deployment_id)
        if not snapshot:
            raise ValueError(f"Deployment with ID '{deployment_id}' not found in deployment repository.")

        # 3. Assemble Final Evidence Package
        return self.assemble_evidence_package(
            change_impact=impact_evidence,
            snapshot=snapshot,
            forecasts=forecasts,
            baseline_window_minutes=baseline_window_minutes,
            post_window_minutes=post_window_minutes,
            period_seconds=period_seconds,
        )

    def _extract_resource_name(self, resource_id: str) -> str:
        """Extract resource name from ARN or ID."""
        if ":" in resource_id or "/" in resource_id:
            parts = resource_id.replace("/", ":").split(":")
            return parts[-1]
        return resource_id

    def _get_metrics_for_type(self, resource_type: ResourceType) -> List[str]:
        """Get standard CloudWatch metric names for resource type."""
        if resource_type == ResourceType.LAMBDA:
            return ["Invocations", "Duration", "Errors", "Throttles"]
        elif resource_type == ResourceType.DYNAMODB:
            return [
                "ConsumedReadCapacityUnits",
                "ConsumedWriteCapacityUnits",
                "ReadThrottleEvents",
                "WriteThrottleEvents",
            ]
        elif resource_type == ResourceType.API_GATEWAY:
            return ["Count", "Latency", "4XXError", "5XXError"]
        return ["Invocations"]

    def _get_namespace_for_type(self, resource_type: ResourceType) -> str:
        """Get CloudWatch namespace for resource type."""
        if resource_type == ResourceType.LAMBDA:
            return "AWS/Lambda"
        elif resource_type == ResourceType.DYNAMODB:
            return "AWS/DynamoDB"
        elif resource_type == ResourceType.API_GATEWAY:
            return "AWS/ApiGateway"
        return "AWS/Custom"

    def _find_impact_classification(
        self, resource_id: str, change_impact: ChangeImpactEvidence
    ) -> str:
        """Find impact type ('direct', 'downstream', 'upstream', 'unknown') for a resource."""
        for imp in change_impact.impacted_resources:
            if imp.resource_id == resource_id:
                return imp.impact.value
        return "unknown"

    def _find_discovery_provenance(
        self, resource_id: str, change_impact: ChangeImpactEvidence
    ) -> Tuple[EvidenceType, ConfidenceLevel]:
        """Find discovery evidence type and confidence for a resource."""
        for imp in change_impact.impacted_resources:
            if imp.resource_id == resource_id:
                for ev in imp.evidence:
                    if "evidence_type" in ev:
                        return (
                            EvidenceType(ev["evidence_type"]),
                            ConfidenceLevel(ev.get("confidence", "observed")),
                        )
                return EvidenceType.AWS_CONFIGURATION, imp.confidence
        return EvidenceType.UNKNOWN, ConfidenceLevel.UNAVAILABLE

    def _find_dependency_provenance(
        self, resource_id: str, change_impact: ChangeImpactEvidence
    ) -> Tuple[EvidenceType, ConfidenceLevel]:
        """Find dependency evidence type and confidence from impact paths."""
        for path in change_impact.impact_paths:
            if path.target_resource_id == resource_id or path.source_resource_id == resource_id:
                return path.evidence, path.confidence
        return EvidenceType.UNKNOWN, ConfidenceLevel.UNAVAILABLE
