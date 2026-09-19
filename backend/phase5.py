import os

base_dir = r"C:\Users\swapn\.gemini\antigravity\scratch\infrashift-backend\backend"

files = {
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
    
    FRONTEND_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"

settings = Settings()
""",
    
    "app/main.py": """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import health, projects, analyses, github
from app.core.config import settings

app = FastAPI(
    title="InfraShift Backend",
    description="Backend API for InfraShift MVP",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(analyses.router, prefix="/api/v1/analyses", tags=["Analyses"])
app.include_router(github.router, prefix="/api/v1/github", tags=["GitHub"])
""",
    
    "smoke_test.py": """import httpx
import time

BASE_URL = "http://localhost:8000/api/v1"

def run_smoke_test():
    with httpx.Client(base_url=BASE_URL) as client:
        print("--- RUNNING SMOKE TEST ---")
        
        # 1. Health
        print("1. GET /health")
        r = client.get("/health")
        r.raise_for_status()
        print("✅", r.json())
        
        # 2. Create Project
        print("\\n2. POST /projects")
        proj_data = {"repo": "infrashift/smoke-test", "environment": "dev", "owner": "tester", "awsEnvironment": "demo"}
        r = client.post("/projects", json=proj_data)
        r.raise_for_status()
        proj_id = r.json()["projectId"]
        print("✅ Created project:", proj_id)
        
        # 3. Get Project
        print(f"\\n3. GET /projects/{proj_id}")
        r = client.get(f"/projects/{proj_id}")
        r.raise_for_status()
        print("✅", r.json()["repo"])
        
        # 4. Create Analysis
        print(f"\\n4. POST /projects/{proj_id}/analyses")
        ana_data = {"prId": "100", "commitSha": "abc1234"}
        r = client.post(f"/projects/{proj_id}/analyses", json=ana_data)
        r.raise_for_status()
        ana_id = r.json()["analysisId"]
        print("✅ Created analysis:", ana_id)
        
        # Wait for background worker
        print("Waiting 2s for background worker...")
        time.sleep(2)
        
        # 5. Get Analysis
        print(f"\\n5. GET /analyses/{ana_id}")
        r = client.get(f"/analyses/{ana_id}")
        r.raise_for_status()
        print("✅ Status:", r.json()["status"])
        
        # 6. Get Impact
        print(f"\\n6. GET /analyses/{ana_id}/impact")
        r = client.get(f"/analyses/{ana_id}/impact")
        r.raise_for_status()
        print("✅", list(r.json().keys()))
        
        # 7. Get Forecast
        print(f"\\n7. GET /analyses/{ana_id}/forecast")
        r = client.get(f"/analyses/{ana_id}/forecast")
        r.raise_for_status()
        print("✅", list(r.json().keys()))
        
        # 8. Get Evidence
        print(f"\\n8. GET /analyses/{ana_id}/evidence")
        r = client.get(f"/analyses/{ana_id}/evidence")
        r.raise_for_status()
        print("✅", list(r.json().keys()))
        
        # 9. Get Recommendations
        print(f"\\n9. GET /analyses/{ana_id}/recommendations")
        r = client.get(f"/analyses/{ana_id}/recommendations")
        r.raise_for_status()
        print("✅", list(r.json().keys()))
        
        # 10. Post Outcome
        print(f"\\n10. POST /analyses/{ana_id}/outcome")
        out_data = {"actualCost": "+$20/mo", "actualPerformance": "Same", "deploymentResult": "SUCCESS"}
        r = client.post(f"/analyses/{ana_id}/outcome", json=out_data)
        r.raise_for_status()
        print("✅ Outcome recorded")
        
        # 11. Get History
        print(f"\\n11. GET /projects/{proj_id}/history")
        r = client.get(f"/projects/{proj_id}/history")
        r.raise_for_status()
        print(f"✅ History count: {len(r.json())}")
        
        print("\\n--- SMOKE TEST SUCCESSFUL ---")

if __name__ == "__main__":
    run_smoke_test()
""",
    
    "tests/unit/test_api.py": """import hmac
import hashlib
from app.core.config import settings
import pytest
import asyncio
from unittest.mock import patch

def test_full_project_analysis_flow(client):
    res_proj = client.post("/api/v1/projects", json={
        "repo": "test/integration",
        "environment": "staging",
        "owner": "dev",
        "awsEnvironment": "demo"
    })
    assert res_proj.status_code == 200
    proj = res_proj.json()
    assert proj["repo"] == "test/integration"
    project_id = proj["projectId"]
    
    res_get_proj = client.get(f"/api/v1/projects/{project_id}")
    assert res_get_proj.status_code == 200
    assert res_get_proj.json()["projectId"] == project_id
    
    res_ana = client.post(f"/api/v1/projects/{project_id}/analyses", json={
        "prId": "99",
        "commitSha": "xyz"
    })
    assert res_ana.status_code == 200
    ana = res_ana.json()
    assert ana["status"] == "PENDING"
    analysis_id = ana["analysisId"]
    
    res_get_ana = client.get(f"/api/v1/analyses/{analysis_id}")
    assert res_get_ana.status_code == 200
    completed_ana = res_get_ana.json()
    assert completed_ana["status"] == "COMPLETED"
    
    res_out = client.post(f"/api/v1/analyses/{analysis_id}/outcome", json={
        "actualCost": "+$15/mo",
        "actualPerformance": "Same",
        "deploymentResult": "SUCCESS"
    })
    assert res_out.status_code == 200
    
    res_hist = client.get(f"/api/v1/projects/{project_id}/history")
    assert res_hist.status_code == 200
    assert len(res_hist.json()) > 0

def test_webhook_idempotency(client):
    payload = {
        "action": "opened",
        "pull_request": {"number": 55, "head": {"sha": "idemp123"}},
        "repository": {"full_name": "test/idempo", "owner": {"login": "usr"}}
    }
    
    res1 = client.post("/api/v1/github/webhook", json=payload)
    assert res1.status_code == 200
    
    client.post("/api/v1/projects", json={
        "repo": "test/idempo",
        "environment": "dev",
        "owner": "usr",
        "awsEnvironment": "demo"
    })
    
    res2 = client.post("/api/v1/github/webhook", json=payload)
    assert res2.status_code == 200

def test_invalid_webhook_signature(client):
    original_secret = settings.GITHUB_WEBHOOK_SECRET
    settings.GITHUB_WEBHOOK_SECRET = "secret123"
    settings.MOCK_GITHUB = False
    
    try:
        payload = b'{"action": "opened"}'
        res = client.post("/api/v1/github/webhook", content=payload, headers={"X-Hub-Signature-256": "sha256=invalid"})
        assert res.status_code == 403
    finally:
        settings.GITHUB_WEBHOOK_SECRET = original_secret
        settings.MOCK_GITHUB = True
        
def test_failed_analysis_worker(client):
    with patch("app.workers.analysis_worker.analyze_impact", side_effect=ValueError("AI error")):
        res_proj = client.post("/api/v1/projects", json={
            "repo": "test/fail",
            "environment": "staging",
            "owner": "dev",
            "awsEnvironment": "demo"
        })
        project_id = res_proj.json()["projectId"]
        
        res_ana = client.post(f"/api/v1/projects/{project_id}/analyses", json={
            "prId": "1",
            "commitSha": "111"
        })
        
        analysis_id = res_ana.json()["analysisId"]
        res_get = client.get(f"/api/v1/analyses/{analysis_id}")
        assert res_get.json()["status"] == "FAILED"
        assert res_get.json()["error"] == "AI error"
""",
    "tests/unit/test_analyses.py": """def test_create_and_get_analysis(client):
    proj_res = client.post("/api/v1/projects", json={
        "repo": "test/repo2",
        "environment": "dev",
        "owner": "test",
        "awsEnvironment": "demo"
    })
    project_id = proj_res.json()["projectId"]
    
    ana_res = client.post(f"/api/v1/projects/{project_id}/analyses", json={
        "prId": "123",
        "commitSha": "abc1234"
    })
    assert ana_res.status_code == 200
    analysis_id = ana_res.json()["analysisId"]
    
    get_res = client.get(f"/api/v1/analyses/{analysis_id}")
    assert get_res.status_code == 200
    assert get_res.json()["analysisId"] == analysis_id
""",
    "tests/unit/test_projects.py": """def test_create_project(client):
    response = client.post("/api/v1/projects", json={
        "repo": "test/repo",
        "environment": "dev",
        "owner": "test",
        "awsEnvironment": "demo"
    })
    assert response.status_code == 200
    data = response.json()
    assert "projectId" in data
""",
    "tests/unit/test_health.py": """def test_health(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
""",
    "tests/unit/test_github.py": """def test_github_webhook(client):
    payload = {
        "action": "opened",
        "pull_request": {"number": 123, "head": {"sha": "abcdef123"}},
        "repository": {"full_name": "test/webhook-repo2", "owner": {"login": "test_user"}}
    }
    res = client.post("/api/v1/github/webhook", json=payload)
    assert res.status_code == 200
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
        
    settings.LIVE_AWS = True
    client = TestClient(app)
    
    res = client.get("/api/v1/health/aws")
    data = res.json()
    
    assert data["status"] != "skipped"
    settings.LIVE_AWS = False
""",

    "INTEGRATION.md": """# InfraShift Backend Integration Contract

## PERSON 1 — AI/Forecasting

**Goal**: Swap `MOCK_AI=true` with a live inference API call in `app/services/ai_service.py`.

### Payload sent to you
The backend will aggregate GitHub and AWS context and pass you a dictionary:
```json
{
  "changed_files": ["src/lambda/handler.py"],
  "additions": 45,
  "deletions": 12,
  "aws_evidence": {
    "metric": "Invocations",
    "value": 1500,
    "is_mock": false,
    "insufficient_evidence": false
  }
}
```

### Response Expected (Strict Schema)
You must return a dictionary that exactly matches `AIResponseModel`:
```json
{
  "forecast": {
    "costRange": "+$10 to +$50/mo",
    "performanceRange": "No significant change expected"
  },
  "confidence": 0.85,
  "evidence": [{"source": "mock_cloudwatch", "metric": "cpu_utilization", "value": "45%"}],
  "assumptions": ["Traffic remains constant"],
  "recommendations": [
    {
      "action": "Monitor DynamoDB consumed capacity",
      "reason": "New query pattern might increase costs",
      "priority": "MEDIUM",
      "affectedResource": "DynamoDB Table"
    }
  ]
}
```

### Local Testing
Run the backend with `MOCK_AI=false`, hit `POST /api/v1/projects/{id}/analyses`, and check the backend logs for Pydantic validation errors.

---

## PERSON 2 — AWS/Infrastructure

**Goal**: Create real tables and connect the read-only metrics.

### DynamoDB Schema
- Table 1: `infrashift-projects`, Partition Key: `projectId` (String)
- Table 2: `infrashift-analyses`, Partition Key: `analysisId` (String)
- Table 3: `infrashift-audit-events`, Partition Key: `analysisId` (String)

### Permissions Needed by Backend Execution Role
- `dynamodb:PutItem`, `dynamodb:GetItem`, `dynamodb:Scan`
- `cloudwatch:GetMetricData`, `cloudwatch:ListMetrics`

### Verification
1. Ensure AWS credentials are in your environment (`~/.aws/credentials` or `AWS_ACCESS_KEY_ID`).
2. Run `pytest -m aws`.
3. Hit `GET /api/v1/health/aws` with `LIVE_AWS=true` in `.env`.
*NOTE: The backend is currently running without live AWS verification since it was built in a local sandbox.*

---

## PERSON 4 — Frontend

**Goal**: Integrate the React dashboard with the API.

### Environment variables
Backend CORS requires `FRONTEND_ORIGINS` (e.g., `FRONTEND_ORIGINS=["http://localhost:5173"]`).

### API Endpoints
Base URL: `http://localhost:8000/api/v1` (Production URL: `https://api.infrashift.example.com/api/v1` - Placeholder)

- `GET /health`
- `POST /projects`
- `GET /projects/{id}`
- `GET /projects/{id}/history`
- `POST /projects/{id}/analyses`
- `GET /analyses/{id}` (Poll this! Status will transition `PENDING` -> `RUNNING` -> `COMPLETED` | `FAILED`)
- `GET /analyses/{id}/impact`
- `GET /analyses/{id}/forecast`
- `GET /analyses/{id}/evidence`
- `GET /analyses/{id}/recommendations`
- `POST /analyses/{id}/outcome`

### Workflow
1. When a PR arrives, backend creates an analysis (Status `PENDING`).
2. Frontend polls `GET /analyses/{id}` every 2 seconds.
3. If `COMPLETED`, UI renders the Forecast and Recommendations.
4. If `FAILED`, UI renders `analysis.error` string.
"""
}

for path, content in files.items():
    full_path = os.path.join(base_dir, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Phase 5 files successfully written.")
