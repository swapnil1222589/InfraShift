import os

base_dir = r"C:\Users\swapn\.gemini\antigravity\scratch\infrashift-backend\backend"

files = {
    "app/repositories/project_repository.py": """import boto3
from boto3.dynamodb.conditions import Attr
from typing import Dict, Optional
from app.schemas.project import ProjectResponse
from app.core.config import settings

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
            self.table.put_item(Item=project.model_dump(mode='json'))

    async def get(self, project_id: str) -> Optional[ProjectResponse]:
        if settings.LOCAL_MODE:
            return self.db.get(project_id)
        else:
            response = self.table.get_item(Key={'projectId': project_id})
            item = response.get('Item')
            return ProjectResponse(**item) if item else None

    async def get_by_repo(self, repo: str) -> Optional[ProjectResponse]:
        if settings.LOCAL_MODE:
            for p in self.db.values():
                if p.repo == repo:
                    return p
            return None
        else:
            response = self.table.scan(FilterExpression=Attr('repo').eq(repo))
            items = response.get('Items', [])
            return ProjectResponse(**items[0]) if items else None

project_repo = ProjectRepository()
""",

    "app/repositories/analysis_repository.py": """import boto3
from boto3.dynamodb.conditions import Attr
from typing import Dict, List, Optional
from app.schemas.analysis import AnalysisResponse, OutcomeResponse
from app.core.config import settings

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
            self.analyses_table.put_item(Item=analysis.model_dump(mode='json'))

    async def get(self, analysis_id: str) -> Optional[AnalysisResponse]:
        if settings.LOCAL_MODE:
            return self.analyses.get(analysis_id)
        else:
            response = self.analyses_table.get_item(Key={'analysisId': analysis_id})
            item = response.get('Item')
            return AnalysisResponse(**item) if item else None
        
    async def get_by_project(self, project_id: str) -> List[dict]:
        res = []
        if settings.LOCAL_MODE:
            analyses_list = [a for a in self.analyses.values() if a.projectId == project_id]
            for a in analyses_list:
                out = self.outcomes.get(a.analysisId)
                res.append({"analysis": a.model_dump(), "outcome": out.model_dump() if out else None})
        else:
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
        return res
        
    async def save_outcome(self, outcome: OutcomeResponse):
        if settings.LOCAL_MODE:
            self.outcomes[outcome.analysisId] = outcome
        else:
            self.outcomes_table.put_item(Item=outcome.model_dump(mode='json'))

analysis_repo = AnalysisRepository()
""",

    "app/api/github.py": """from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
import hmac
import hashlib
from app.core.config import settings
from app.services.github_service import process_webhook

router = APIRouter()

@router.post("/webhook")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")
    
    if not settings.MOCK_GITHUB and settings.GITHUB_WEBHOOK_SECRET:
        if not signature:
            raise HTTPException(status_code=400, detail="Missing signature")
        
        mac = hmac.new(settings.GITHUB_WEBHOOK_SECRET.encode(), msg=payload, digestmod=hashlib.sha256)
        expected_signature = "sha256=" + mac.hexdigest()
        
        if not hmac.compare_digest(expected_signature, signature):
            raise HTTPException(status_code=403, detail="Invalid signature")

    data = await request.json()
    await process_webhook(data, background_tasks)
    return {"status": "received"}
""",

    "app/services/github_service.py": """import httpx
from fastapi import BackgroundTasks
from app.core.config import settings
from app.schemas.analysis import AnalysisCreate
from app.schemas.project import ProjectCreate
from app.services.analysis_service import start_analysis
from app.services.project_service import create_project
from app.repositories.project_repository import project_repo

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
        
    analysis_in = AnalysisCreate(
        prId=str(pr_number),
        commitSha=commit_sha
    )
    
    await start_analysis(project.projectId, analysis_in, background_tasks)
""",

    "app/services/cloudwatch_service.py": """import boto3
from datetime import datetime, timedelta, timezone
from app.core.config import settings

class CloudWatchService:
    def __init__(self):
        if not settings.LOCAL_MODE:
            self.client = boto3.client('cloudwatch', region_name=settings.AWS_REGION)

    def get_lambda_metrics(self, function_name: str) -> dict:
        if settings.LOCAL_MODE:
            return {"invocations": 1500, "errors": 2, "duration_avg_ms": 120, "insufficient_evidence": False}
            
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=7)
        
        try:
            response = self.client.get_metric_data(
                MetricDataQueries=[
                    {
                        'Id': 'invocations',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': 'AWS/Lambda',
                                'MetricName': 'Invocations',
                                'Dimensions': [{'Name': 'FunctionName', 'Value': function_name}]
                            },
                            'Period': 86400 * 7,
                            'Stat': 'Sum'
                        }
                    }
                ],
                StartTime=start_time,
                EndTime=end_time
            )
            
            total_invocations = sum(response['MetricDataResults'][0]['Values']) if response.get('MetricDataResults') and response['MetricDataResults'][0].get('Values') else 0
            return {"invocations": total_invocations, "insufficient_evidence": False}
        except Exception as e:
            return {"error": str(e), "insufficient_evidence": True}

cloudwatch_service = CloudWatchService()
""",

    "app/workers/analysis_worker.py": """from app.repositories.analysis_repository import analysis_repo
from app.services.ai_service import analyze_impact
from app.services.github_service import get_pr_files
from app.services.cloudwatch_service import cloudwatch_service
import asyncio
from datetime import datetime, timezone

async def run_analysis(analysis_id: str):
    analysis = await analysis_repo.get(analysis_id)
    if not analysis:
        return
        
    analysis.status = "RUNNING"
    analysis.updatedAt = datetime.now(timezone.utc)
    await analysis_repo.save(analysis)
    
    try:
        # 1. Fetch GitHub PR Files
        pr_data = await get_pr_files(analysis.repo, int(analysis.prId))
        analysis.changedFiles = pr_data.get("changed_files", [])
        
        # 2. Map Affected Resources (Mock mapping for MVP)
        function_name = f"{analysis.repo.split('/')[-1]}-main-func"
        analysis.affectedResources = [f"arn:aws:lambda:region:account:function:{function_name}"]
        
        # 3. Collect AWS Evidence
        cw_evidence = cloudwatch_service.get_lambda_metrics(function_name)
        
        # 4. AI Service
        ai_payload = {
            "changed_files": analysis.changedFiles,
            "additions": pr_data.get("additions", 0),
            "deletions": pr_data.get("deletions", 0),
            "aws_evidence": cw_evidence
        }
        
        ai_response = await analyze_impact(ai_payload)
        
        analysis.forecast = ai_response.get("forecast")
        analysis.confidence = ai_response.get("confidence")
        
        evidence = ai_response.get("evidence", [])
        evidence.append({"source": "cloudwatch", "metrics": cw_evidence})
        analysis.evidence = evidence
        
        analysis.assumptions = ai_response.get("assumptions")
        analysis.recommendations = ai_response.get("recommendations")
        
        analysis.status = "COMPLETED"
        
    except Exception as e:
        analysis.status = "FAILED"
        analysis.error = str(e)
        
    analysis.completedAt = datetime.now(timezone.utc)
    analysis.updatedAt = datetime.now(timezone.utc)
    await analysis_repo.save(analysis)
""",
    
    "tests/unit/test_github.py": """def test_github_webhook(client):
    payload = {
        "action": "opened",
        "pull_request": {
            "number": 123,
            "head": {"sha": "abcdef123"}
        },
        "repository": {
            "full_name": "test/webhook-repo",
            "owner": {"login": "test_user"}
        }
    }
    res = client.post("/github/webhook", json=payload)
    assert res.status_code == 200
    assert res.json() == {"status": "received"}
""",
    "tests/unit/test_dynamodb.py": """from app.core.config import settings
def test_local_mode_is_true():
    # In tests, we ensure LOCAL_MODE is true to avoid real AWS calls
    assert settings.LOCAL_MODE is True
"""
}

for path, content in files.items():
    full_path = os.path.join(base_dir, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)

print("Phase 2 files updated successfully.")
