"""
Unified AWS Evidence Package and Traceability Models for InfraShift.
Provides the final handoff data structure between Person 2 (AWS/Infrastructure Evidence),
Person 1 (AI / Forecasting Layer), and Person 3 (Backend API Layer).
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict

from aws.models.aws_models import (
    ResourceType,
    EvidenceType,
    ConfidenceLevel,
)
from aws.impact.code_change_models import (
    CodeChangeInput,
    ComponentMapping,
    ImpactedResource,
    ImpactPath,
    ResourceTelemetryReference,
    UnresolvedMapping,
    ChangeImpactEvidence,
)
from aws.events.event_models import DeploymentSnapshot
from aws.telemetry.telemetry_loop import TelemetryWindow
from aws.telemetry.forecast_comparison import DeploymentForecastVsActualResult


class TraceabilityStageStatus(str, Enum):
    """Status of evidence at a specific stage of the pipeline."""

    OBSERVED = "observed"
    INFERRED = "inferred"
    UNAVAILABLE = "unavailable"
    NOT_APPLICABLE = "not_applicable"


class ResourceTraceability(BaseModel):
    """
    Detailed traceability matrix for a single AWS resource across all evidence pipeline stages.
    Answers: "Where did this resource's evidence come from, and how confident are we?"
    """

    model_config = ConfigDict(extra="ignore")

    resource_id: str
    resource_type: ResourceType
    resource_name: str
    impact_classification: str = Field(description="'direct', 'downstream', 'upstream', or 'unknown'")
    discovery_evidence: EvidenceType = Field(default=EvidenceType.AWS_CONFIGURATION)
    discovery_confidence: ConfidenceLevel = Field(default=ConfidenceLevel.OBSERVED)
    dependency_evidence: EvidenceType = Field(default=EvidenceType.UNKNOWN)
    dependency_confidence: ConfidenceLevel = Field(default=ConfidenceLevel.UNAVAILABLE)
    baseline_telemetry_status: str = Field(default="usable", description="'usable', 'no_data', or 'unavailable'")
    post_telemetry_status: str = Field(default="usable", description="'usable', 'no_data', or 'unavailable'")
    forecast_comparison_status: str = Field(
        default="usable",
        description="'usable', 'no_actual_data', 'no_forecast_data', or 'not_provided'",
    )


class AWSEvidencePackage(BaseModel):
    """
    Unified, complete AWS Infrastructure Evidence Package.
    Represents the end-to-end chain:
    Change -> Impacted Resources -> Deployment -> Telemetry Anchor -> Baseline -> Actual -> Forecast Comparison.
    Handoff object for Person 1 (AI Forecasting) and Person 3 (Backend API).
    """

    model_config = ConfigDict(extra="ignore")

    change_id: str = Field(description="Unique code change identifier e.g. PR-102")
    commit_sha: Optional[str] = Field(default=None, description="Git commit SHA if available")
    deployment_id: str = Field(description="Deployment tracking ID")
    environment: str = Field(description="Target environment e.g. sandbox, staging, production")
    deployment_status: str = Field(description="Deployment lifecycle status e.g. completed, failed")
    telemetry_anchor_timestamp: Optional[str] = Field(
        default=None,
        description="ISO 8601 UTC timestamp anchor for pre/post telemetry window calculation",
    )

    # Change & Impact Evidence
    change_impact: ChangeImpactEvidence = Field(description="Full code-change impact evidence")
    impacted_resources: List[ImpactedResource] = Field(default_factory=list)
    dependency_paths: List[ImpactPath] = Field(default_factory=list)
    unresolved_items: List[UnresolvedMapping] = Field(default_factory=list)

    # Historical Baseline & Post-Deployment Telemetry Windows
    baseline_observations: List[TelemetryWindow] = Field(
        default_factory=list,
        description="Pre-deployment CloudWatch baseline telemetry windows",
    )
    post_deployment_observations: List[TelemetryWindow] = Field(
        default_factory=list,
        description="Post-deployment CloudWatch actual telemetry windows",
    )

    # Forecast Comparison Results (if forecast was supplied by Person 1)
    forecast_comparisons: Optional[DeploymentForecastVsActualResult] = Field(
        default=None,
        description="Forecast vs actual comparison report from ForecastVsActualService",
    )
    forecast_status: str = Field(
        default="not_provided",
        description="'provided', 'not_provided', 'no_actual_data', or 'error'",
    )

    # Evidence Traceability & Metadata
    traceability: List[ResourceTraceability] = Field(
        default_factory=list,
        description="Per-resource evidence provenance and confidence matrix",
    )
    evidence_references: Dict[str, Any] = Field(
        default_factory=dict,
        description="References to underlying raw evidence (e.g. X-Ray trace IDs, CloudWatch metric query metadata)",
    )
    status: str = Field(
        default="usable",
        description="Overall evidence package status e.g. 'usable', 'no_actual_data', 'partially_mapped'",
    )
    read_only_verified: bool = Field(
        default=True,
        description="Guarantees zero mutating AWS API calls were performed",
    )
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp of evidence package assembly",
    )
