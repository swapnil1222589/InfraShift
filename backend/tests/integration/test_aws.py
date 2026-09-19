import boto3
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


def has_aws_credentials():
    try:
        sts = boto3.client('sts', region_name=settings.AWS_REGION)
        sts.get_caller_identity()
        return True
    except Exception:  # noqa: BLE001
        return False

@pytest.mark.aws
def test_aws_health_endpoint():
    if not has_aws_credentials():
        pytest.skip("No AWS credentials available in environment.")
        
    settings.LIVE_AWS = True
    client = TestClient(app)
    
    res = client.get("/api/v1/health/aws")
    data = res.json()
    
    assert data["status"] != "skipped"
    settings.LIVE_AWS = False
