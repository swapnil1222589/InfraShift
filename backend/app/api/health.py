import logging

import boto3
from fastapi import APIRouter

from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.get("/health/aws")
async def aws_health_check():
    if not settings.LIVE_AWS:
        return {"status": "skipped", "reason": "LIVE_AWS is false"}
        
    status_report = {"status": "connected", "dynamodb": "ok", "cloudwatch": "ok", "errors": []}
    
    try:
        ddb = boto3.client('dynamodb', region_name=settings.AWS_REGION)
        tables = ddb.list_tables().get('TableNames', [])
        required = [
            settings.DYNAMODB_PROJECTS_TABLE,
            settings.DYNAMODB_ANALYSES_TABLE,
            settings.DYNAMODB_AUDIT_TABLE
        ]
        missing = [t for t in required if t not in tables]
        if missing:
            status_report["dynamodb"] = "missing_tables"
            status_report["errors"].append(f"Missing tables: {missing}")
            status_report["status"] = "degraded"
            
    except Exception as e:  # noqa: BLE001
        status_report["dynamodb"] = "error"
        status_report["errors"].append(f"DynamoDB Error: {e}")
        status_report["status"] = "error"
        
    try:
        cw = boto3.client('cloudwatch', region_name=settings.AWS_REGION)
        # Attempt minimal read-only list_metrics action to test IAM
        cw.list_metrics(Namespace='AWS/Lambda', Limit=1)
    except Exception as e:  # noqa: BLE001
        status_report["cloudwatch"] = "error"
        status_report["errors"].append(f"CloudWatch Error: {e}")
        status_report["status"] = "error"
        
    return status_report
