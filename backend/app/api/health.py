"""Health check endpoints."""
from __future__ import annotations

import logging

from fastapi import APIRouter, Request

from app.core.config import settings
from app.core.security import get_request_id

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", summary="Basic health check")
async def health_check(request: Request) -> dict:
    return {
        "status": "ok",
        "service": "infrashift-backend",
        "environment": settings.ENVIRONMENT,
        "request_id": get_request_id(request),
    }


@router.get("/health/aws", summary="AWS connectivity check")
async def aws_health_check(request: Request) -> dict:
    request_id = get_request_id(request)

    if not settings.LIVE_AWS:
        return {
            "status": "local",
            "aws_enabled": False,
            "request_id": request_id,
        }

    # LIVE_AWS=true — actually test AWS connectivity
    report: dict = {
        "status": "ok",
        "aws_enabled": True,
        "dynamodb": "ok",
        "cloudwatch": "ok",
        "errors": [],
        "request_id": request_id,
    }

    # Test DynamoDB
    try:
        import boto3  # noqa: PLC0415

        ddb = boto3.client("dynamodb", region_name=settings.AWS_REGION)
        tables_resp = ddb.list_tables()
        table_names = tables_resp.get("TableNames", [])
        required = [
            settings.DYNAMODB_PROJECTS_TABLE,
            settings.DYNAMODB_ANALYSES_TABLE,
            settings.DYNAMODB_AUDIT_TABLE,
        ]
        missing = [t for t in required if t not in table_names]
        if missing:
            report["dynamodb"] = "missing_tables"
            report["errors"].append(f"Missing DynamoDB tables: {missing}")
            report["status"] = "degraded"
    except Exception as exc:  # noqa: BLE001
        report["dynamodb"] = "error"
        report["errors"].append(f"DynamoDB error: {type(exc).__name__}")
        report["status"] = "error"

    # Test CloudWatch
    try:
        import boto3  # noqa: PLC0415

        cw = boto3.client("cloudwatch", region_name=settings.AWS_REGION)
        cw.list_metrics(Namespace="AWS/Lambda", Limit=1)
    except Exception as exc:  # noqa: BLE001
        report["cloudwatch"] = "error"
        report["errors"].append(f"CloudWatch error: {type(exc).__name__}")
        report["status"] = "error"

    if report["status"] == "error":
        from fastapi.responses import JSONResponse  # noqa: PLC0415

        return JSONResponse(status_code=503, content=report)

    return report
