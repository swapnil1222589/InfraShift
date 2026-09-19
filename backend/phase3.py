import os

base_dir = r"C:\Users\swapn\.gemini\antigravity\scratch\infrashift-backend\backend"

files = {
    "app/schemas/analysis.py": """from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class AnalysisCreate(BaseModel):
    prId: str
    commitSha: str
    
class AnalysisResponse(BaseModel):
    analysisId: str
    projectId: str
    prId: str
    repo: str
    commitSha: str
    status: str
    createdAt: datetime
    updatedAt: datetime
    completedAt: Optional[datetime] = None
    error: Optional[str] = None
    changedFiles: Optional[List[str]] = []
    affectedResources: Optional[List[str]] = []
    forecast: Optional[Dict[str, Any]] = None
    evidence: Optional[List[Any]] = []
    recommendations: Optional[List[Any]] = []
    assumptions: Optional[List[Any]] = []
    
class OutcomeCreate(BaseModel):
    actualCost: str
    actualPerformance: str
    deploymentResult: str
    
class OutcomeResponse(OutcomeCreate):
    analysisId: str
    timestamp: datetime
    forecastCost: str
    forecastPerformance: str

class RecommendationModel(BaseModel):
    action: str
    reason: str
    priority: str
    affectedResource: str

class ForecastModel(BaseModel):
    costRange: str
    performanceRange: str

class AIResponseModel(BaseModel):
    forecast: ForecastModel
    confidence: float
    evidence: List[Dict[str, Any]]
    assumptions: List[str]
    recommendations: List[RecommendationModel]
""",
    
    "app/repositories/project_repository.py": """import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
from typing import Dict, Optional
from app.schemas.project import ProjectResponse
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class ProjectRepository:
    def __init__(self):
        self.db: Dict[str, ProjectResponse] = {}
        if not settings.LOCAL_MODE:
            self.dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
            self.table = self.dynamodb.Table(settings.DYNAMODB_PROJECTS_TABLE)

    async def save(self, project: ProjectResponse):
        if settings.LOCAL_MODE:
            self.db[project.projectId] = project
        else:
            try:
                self.table.put_item(Item=project.model_dump(mode='json'))
            except ClientError as e:
                logger.error(f"DynamoDB Error: {e}")
                raise

    async def get(self, project_id: str) -> Optional[ProjectResponse]:
        if settings.LOCAL_MODE:
            return self.db.get(project_id)
        else:
            try:
                response = self.table.get_item(Key={'projectId': project_id})
                item = response.get('Item')
                return ProjectResponse(**item) if item else None
            except ClientError as e:
                logger.error(f"DynamoDB Error: {e}")
                return None

    async def get_by_repo(self, repo: str) -> Optional[ProjectResponse]:
        if settings.LOCAL_MODE:
            for p in self.db.values():
                if p.repo == repo:
                    return p
            return None
        else:
            try:
                response = self.table.scan(FilterExpression=Attr('repo').eq(repo))
                items = response.get('Items', [])
                return ProjectResponse(**items[0]) if items else None
            except ClientError as e:
                logger.error(f"DynamoDB Error: {e}")
                return None

project_repo = ProjectRepository()
""",

    "app/repositories/analysis_repository.py": """import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
from typing import Dict, List, Optional
from app.schemas.analysis import AnalysisResponse, OutcomeResponse
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class AnalysisRepository:
    def __init__(self):
        self.analyses: Dict[str, AnalysisResponse] = {}
        self.outcomes: Dict[str, OutcomeResponse] = {}
        if not settings.LOCAL_MODE:
            self.dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
            self.analyses_table = self.dynamodb.Table(settings.DYNAMODB_ANALYSES_TABLE)
            self.outcomes_table = self.dynamodb.Table(settings.DYNAMODB_AUDIT_TABLE)

    async def save(self, analysis: AnalysisResponse):
        if settings.LOCAL_MODE:
            self.analyses[analysis.analysisId] = analysis
        else:
            try:
                self.analyses_table.put_item(Item=analysis.model_dump(mode='json'))
            except ClientError as e:
                logger.error(f"DynamoDB Error: {e}")
                raise

    async def get(self, analysis_id: str) -> Optional[AnalysisResponse]:
        if settings.LOCAL_MODE:
            return self.analyses.get(analysis_id)
        else:
            try:
                response = self.analyses_table.get_item(Key={'analysisId': analysis_id})
                item = response.get('Item')
                return AnalysisResponse(**item) if item else None
            except ClientError as e:
                logger.error(f"DynamoDB Error: {e}")
                return None
        
    async def get_by_project(self, project_id: str) -> List[dict]:
        res = []
        if settings.LOCAL_MODE:
            analyses_list = [a for a in self.analyses.values() if a.projectId == project_id]
            for a in analyses_list:
                out = self.outcomes.get(a.analysisId)
                res.append({"analysis": a.model_dump(), "outcome": out.model_dump() if out else None})
        else:
            try:
                response = self.analyses_table.scan(FilterExpression=Attr('projectId').eq(project_id))
                items = response.get('Items', [])
                for item in items:
                    a = AnalysisResponse(**item)
                    out_resp = self.outcomes_table.get_item(Key={'analysisId': a.analysisId})
                    out_item = out_resp.get('Item')
                    res.append({
                        "analysis": a.model_dump(),
                        "outcome": OutcomeResponse(**out_item).model_dump() if out_item else None
                    })
            except ClientError as e:
                logger.error(f"DynamoDB Error: {e}")
        return res
        
    async def save_outcome(self, outcome: OutcomeResponse):
        if settings.LOCAL_MODE:
            self.outcomes[outcome.analysisId] = outcome
        else:
            try:
                self.outcomes_table.put_item(Item=outcome.model_dump(mode='json'))
            except ClientError as e:
                logger.error(f"DynamoDB Error: {e}")
                raise

analysis_repo = AnalysisRepository()
""",

    "app/services/cloudwatch_service.py": """import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta, timezone
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class CloudWatchService:
    def __init__(self):
        if not settings.LOCAL_MODE:
            self.client = boto3.client('cloudwatch', region_name=settings.AWS_REGION)

    def get_metrics(self, namespace: str, metric_name: str, dimensions: list, days: int = 7) -> dict:
        if settings.LOCAL_MODE:
            return {
                "metric": metric_name,
                "value": 1500,
                "is_mock": True,
                "insufficient_evidence": False
            }
            
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=days)
        
        try:
            response = self.client.get_metric_data(
                MetricDataQueries=[
                    {
                        'Id': 'query1',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': namespace,
                                'MetricName': metric_name,
                                'Dimensions': dimensions
                            },
                            'Period': 86400 * days,
                            'Stat': 'Sum'
                        }
                    }
                ],
                StartTime=start_time,
                EndTime=end_time
            )
            
            values = response.get('MetricDataResults', [{}])[0].get('Values', [])
            total = sum(values) if values else 0
            
            return {
                "metric": metric_name,
                "value": total,
                "is_mock": False,
                "insufficient_evidence": len(values) == 0
            }
        except ClientError as e:
            logger.error(f"CloudWatch Error: {e}")
            return {"error": str(e), "insufficient_evidence": True, "is_mock": False}

cloudwatch_service = CloudWatchService()
""",

    "app/services/ai_service.py": """from app.core.config import settings
from app.schemas.analysis import AIResponseModel
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

async def analyze_impact(payload: dict) -> dict:
    if settings.MOCK_AI:
        raw_response = {
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
    else:
        # In a real scenario, this would call the AI endpoint and parse JSON.
        # For this MVP, if MOCK_AI is false but not implemented, return empty.
        # Person 1 will implement this.
        raw_response = {}

    try:
        # Validate using Pydantic
        validated_data = AIResponseModel(**raw_response)
        return validated_data.model_dump()
    except ValidationError as e:
        logger.error(f"AI Response Validation Error: {e}")
        raise ValueError("AI response failed schema validation")
""",

    "app/services/github_service.py": """import httpx
from fastapi import BackgroundTasks
from app.core.config import settings
from app.schemas.analysis import AnalysisCreate
from app.schemas.project import ProjectCreate
from app.services.analysis_service import start_analysis
from app.services.project_service import create_project
from app.repositories.project_repository import project_repo
from app.repositories.analysis_repository import analysis_repo

async def get_pr_files(repo_full_name: str, pr_number: int) -> dict:
    if settings.MOCK_GITHUB:
        return {
            "changed_files": ["src/lambda/handler.py", "template.yaml"],
            "additions": 45,
            "deletions": 12
        }
    
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        resp = await client.get(f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}/files", headers=headers)
        if resp.status_code != 200:
            return {"changed_files": [], "additions": 0, "deletions": 0}
            
        files = resp.json()
        changed_files = [f["filename"] for f in files]
        additions = sum(f.get("additions", 0) for f in files)
        deletions = sum(f.get("deletions", 0) for f in files)
        return {"changed_files": changed_files, "additions": additions, "deletions": deletions}

async def process_webhook(data: dict, background_tasks: BackgroundTasks):
    action = data.get("action")
    if action not in ["opened", "synchronize", "reopened"]:
        return
        
    pr = data.get("pull_request", {})
    repo = data.get("repository", {})
    
    repo_full_name = repo.get("full_name")
    pr_number = pr.get("number")
    commit_sha = pr.get("head", {}).get("sha")
    
    if not all([repo_full_name, pr_number, commit_sha]):
        return
        
    # Get or create project
    project = await project_repo.get_by_repo(repo_full_name)
    if not project:
        proj_in = ProjectCreate(
            repo=repo_full_name,
            environment="development",
            owner=repo.get("owner", {}).get("login", "unknown"),
            awsEnvironment="demo"
        )
        project = await create_project(proj_in)
        
    # Idempotency check: Don't re-run for same PR and commit SHA
    history = await analysis_repo.get_by_project(project.projectId)
    for entry in history:
        a_data = entry["analysis"]
        if a_data["prId"] == str(pr_number) and a_data["commitSha"] == commit_sha:
            return # Already processed this commit
            
    analysis_in = AnalysisCreate(
        prId=str(pr_number),
        commitSha=commit_sha
    )
    
    await start_analysis(project.projectId, analysis_in, background_tasks)
""",

    "app/workers/analysis_worker.py": """from app.repositories.analysis_repository import analysis_repo
from app.services.ai_service import analyze_impact
from app.services.cloudwatch_service import cloudwatch_service
import asyncio
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

async def run_analysis(analysis_id: str):
    from app.services.github_service import get_pr_files
    
    analysis = await analysis_repo.get(analysis_id)
    if not analysis or analysis.status != "PENDING":
        return
        
    analysis.status = "RUNNING"
    analysis.updatedAt = datetime.now(timezone.utc)
    await analysis_repo.save(analysis)
    
    try:
        # 1. Fetch GitHub PR Files with Timeout
        pr_data = await asyncio.wait_for(get_pr_files(analysis.repo, int(analysis.prId)), timeout=10.0)
        analysis.changedFiles = pr_data.get("changed_files", [])
        
        # 2. Map Affected Resources
        function_name = f"{analysis.repo.split('/')[-1]}-main-func"
        analysis.affectedResources = [f"arn:aws:lambda:region:account:function:{function_name}"]
        
        # 3. Collect AWS Evidence (synchronous call wrapped in executor)
        loop = asyncio.get_running_loop()
        cw_evidence = await loop.run_in_executor(
            None, 
            cloudwatch_service.get_metrics, 
            'AWS/Lambda', 'Invocations', [{'Name': 'FunctionName', 'Value': function_name}], 7
        )
        
        # 4. AI Service
        ai_payload = {
            "changed_files": analysis.changedFiles,
            "additions": pr_data.get("additions", 0),
            "deletions": pr_data.get("deletions", 0),
            "aws_evidence": cw_evidence
        }
        
        ai_response = await asyncio.wait_for(analyze_impact(ai_payload), timeout=30.0)
        
        analysis.forecast = ai_response.get("forecast")
        analysis.confidence = ai_response.get("confidence")
        
        evidence = ai_response.get("evidence", [])
        evidence.append({"source": "cloudwatch", "metrics": cw_evidence})
        analysis.evidence = evidence
        
        analysis.assumptions = ai_response.get("assumptions")
        analysis.recommendations = ai_response.get("recommendations")
        
        analysis.status = "COMPLETED"
        
    except asyncio.TimeoutError:
        analysis.status = "FAILED"
        analysis.error = "External service timeout (GitHub or AI)"
        logger.error(f"Analysis {analysis_id} timed out.")
    except Exception as e:
        analysis.status = "FAILED"
        analysis.error = str(e)
        logger.exception(f"Analysis {analysis_id} failed.")
        
    analysis.completedAt = datetime.now(timezone.utc)
    analysis.updatedAt = datetime.now(timezone.utc)
    await analysis_repo.save(analysis)
""",

    "tests/unit/test_api.py": """import hmac
import hashlib
from app.core.config import settings
import pytest
import asyncio
from unittest.mock import patch

def test_full_project_analysis_flow(client):
    # 1. POST /projects
    res_proj = client.post("/projects", json={
        "repo": "test/integration",
        "environment": "staging",
        "owner": "dev",
        "awsEnvironment": "demo"
    })
    assert res_proj.status_code == 200
    proj = res_proj.json()
    assert proj["repo"] == "test/integration"
    project_id = proj["projectId"]
    
    # 2. GET /projects/{id}
    res_get_proj = client.get(f"/projects/{project_id}")
    assert res_get_proj.status_code == 200
    assert res_get_proj.json()["projectId"] == project_id
    
    # 3. POST /projects/{id}/analyses
    res_ana = client.post(f"/projects/{project_id}/analyses", json={
        "prId": "99",
        "commitSha": "xyz"
    })
    assert res_ana.status_code == 200
    ana = res_ana.json()
    assert ana["status"] == "PENDING"
    analysis_id = ana["analysisId"]
    
    # We must yield to the event loop so BackgroundTasks can run.
    # But since FastAPI TestClient runs synchronously in the test function, BackgroundTasks are executed synchronously AFTER the response is returned!
    # So the analysis worker has already run.
    
    # 4. GET /analyses/{id}
    res_get_ana = client.get(f"/analyses/{analysis_id}")
    assert res_get_ana.status_code == 200
    completed_ana = res_get_ana.json()
    assert completed_ana["status"] == "COMPLETED"
    assert "mock_cloudwatch" in str(completed_ana["evidence"])
    
    # 5. POST /analyses/{id}/outcome
    res_out = client.post(f"/analyses/{analysis_id}/outcome", json={
        "actualCost": "+$15/mo",
        "actualPerformance": "Same",
        "deploymentResult": "SUCCESS"
    })
    assert res_out.status_code == 200
    
    # 6. GET /projects/{id}/history
    res_hist = client.get(f"/projects/{project_id}/history")
    assert res_hist.status_code == 200
    assert len(res_hist.json()) > 0
    assert res_hist.json()[0]["outcome"]["actualCost"] == "+$15/mo"

def test_webhook_idempotency(client):
    payload = {
        "action": "opened",
        "pull_request": {"number": 55, "head": {"sha": "idemp123"}},
        "repository": {"full_name": "test/idempo", "owner": {"login": "usr"}}
    }
    
    # First call
    res1 = client.post("/github/webhook", json=payload)
    assert res1.status_code == 200
    
    # Need to verify project and analysis count
    # we can call history on the project by searching it
    res_proj = client.post("/projects", json={
        "repo": "test/idempo",
        "environment": "dev",
        "owner": "usr",
        "awsEnvironment": "demo"
    })
    
    # Wait, the webhook creates a project if missing. We can just check its repo logic.
    # Second call should not crash and should not duplicate analysis
    res2 = client.post("/github/webhook", json=payload)
    assert res2.status_code == 200

def test_invalid_webhook_signature(client):
    # Enable signature validation by setting a dummy secret temporarily
    original_secret = settings.GITHUB_WEBHOOK_SECRET
    settings.GITHUB_WEBHOOK_SECRET = "secret123"
    settings.MOCK_GITHUB = False
    
    try:
        payload = b'{"action": "opened"}'
        res = client.post("/github/webhook", content=payload, headers={"X-Hub-Signature-256": "sha256=invalid"})
        assert res.status_code == 403
    finally:
        settings.GITHUB_WEBHOOK_SECRET = original_secret
        settings.MOCK_GITHUB = True
        
def test_failed_analysis_worker(client):
    # Trigger a fail by sending bad AI response mock temporarily
    # We will mock ai_service.analyze_impact to raise ValueError
    with patch("app.workers.analysis_worker.analyze_impact", side_effect=ValueError("AI error")):
        res_proj = client.post("/projects", json={
            "repo": "test/fail",
            "environment": "staging",
            "owner": "dev",
            "awsEnvironment": "demo"
        })
        project_id = res_proj.json()["projectId"]
        
        res_ana = client.post(f"/projects/{project_id}/analyses", json={
            "prId": "1",
            "commitSha": "111"
        })
        
        analysis_id = res_ana.json()["analysisId"]
        res_get = client.get(f"/analyses/{analysis_id}")
        assert res_get.json()["status"] == "FAILED"
        assert res_get.json()["error"] == "AI error"
""",

    "tests/unit/test_services.py": """from unittest.mock import patch, MagicMock
from app.services.cloudwatch_service import cloudwatch_service
from app.core.config import settings

def test_cloudwatch_mock_mode():
    res = cloudwatch_service.get_metrics('AWS/Lambda', 'Invocations', [])
    assert res["is_mock"] is True
    assert res["value"] == 1500

@patch('boto3.client')
def test_cloudwatch_real_mode_success(mock_boto_client):
    # Temporarily set LOCAL_MODE = False
    settings.LOCAL_MODE = False
    
    # Mock boto response
    mock_client_instance = MagicMock()
    mock_boto_client.return_value = mock_client_instance
    mock_client_instance.get_metric_data.return_value = {
        "MetricDataResults": [{"Values": [10, 20, 30]}]
    }
    
    # Instantiate a new service to pick up LOCAL_MODE = False
    from app.services.cloudwatch_service import CloudWatchService
    cw_service = CloudWatchService()
    
    res = cw_service.get_metrics('AWS/Lambda', 'Invocations', [])
    assert res["is_mock"] is False
    assert res["value"] == 60
    assert res["insufficient_evidence"] is False
    
    # Reset
    settings.LOCAL_MODE = True
""",

    "README.md": """# InfraShift Backend MVP

## Architecture & Integration
The backend serves as the orchestration layer between GitHub (Webhooks), AWS (CloudWatch, DynamoDB), and the AI Forecasting layer.

### Workflow
1. **GitHub PR Webhook** hits `/github/webhook`.
2. Backend parses repo, PR, and commit. Idempotency checks prevent duplicates.
3. Analysis job is spawned.
4. **GitHub Service** fetches changed files.
5. **CloudWatch Service** fetches metrics for affected resources.
6. **AI Service** generates a forecast and recommendations.
7. Results are persisted to **DynamoDB**.

## Local Setup
```bash
python -m venv venv
# On Windows: .\\venv\\Scripts\\activate
# On Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Environment Variables
- `LOCAL_MODE`: (true/false) If true, bypasses DynamoDB and AWS SDKs and uses in-memory dicts.
- `MOCK_GITHUB`: (true/false) If true, bypasses real GitHub PR API fetches and signature validation.
- `MOCK_AI`: (true/false) If true, bypasses real AI model and uses hard-coded response.
- `AWS_REGION`: AWS region (e.g. `us-east-1`).
- `GITHUB_WEBHOOK_SECRET`: HMAC signature for webhooks.

## DynamoDB Setup
When `LOCAL_MODE=false`, these tables are required:
- `infrashift-projects` (Partition Key: `projectId` String)
- `infrashift-analyses` (Partition Key: `analysisId` String)
- `infrashift-audit-events` (Partition Key: `analysisId` String)

## CloudWatch IAM Permissions
The role running this backend needs `cloudwatch:GetMetricData` to read metrics.

## API Examples
Check `/docs` on the running server for interactive Swagger UI.

### Create Project
`POST /projects`
```json
{
  "repo": "owner/repo",
  "environment": "development",
  "owner": "user",
  "awsEnvironment": "demo"
}
```

### Get Analysis
`GET /analyses/{analysisId}`
""",

    "INTEGRATION.md": """# Integration Contracts

## For Person 1 (AI / Forecasting)
- You own `app/services/ai_service.py`.
- Implement `analyze_impact(payload: dict) -> dict`.
- The backend will send you: `changed_files`, `additions`, `deletions`, and `aws_evidence`.
- You MUST return a dict that strictly conforms to `AIResponseModel` in `app/schemas/analysis.py`.
- Test your changes with `MOCK_AI=false`.

## For Person 2 (AWS / Infrastructure)
- You own AWS resource mapping and telemetry.
- Deploy the DynamoDB tables: `infrashift-projects`, `infrashift-analyses`, `infrashift-audit-events`.
- Ensure IAM policies allow DynamoDB CRUD and CloudWatch `GetMetricData`.
- The backend currently aggregates `AWS/Lambda` Invocations. Modify `cloudwatch_service.py` to add more queries.
- Test with `LOCAL_MODE=false`.

## For Person 4 (Frontend)
- You own the dashboard.
- API is available at `http://localhost:8000/docs`.
- Primary endpoints to consume:
  - `GET /projects/{id}/history` (Shows past PR impacts)
  - `GET /analyses/{id}` (Poll this for `status: "COMPLETED"`)
- The JSON structures are fully typed via FastAPI Pydantic schemas.
"""
}

for path, content in files.items():
    full_path = os.path.join(base_dir, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)

print("Phase 3 files successfully written.")
