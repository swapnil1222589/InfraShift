"""
Pydantic schemas for code change input, component mapping, impact analysis, and evidence packages.
Provides the handoff data structures between Infrastructure Evidence and AI Forecasting layers.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict

from aws.models.aws_models import (
    ResourceType,
    EvidenceType,
    ConfidenceLevel,
    RelationshipType,
)


class ImpactType(str, Enum):
    """Classification of impact on an AWS resource."""

    DIRECT = "direct"
    DOWNSTREAM = "downstream"
    UPSTREAM = "upstream"
    UNKNOWN = "unknown"


class FileChangeStatus(str, Enum):
    """Git status of a changed file."""

    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"


class FileChange(BaseModel):
    """Details of a single file modified in a code change."""

    model_config = ConfigDict(extra="ignore")

    path: str = Field(description="Relative file path in repository (e.g. src/orders/service.py)")
    status: FileChangeStatus = Field(default=FileChangeStatus.MODIFIED)
    additions: Optional[int] = Field(default=0)
    deletions: Optional[int] = Field(default=0)


class CodeChangeInput(BaseModel):
    """
    Normalized code change input representation (commits, PRs, file lists).
    """

    model_config = ConfigDict(extra="ignore")

    change_id: str = Field(description="Unique identifier for code change e.g. PR-102 or commit SHA")
    commit_sha: Optional[str] = None
    base_sha: Optional[str] = None
    repository: Optional[str] = None
    author: Optional[str] = None
    files_changed: List[FileChange] = Field(default_factory=list)


class ComponentMapping(BaseModel):
    """
    Mapping between a changed source file, an application component, and a discovered AWS resource.
    """

    model_config = ConfigDict(extra="ignore")

    file_path: str
    component_name: Optional[str] = None
    resource_id: Optional[str] = None
    resource_type: Optional[ResourceType] = None
    evidence_type: EvidenceType = Field(default=EvidenceType.UNKNOWN)
    confidence: ConfidenceLevel = Field(default=ConfidenceLevel.UNAVAILABLE)
    status: str = Field(default="mapped", description="'mapped' or 'unknown'")
    reason: Optional[str] = None


class ImpactedResource(BaseModel):
    """
    An AWS resource identified as affected by a code change.
    """

    model_config = ConfigDict(extra="ignore")

    resource_id: str = Field(description="ARN or ID of impacted AWS resource")
    resource_type: ResourceType
    resource_name: str
    impact: ImpactType
    confidence: ConfidenceLevel
    evidence: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Evidence trace (e.g. deployment_metadata, dependency_graph, xray)",
    )
    telemetry_metrics: List[str] = Field(
        default_factory=list,
        description="Available CloudWatch metric names for this resource",
    )


class ImpactPathStep(BaseModel):
    """Single step in an impact dependency path."""

    model_config = ConfigDict(extra="ignore")

    resource_id: str
    resource_type: ResourceType
    relationship: RelationshipType
    impact_type: ImpactType


class ImpactPath(BaseModel):
    """
    Explicit dependency traversal path connecting a directly changed resource to affected resources.
    """

    model_config = ConfigDict(extra="ignore")

    source_resource_id: str
    target_resource_id: str
    path: List[ImpactPathStep] = Field(default_factory=list)
    relationship: RelationshipType
    evidence: EvidenceType
    confidence: ConfidenceLevel


class ResourceTelemetryReference(BaseModel):
    """
    Reference to historical CloudWatch telemetry metrics available for an impacted resource.
    """

    model_config = ConfigDict(extra="ignore")

    resource_id: str
    resource_type: ResourceType
    historical_metrics: List[str] = Field(default_factory=list)
    namespace: str


class UnresolvedMapping(BaseModel):
    """
    Record of a changed file that could not be mapped to an AWS resource.
    """

    model_config = ConfigDict(extra="ignore")

    file_path: str
    status: str = "unknown"
    reason: str = "No application component mapping available."


class ChangeImpactEvidence(BaseModel):
    """
    Unified, reusable impact evidence package produced by the Infrastructure layer.
    Serves as the explicit handoff boundary for AI / Forecasting analysis.
    """

    model_config = ConfigDict(extra="ignore")

    change_id: str
    status: str = Field(default="completed", description="'completed', 'partially_mapped', 'unmapped'")
    change: CodeChangeInput
    changed_files: List[str] = Field(default_factory=list)
    mapped_components: List[ComponentMapping] = Field(default_factory=list)
    impacted_resources: List[ImpactedResource] = Field(default_factory=list)
    impact_paths: List[ImpactPath] = Field(default_factory=list)
    telemetry_references: List[ResourceTelemetryReference] = Field(default_factory=list)
    unresolved_items: List[UnresolvedMapping] = Field(default_factory=list)
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp of impact analysis execution",
    )
