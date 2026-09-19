"""
Pydantic schemas for normalized AWS resources and CloudWatch telemetry series.
Ensures observed cloud data is explicitly separated from AI-inferred metrics.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class ResourceType(str, Enum):
    LAMBDA = "lambda"
    DYNAMODB = "dynamodb"
    API_GATEWAY = "api_gateway"


class LambdaMetadata(BaseModel):
    """Specific metadata for AWS Lambda functions."""

    model_config = ConfigDict(extra="ignore")

    function_arn: str
    function_name: str
    runtime: Optional[str] = None
    memory_mb: Optional[int] = Field(default=None, description="Memory in MB")
    timeout_seconds: Optional[int] = Field(default=None, description="Timeout in seconds")
    handler: Optional[str] = None
    code_size_bytes: Optional[int] = None
    last_modified: Optional[str] = None
    environment_keys: List[str] = Field(
        default_factory=list,
        description="Keys of environment variables present (values omitted/redacted for security)",
    )
    role_arn: Optional[str] = None
    architectures: List[str] = Field(default_factory=list)


class DynamoDBMetadata(BaseModel):
    """Specific metadata for AWS DynamoDB tables."""

    model_config = ConfigDict(extra="ignore")

    table_arn: str
    table_name: str
    table_status: str
    billing_mode: Optional[str] = "PROVISIONED"
    read_capacity_units: Optional[int] = None
    write_capacity_units: Optional[int] = None
    item_count: Optional[int] = None
    table_size_bytes: Optional[int] = None
    creation_date_time: Optional[str] = None
    partition_key: Optional[str] = None
    sort_key: Optional[str] = None
    global_secondary_indexes_count: int = 0
    local_secondary_indexes_count: int = 0


class APIGatewayMetadata(BaseModel):
    """Specific metadata for AWS API Gateway APIs."""

    model_config = ConfigDict(extra="ignore")

    api_id: str
    api_name: str
    api_type: str = Field(description="REST (v1) or HTTP/WEBSOCKET (v2)")
    protocol_type: Optional[str] = "HTTP"
    stages: List[str] = Field(default_factory=list)
    endpoint_types: List[str] = Field(default_factory=list)
    routes_or_resources: List[str] = Field(
        default_factory=list,
        description="List of paths/routes defined on the API",
    )
    endpoint_url: Optional[str] = None
    created_date: Optional[str] = None


class NormalizedResource(BaseModel):
    """
    Standardized internal representation of an AWS Infrastructure resource.
    """

    model_config = ConfigDict(extra="ignore")

    resource_id: str = Field(description="Canonical ARN or unique identifier")
    resource_type: ResourceType
    resource_name: str
    region: str
    account_id: Optional[str] = None
    tags: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Service-specific metadata dict (e.g. LambdaMetadata, DynamoDBMetadata)",
    )
    observed_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp when resource discovery was executed",
    )
    is_inferred: bool = Field(
        default=False,
        description="False for observed AWS API telemetry/config; True for downstream AI predictions",
    )


class Datapoint(BaseModel):
    """Single CloudWatch metric measurement point."""

    model_config = ConfigDict(extra="ignore")

    timestamp: str = Field(description="ISO 8601 timestamp of data point")
    value: float = Field(description="Observed numeric value")
    unit: Optional[str] = Field(default=None, description="CloudWatch unit (Count, Seconds, Bytes, etc.)")


class TelemetrySeries(BaseModel):
    """
    Normalized CloudWatch telemetry metric time series.
    """

    model_config = ConfigDict(extra="ignore")

    resource_id: str
    metric_name: str
    namespace: str
    statistic: str
    start_time: str
    end_time: str
    period_seconds: int
    datapoints: List[Datapoint] = Field(
        default_factory=list,
        description="List of observed telemetry datapoints. Empty list [] if AWS has no data.",
    )
    is_inferred: bool = Field(
        default=False,
        description="Always False for real AWS CloudWatch telemetry",
    )


class CloudWatchMetricQuery(BaseModel):
    """Query parameter model for requesting telemetry."""

    model_config = ConfigDict(extra="ignore")

    resource_id: str
    metric_name: str
    namespace: str
    statistic: str = "Sum"  # Sum, Average, Maximum, Minimum, SampleCount
    period_seconds: int = 300
    start_time: str
    end_time: str
    unit: Optional[str] = None


class EvidenceType(str, Enum):
    """Source of dependency evidence."""
    AWS_CONFIGURATION = "aws_configuration"
    XRAY = "xray"
    APPLICATION_METADATA = "application_metadata"
    INFERRED = "inferred"
    UNKNOWN = "unknown"


class ConfidenceLevel(str, Enum):
    """Confidence status of a discovered relationship or telemetry evidence."""
    OBSERVED = "observed"
    INFERRED = "inferred"
    UNAVAILABLE = "unavailable"


class RelationshipType(str, Enum):
    """Relationship classification between AWS resources."""
    ROUTES_TO = "routes_to"
    ACCESSES = "accesses"
    INVOKES = "invokes"
    DEPENDS_ON = "depends_on"


class NormalizedDependency(BaseModel):
    """
    Typed normalized dependency representation between AWS resources.
    """

    model_config = ConfigDict(extra="ignore")

    source_resource_id: str = Field(description="ARN or ID of source resource")
    source_type: ResourceType = Field(description="ResourceType of source resource")
    target_resource_id: str = Field(description="ARN or ID of target resource")
    target_type: ResourceType = Field(description="ResourceType of target resource")
    relationship: RelationshipType = Field(description="Type of relationship (routes_to, accesses, etc.)")
    evidence_type: EvidenceType = Field(description="Origin of relationship evidence")
    confidence: ConfidenceLevel = Field(description="Observed vs Inferred classification")
    observed_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp of observation",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context (e.g. route path, trace_id, duration_ms, error status)",
    )


class XRayTraceEvidence(BaseModel):
    """
    Normalized structure representing X-Ray trace evidence between resources.
    """

    model_config = ConfigDict(extra="ignore")

    trace_id: str
    timestamp: str = Field(description="ISO 8601 timestamp of trace")
    source: Dict[str, Any] = Field(description="Source dict e.g. {'type': 'lambda', 'resource_id': '...'}")
    target: Dict[str, Any] = Field(description="Target dict e.g. {'type': 'dynamodb', 'resource_id': '...'}")
    duration_ms: Optional[float] = Field(default=None, description="Segment execution duration in ms")
    error: bool = Field(default=False, description="True if 4xx error recorded")
    fault: bool = Field(default=False, description="True if 5xx fault recorded")
    evidence_type: EvidenceType = Field(default=EvidenceType.XRAY)
    confidence: ConfidenceLevel = Field(default=ConfidenceLevel.OBSERVED)


class DependencyGraphNode(BaseModel):
    """Node in the normalized AWS dependency graph."""

    model_config = ConfigDict(extra="ignore")

    id: str = Field(description="Unique node identifier (typically resource ARN or ID)")
    type: ResourceType
    name: str
    arn: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DependencyGraphEdge(BaseModel):
    """Edge connecting two nodes in the normalized AWS dependency graph."""

    model_config = ConfigDict(extra="ignore")

    source: str = Field(description="Node ID of source")
    target: str = Field(description="Node ID of target")
    relationship: RelationshipType
    evidence: EvidenceType
    confidence: ConfidenceLevel = Field(default=ConfidenceLevel.OBSERVED)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DependencyGraph(BaseModel):
    """
    Normalized graph representation of AWS infrastructure relationships.
    """

    model_config = ConfigDict(extra="ignore")

    nodes: List[DependencyGraphNode] = Field(default_factory=list)
    edges: List[DependencyGraphEdge] = Field(default_factory=list)


class DependencyDiscoveryResult(BaseModel):
    """
    Wrapper for dependency discovery execution result with evidence status.
    """

    model_config = ConfigDict(extra="ignore")

    dependencies: List[NormalizedDependency] = Field(default_factory=list)
    graph: DependencyGraph = Field(default_factory=DependencyGraph)
    evidence_status: ConfidenceLevel = Field(default=ConfidenceLevel.OBSERVED)
    reason: Optional[str] = None

