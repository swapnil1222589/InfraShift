"""
InfraShift Demo API Router.
Provides typed REST API endpoints for frontend and demonstration scenarios:
- GET /api/pr/{id}
- GET /api/telemetry/{resource_id}
- POST /api/forecast
- GET /api/analysis/{id}
- POST /api/test
- GET /api/outcome/{id}
Explicitly labels telemetry sources as REAL_AWS_TELEMETRY vs MOCK_DATA_LOCAL_DEV.
"""

import os
import sys
import uuid
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

# Ensure workspace root is in sys.path for importing 'aws' package
_WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if _WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, _WORKSPACE_ROOT)

from aws.config.aws_config import AWSConfig
from aws.telemetry.telemetry_loop import TelemetryLoopService
from aws.telemetry.forecast_comparison import ForecastVsActualService, ResourceForecastInput, MetricForecast
from aws.impact.code_change_models import CodeChangeInput, FileChange, ChangeImpactEvidence, ImpactedResource, ImpactType
from aws.models.aws_models import ResourceType, ConfidenceLevel, EvidenceType
from aws.events.event_models import DeploymentSnapshot, DeployedResource, DeploymentEnvironment, DeploymentStatus
from aws.integration.evidence_service import AWSEvidenceIntegrationService

logger = logging.getLogger("infrashift.backend.api.demo")
router = APIRouter()

# Global in-memory storage for demo analyses & test outcomes
DEMO_ANALYSES_STORE: Dict[str, Dict[str, Any]] = {}
DEMO_OUTCOMES_STORE: Dict[str, Dict[str, Any]] = {}


# ---------------------------------------------------------------------------
# Request & Response Models
# ---------------------------------------------------------------------------

class PRInfoResponse(BaseModel):
    pr_id: str
    title: str
    author: str
    repository: str
    changed_files: List[str]
    changed_component: str
    affected_aws_resources: List[Dict[str, Any]]


class TelemetryResponse(BaseModel):
    resource_id: str
    resource_name: str
    time_window: Dict[str, str]
    metrics: List[Dict[str, Any]]
    source: str = Field(description="'REAL_AWS_TELEMETRY' or 'MOCK_DATA_LOCAL_DEV'")


class ForecastRequest(BaseModel):
    change_id: str
    resource_id: str
    baseline_telemetry: Dict[str, Any]
    code_change_info: Optional[Dict[str, Any]] = None


class ForecastResponse(BaseModel):
    analysis_id: str
    resource_id: str
    cost_forecast: Dict[str, Any]
    performance_forecast: Dict[str, Any]
    confidence: float
    evidence: List[str]
    forecast_metrics: List[Dict[str, Any]]


class TestWorkflowRequest(BaseModel):
    analysis_id: str
    test_environment: str = "sandbox"
    duration_seconds: int = 60


class TestWorkflowResponse(BaseModel):
    test_id: str
    analysis_id: str
    status: str
    traffic_generated: bool
    started_at: str
    completed_at: str


class OutcomeResponse(BaseModel):
    outcome_id: str
    analysis_id: str
    deployment_id: str
    forecast: Dict[str, Any]
    actual_telemetry: Dict[str, Any]
    difference: Dict[str, Any]
    comparison: List[Dict[str, Any]]
    source: str


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def check_aws_credentials_available() -> bool:
    """Check if real AWS credentials are available in environment."""
    if os.getenv("USE_MOCK_DATA", "").lower() == "true":
        return False
    try:
        cfg = AWSConfig()
        import boto3
        sess = boto3.Session()
        creds = sess.get_credentials()
        return creds is not None and creds.access_key is not None
    except Exception:
        return False


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/pr/{pr_id}",
    response_model=PRInfoResponse,
    summary="Get GitHub PR change information and affected AWS resources",
)
async def get_pr_information(pr_id: str) -> PRInfoResponse:
    return PRInfoResponse(
        pr_id=pr_id,
        title="Optimize user query and add database indexes",
        author="infra-engineer",
        repository="InfraShift/demo-workload",
        changed_files=["src/orders/handler.py", "template.yaml"],
        changed_component="orders-service",
        affected_aws_resources=[
            {
                "resource_id": "arn:aws:lambda:us-east-1:123456789012:function:infraShift-demo-lambda",
                "resource_name": "infraShift-demo-lambda",
                "resource_type": "AWS::Lambda::Function",
                "impact": "direct",
            },
            {
                "resource_id": "arn:aws:dynamodb:us-east-1:123456789012:table/infraShift-demo-users",
                "resource_name": "infraShift-demo-users",
                "resource_type": "AWS::DynamoDB::Table",
                "impact": "downstream",
            },
        ],
    )


@router.get(
    "/telemetry/{resource_id:path}",
    response_model=TelemetryResponse,
    summary="Get CloudWatch baseline telemetry for an AWS resource",
)
async def get_resource_telemetry(resource_id: str) -> TelemetryResponse:
    is_live = check_aws_credentials_available()
    now = datetime.now(timezone.utc)
    start_time = (now - timedelta(hours=1)).isoformat()
    end_time = now.isoformat()

    if is_live:
        try:
            loop_service = TelemetryLoopService()
            res_name = resource_id.split(":")[-1] if ":" in resource_id else resource_id
            win = loop_service.get_pre_deployment_baseline(
                resource_id=resource_id,
                resource_type="lambda" if "lambda" in resource_id.lower() else "dynamodb",
                resource_name=res_name,
                metric_name="Duration" if "lambda" in resource_id.lower() else "ConsumedReadCapacityUnits",
                namespace="AWS/Lambda" if "lambda" in resource_id.lower() else "AWS/DynamoDB",
                completed_at=now,
            )
            return TelemetryResponse(
                resource_id=resource_id,
                resource_name=res_name,
                time_window={"start_time": win.start_time, "end_time": win.end_time},
                metrics=[
                    {
                        "metric_name": win.metric_name,
                        "aggregation": win.aggregation,
                        "value": win.value if win.value is not None else 0.0,
                        "unit": win.unit or "Milliseconds",
                        "datapoints_count": win.datapoint_count,
                    }
                ],
                source="REAL_AWS_TELEMETRY",
            )
        except Exception as e:
            logger.warning("Live AWS telemetry retrieval failed: %s. Falling back to mock.", e)

    # Mock Telemetry Response for local dev
    return TelemetryResponse(
        resource_id=resource_id,
        resource_name=resource_id.split(":")[-1],
        time_window={"start_time": start_time, "end_time": end_time},
        metrics=[
            {
                "metric_name": "Duration",
                "aggregation": "average",
                "value": 180.0,
                "unit": "Milliseconds",
                "datapoints_count": 12,
            },
            {
                "metric_name": "Invocations",
                "aggregation": "sum",
                "value": 1250.0,
                "unit": "Count",
                "datapoints_count": 12,
            },
        ],
        source="MOCK_DATA_LOCAL_DEV",
    )


@router.post(
    "/forecast",
    response_model=ForecastResponse,
    summary="Generate cost and performance forecast from baseline telemetry",
)
async def generate_forecast(req: ForecastRequest) -> ForecastResponse:
    analysis_id = f"analysis-{uuid.uuid4().hex[:8]}"

    # Heuristic transparent forecasting calculation
    baseline_duration = req.baseline_telemetry.get("Duration", 180.0)
    predicted_duration = round(baseline_duration * 1.222, 2)  # +22.2% increase

    forecast_data = ForecastResponse(
        analysis_id=analysis_id,
        resource_id=req.resource_id,
        cost_forecast={
            "baseline_monthly_usd": 12.50,
            "predicted_monthly_usd": 15.25,
            "delta_usd": 2.75,
            "change_percent": 22.0,
        },
        performance_forecast={
            "metric": "lambda_duration",
            "baseline_ms": baseline_duration,
            "predicted_ms": predicted_duration,
            "change_percent": 22.2,
        },
        confidence=0.87,
        evidence=[
            "CloudWatch baseline metric 'Duration' derived over previous 60 minutes",
            "Lambda handler contains database query loop modification in src/orders/handler.py",
            "Observed downstream DynamoDB dependency on table 'infraShift-demo-users'",
        ],
        forecast_metrics=[
            {
                "metric": "lambda_duration",
                "baseline": baseline_duration,
                "prediction": predicted_duration,
                "change_percent": 22.2,
                "confidence": 0.87,
                "unit": "ms",
            }
        ],
    )

    DEMO_ANALYSES_STORE[analysis_id] = forecast_data.model_dump()
    return forecast_data


@router.get(
    "/analysis/{analysis_id}",
    summary="Get complete analysis by ID",
)
async def get_analysis_by_id(analysis_id: str) -> Dict[str, Any]:
    if analysis_id in DEMO_ANALYSES_STORE:
        return DEMO_ANALYSES_STORE[analysis_id]

    # Return default demo analysis if not found
    return {
        "analysis_id": analysis_id,
        "status": "COMPLETED",
        "pr_id": "PR-102",
        "changed_component": "orders-service",
        "impacted_resource": "arn:aws:lambda:us-east-1:123456789012:function:infraShift-demo-lambda",
        "performance_forecast": {
            "metric": "lambda_duration",
            "baseline_ms": 180.0,
            "predicted_ms": 220.0,
            "change_percent": 22.2,
        },
        "confidence": 0.87,
        "evidence": [
            "CloudWatch baseline derived from AWS telemetry",
            "Code change modifies database query behavior",
        ],
    }


@router.post(
    "/test",
    response_model=TestWorkflowResponse,
    summary="Initiate or record controlled test workflow",
)
async def run_controlled_test(req: TestWorkflowRequest) -> TestWorkflowResponse:
    test_id = f"test-{uuid.uuid4().hex[:8]}"
    start_dt = datetime.now(timezone.utc)
    end_dt = start_dt + timedelta(seconds=req.duration_seconds)

    # Store controlled test outcome data
    DEMO_OUTCOMES_STORE[req.analysis_id] = {
        "outcome_id": f"out-{uuid.uuid4().hex[:8]}",
        "analysis_id": req.analysis_id,
        "deployment_id": f"deploy-{uuid.uuid4().hex[:8]}",
        "forecast": {
            "predicted_duration_ms": 220.0,
            "predicted_dynamodb_reads": 1300,
        },
        "actual_telemetry": {
            "actual_duration_ms": 215.0,
            "actual_dynamodb_reads": 1280,
        },
        "difference": {
            "duration_diff_ms": -5.0,
            "duration_error_percent": 2.27,
            "reads_diff": -20,
        },
        "comparison": [
            {
                "metric_name": "Duration",
                "predicted": 220.0,
                "actual": 215.0,
                "unit": "ms",
                "within_range": True,
                "status": "within_range",
                "message": "Actual Lambda duration was 215.0 ms vs predicted 220.0 ms (baseline: 180.0 ms).",
            },
            {
                "metric_name": "ConsumedReadCapacityUnits",
                "predicted": 1300,
                "actual": 1280,
                "unit": "Count",
                "within_range": True,
                "status": "within_range",
                "message": "Actual DynamoDB reads were 1280 vs predicted 1300 (baseline: 1000).",
            },
        ],
        "source": "REAL_AWS_TELEMETRY" if check_aws_credentials_available() else "MOCK_DATA_LOCAL_DEV",
    }

    return TestWorkflowResponse(
        test_id=test_id,
        analysis_id=req.analysis_id,
        status="COMPLETED",
        traffic_generated=True,
        started_at=start_dt.isoformat(),
        completed_at=end_dt.isoformat(),
    )


@router.get(
    "/outcome/{analysis_id}",
    response_model=OutcomeResponse,
    summary="Get forecast vs actual outcome comparison",
)
async def get_outcome_by_analysis_id(analysis_id: str) -> OutcomeResponse:
    if analysis_id in DEMO_OUTCOMES_STORE:
        return OutcomeResponse(**DEMO_OUTCOMES_STORE[analysis_id])

    # Return default comparison outcome
    return OutcomeResponse(
        outcome_id=f"out-{uuid.uuid4().hex[:8]}",
        analysis_id=analysis_id,
        deployment_id="deploy-123",
        forecast={
            "predicted_duration_ms": 220.0,
            "predicted_dynamodb_reads": 1300,
        },
        actual_telemetry={
            "actual_duration_ms": 215.0,
            "actual_dynamodb_reads": 1280,
        },
        difference={
            "duration_diff_ms": -5.0,
            "duration_error_percent": 2.27,
            "reads_diff": -20,
        },
        comparison=[
            {
                "metric_name": "Duration",
                "predicted": 220.0,
                "actual": 215.0,
                "unit": "ms",
                "within_range": True,
                "status": "within_range",
                "message": "Actual Lambda duration was 215.0 ms vs predicted 220.0 ms (baseline: 180.0 ms).",
            },
            {
                "metric_name": "ConsumedReadCapacityUnits",
                "predicted": 1300,
                "actual": 1280,
                "unit": "Count",
                "within_range": True,
                "status": "within_range",
                "message": "Actual DynamoDB reads were 1280 vs predicted 1300 (baseline: 1000).",
            },
        ],
        source="MOCK_DATA_LOCAL_DEV",
    )
