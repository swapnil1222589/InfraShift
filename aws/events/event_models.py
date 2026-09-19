"""
Pydantic schemas for deployment events, lifecycle statuses, environments, deployed resources, and deployment snapshots.
Establishes the deployment evidence anchor for post-deployment CloudWatch telemetry collection.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict

from aws.models.aws_models import ResourceType


class DeploymentStatus(str, Enum):
    """Lifecycle status of an infrastructure deployment."""

    PENDING = "pending"
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


class DeploymentEnvironment(str, Enum):
    """Target deployment environment classification."""

    SANDBOX = "sandbox"
    STAGING = "staging"
    PRODUCTION = "production"
    UNKNOWN = "unknown"


class DeployedResource(BaseModel):
    """Representation of an AWS resource associated with a deployment."""

    model_config = ConfigDict(extra="ignore")

    resource_id: str = Field(description="ARN or ID of deployed AWS resource")
    resource_type: ResourceType
    region: str = Field(default="us-east-1")
    deployment_relationship: Optional[str] = Field(default="deployed")


class DeploymentEvent(BaseModel):
    """
    Normalized deployment event received from deployment pipelines, AWS EventBridge, or CI/CD.
    """

    model_config = ConfigDict(extra="ignore")

    event_id: str = Field(description="Unique event ID for deduplication")
    deployment_id: str = Field(description="Unique deployment identifier")
    change_id: Optional[str] = Field(default=None, description="Associated code change or PR ID")
    commit_sha: Optional[str] = Field(default=None, description="Associated Git commit SHA")
    environment: DeploymentEnvironment = Field(default=DeploymentEnvironment.SANDBOX)
    status: DeploymentStatus = Field(default=DeploymentStatus.PENDING)
    started_at: Optional[str] = Field(
        default=None,
        description="ISO 8601 UTC timestamp when deployment started (null if unavailable)",
    )
    completed_at: Optional[str] = Field(
        default=None,
        description="ISO 8601 UTC timestamp when deployment completed (null if unavailable)",
    )
    region: str = Field(default="us-east-1")
    resources: List[DeployedResource] = Field(default_factory=list)
    raw_payload: Dict[str, Any] = Field(default_factory=dict)


class DeploymentSnapshot(BaseModel):
    """
    Normalized deployment snapshot anchoring post-deployment telemetry and verification.
    """

    model_config = ConfigDict(extra="ignore")

    snapshot_id: str
    deployment_id: str
    change_id: Optional[str] = None
    commit_sha: Optional[str] = None
    environment: DeploymentEnvironment
    status: DeploymentStatus
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    resources: List[DeployedResource] = Field(default_factory=list)
    telemetry_anchor_timestamp: Optional[str] = Field(
        default=None,
        description="ISO 8601 UTC timestamp of deployment completion used to anchor CloudWatch retrieval",
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp when snapshot was generated",
    )
