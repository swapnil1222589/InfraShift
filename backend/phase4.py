import os

base_dir = r"C:\Users\swapn\.gemini\antigravity\scratch\infrashift-backend\backend"

files = {
    "pytest.ini": """[pytest]
markers =
    aws: tests that require real AWS credentials
""",

    "app/core/config.py": """from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ENV: str = "development"
    LOCAL_MODE: bool = True
    LIVE_AWS: bool = False
    MOCK_AI: bool = True
    MOCK_GITHUB: bool = True

    AWS_REGION: str = "us-east-1"
    
    GITHUB_TOKEN: str = ""
    GITHUB_WEBHOOK_SECRET: str = ""

    DYNAMODB_PROJECTS_TABLE: str = "infrashift-projects"
    DYNAMODB_ANALYSES_TABLE: str = "infrashift-analyses"
    DYNAMODB_AUDIT_TABLE: str = "infrashift-audit-events"

    S3_BUCKET: str = ""
    AI_SERVICE_URL: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
""",

    "app/api/health.py": """from fastapi import APIRouter
import boto3
from app.core.config import settings
import logging

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
            
    except Exception as e:
        status_report["dynamodb"] = "error"
        status_report["errors"].append(f"DynamoDB Error: {e}")
        status_report["status"] = "error"
        
    try:
        cw = boto3.client('cloudwatch', region_name=settings.AWS_REGION)
        # Attempt minimal read-only list_metrics action to test IAM
        cw.list_metrics(Namespace='AWS/Lambda', Limit=1)
    except Exception as e:
        status_report["cloudwatch"] = "error"
        status_report["errors"].append(f"CloudWatch Error: {e}")
        status_report["status"] = "error"
        
    return status_report
""",

    "tests/integration/test_aws.py": """import pytest
import boto3
from app.core.config import settings
from fastapi.testclient import TestClient
from app.main import app

def has_aws_credentials():
    try:
        sts = boto3.client('sts', region_name=settings.AWS_REGION)
        sts.get_caller_identity()
        return True
    except Exception:
        return False

@pytest.mark.aws
def test_aws_health_endpoint():
    if not has_aws_credentials():
        pytest.skip("No AWS credentials available in environment.")
        
    # We must explicitly toggle LIVE_AWS to test the endpoint
    settings.LIVE_AWS = True
    client = TestClient(app)
    
    res = client.get("/health/aws")
    data = res.json()
    
    # If creds exist, it might succeed or fail depending on if tables exist
    # But it shouldn't be "skipped"
    assert data["status"] != "skipped"
    
    settings.LIVE_AWS = False
"""
}

# Update Repositories & Services to use LIVE_AWS instead of (not LOCAL_MODE)
# This is a bit of text processing, but since I wrote them, I know where they are.
# Actually, I'll use replace_file_content for precision in the repos.

for path, content in files.items():
    full_path = os.path.join(base_dir, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)

print("Files written successfully")
