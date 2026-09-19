import os

base_dir = r"C:\Users\swapn\.gemini\antigravity\scratch\infrashift-backend\backend"

files = {
    "requirements.txt": """fastapi>=0.100.0
uvicorn>=0.23.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
boto3>=1.28.0
python-dotenv>=1.0.0
pytest>=7.4.0
pytest-asyncio>=0.21.0
ruff>=0.0.280
httpx>=0.24.1
""",
    ".env.example": """APP_ENV=development
LOCAL_MODE=true
MOCK_AI=true
MOCK_GITHUB=true

AWS_REGION=us-east-1

GITHUB_TOKEN=
GITHUB_WEBHOOK_SECRET=

DYNAMODB_PROJECTS_TABLE=infrashift-projects
DYNAMODB_ANALYSES_TABLE=infrashift-analyses
DYNAMODB_AUDIT_TABLE=infrashift-audit-events

S3_BUCKET=
AI_SERVICE_URL=
""",
    "app/__init__.py": "",
    "app/main.py": """from fastapi import FastAPI
from app.api import health, projects, analyses, github
from app.core.config import settings

app = FastAPI(
    title="InfraShift Backend",
    description="Backend API for InfraShift MVP",
    version="1.0.0",
)

app.include_router(health.router, tags=["Health"])
app.include_router(projects.router, prefix="/projects", tags=["Projects"])
app.include_router(analyses.router, prefix="/analyses", tags=["Analyses"])
app.include_router(github.router, prefix="/github", tags=["GitHub"])
""",
    "app/core/__init__.py": "",
    "app/core/config.py": """from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ENV: str = "development"
    LOCAL_MODE: bool = True
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
    "app/schemas/__init__.py": "",
    "app/schemas/common.py": """from pydantic import BaseModel
from typing import Optional

class ErrorResponse(BaseModel):
    code: str
    message: str
    requestId: Optional[str] = None
""",
    "app/schemas/project.py": """from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProjectCreate(BaseModel):
    repo: str
    environment: str
    owner: str
    awsEnvironment: str

class ProjectResponse(ProjectCreate):
    projectId: str
    createdAt: datetime
    updatedAt: datetime
""",
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
""",
    "app/api/__init__.py": "",
    "app/api/health.py": """from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy"}
""",
    "app/api/projects.py": """from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.schemas.project import ProjectCreate, ProjectResponse
from app.services.project_service import create_project, get_project, get_project_history
from app.schemas.analysis import AnalysisCreate, AnalysisResponse
from app.services.analysis_service import start_analysis

router = APIRouter()

@router.post("", response_model=ProjectResponse)
async def create_new_project(project: ProjectCreate):
    return await create_project(project)

@router.get("/{project_id}", response_model=ProjectResponse)
async def read_project(project_id: str):
    proj = await get_project(project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    return proj

@router.post("/{project_id}/analyses", response_model=AnalysisResponse)
async def create_analysis(project_id: str, analysis: AnalysisCreate, background_tasks: BackgroundTasks):
    proj = await get_project(project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Start analysis logic
    return await start_analysis(project_id, analysis, background_tasks)

@router.get("/{project_id}/history")
async def read_project_history(project_id: str):
    return await get_project_history(project_id)
""",
    "app/api/analyses.py": """from fastapi import APIRouter, HTTPException
from app.schemas.analysis import AnalysisResponse, OutcomeCreate, OutcomeResponse
from app.services.analysis_service import get_analysis, record_outcome

router = APIRouter()

@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def read_analysis(analysis_id: str):
    analysis = await get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis

@router.get("/{analysis_id}/impact")
async def get_impact(analysis_id: str):
    analysis = await get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {
        "analysisId": analysis.analysisId,
        "affectedResources": analysis.affectedResources,
        "changedComponents": analysis.changedFiles,
        "dependencies": []
    }

@router.get("/{analysis_id}/forecast")
async def get_forecast(analysis_id: str):
    analysis = await get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {
        "analysisId": analysis.analysisId,
        **analysis.forecast,
        "evidence": analysis.evidence,
        "assumptions": analysis.assumptions
    }

@router.get("/{analysis_id}/evidence")
async def get_evidence(analysis_id: str):
    analysis = await get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {
        "analysisId": analysis.analysisId,
        "historicalEvidence": [],
        "awsEvidence": analysis.evidence,
        "telemetry": [],
        "dataCoverage": "partial"
    }

@router.get("/{analysis_id}/recommendations")
async def get_recommendations(analysis_id: str):
    analysis = await get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {
        "analysisId": analysis.analysisId,
        "recommendations": analysis.recommendations
    }

@router.post("/{analysis_id}/outcome", response_model=OutcomeResponse)
async def create_outcome(analysis_id: str, outcome: OutcomeCreate):
    return await record_outcome(analysis_id, outcome)
""",
    "app/api/github.py": """from fastapi import APIRouter, Request, HTTPException
import hmac
import hashlib
from app.core.config import settings
from app.services.github_service import process_webhook

router = APIRouter()

@router.post("/webhook")
async def github_webhook(request: Request):
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
    await process_webhook(data)
    return {"status": "received"}
""",
    "app/services/__init__.py": "",
    "app/services/project_service.py": """from app.schemas.project import ProjectCreate, ProjectResponse
from app.repositories.project_repository import project_repo
from app.repositories.analysis_repository import analysis_repo
import uuid
from datetime import datetime, timezone

async def create_project(project_in: ProjectCreate) -> ProjectResponse:
    project_id = f"proj_{uuid.uuid4().hex[:8]}"
    now = datetime.now(timezone.utc)
    
    project = ProjectResponse(
        projectId=project_id,
        createdAt=now,
        updatedAt=now,
        **project_in.model_dump()
    )
    await project_repo.save(project)
    return project

async def get_project(project_id: str) -> ProjectResponse | None:
    return await project_repo.get(project_id)

async def get_project_history(project_id: str):
    return await analysis_repo.get_by_project(project_id)
""",
    "app/services/analysis_service.py": """from app.schemas.analysis import AnalysisCreate, AnalysisResponse, OutcomeCreate, OutcomeResponse
from app.repositories.project_repository import project_repo
from app.repositories.analysis_repository import analysis_repo
from app.workers.analysis_worker import run_analysis
from fastapi import BackgroundTasks
import uuid
from datetime import datetime, timezone

async def start_analysis(project_id: str, analysis_in: AnalysisCreate, background_tasks: BackgroundTasks) -> AnalysisResponse:
    project = await project_repo.get(project_id)
    analysis_id = f"analysis_{uuid.uuid4().hex[:8]}"
    now = datetime.now(timezone.utc)
    
    analysis = AnalysisResponse(
        analysisId=analysis_id,
        projectId=project_id,
        prId=analysis_in.prId,
        repo=project.repo,
        commitSha=analysis_in.commitSha,
        status="PENDING",
        createdAt=now,
        updatedAt=now,
    )
    
    await analysis_repo.save(analysis)
    background_tasks.add_task(run_analysis, analysis_id)
    
    return analysis

async def get_analysis(analysis_id: str) -> AnalysisResponse | None:
    return await analysis_repo.get(analysis_id)
    
async def record_outcome(analysis_id: str, outcome_in: OutcomeCreate) -> OutcomeResponse:
    analysis = await analysis_repo.get(analysis_id)
    now = datetime.now(timezone.utc)
    
    outcome = OutcomeResponse(
        analysisId=analysis_id,
        timestamp=now,
        forecastCost=analysis.forecast.get("costRange", "unknown") if analysis.forecast else "unknown",
        forecastPerformance=analysis.forecast.get("performanceRange", "unknown") if analysis.forecast else "unknown",
        **outcome_in.model_dump()
    )
    await analysis_repo.save_outcome(outcome)
    return outcome
""",
    "app/services/github_service.py": """async def process_webhook(data: dict):
    # Dummy implementation for webhook
    pass
""",
    "app/services/ai_service.py": """from app.core.config import settings

async def analyze_impact(payload: dict) -> dict:
    if settings.MOCK_AI:
        return {
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
    return {}
""",
    "app/workers/__init__.py": "",
    "app/workers/analysis_worker.py": """from app.repositories.analysis_repository import analysis_repo
from app.services.ai_service import analyze_impact
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
        # Simulate work
        await asyncio.sleep(2)
        
        # MOCK details
        analysis.changedFiles = ["src/lambda/handler.py"]
        analysis.affectedResources = ["arn:aws:lambda:region:account:function:my-func"]
        
        ai_response = await analyze_impact({"files": analysis.changedFiles})
        
        analysis.forecast = ai_response.get("forecast")
        analysis.confidence = ai_response.get("confidence")
        analysis.evidence = ai_response.get("evidence")
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
    "app/repositories/__init__.py": "",
    "app/repositories/project_repository.py": """from typing import Dict
from app.schemas.project import ProjectResponse
from app.core.config import settings

class ProjectRepository:
    def __init__(self):
        self.db: Dict[str, ProjectResponse] = {}

    async def save(self, project: ProjectResponse):
        self.db[project.projectId] = project

    async def get(self, project_id: str) -> ProjectResponse | None:
        return self.db.get(project_id)

project_repo = ProjectRepository()
""",
    "app/repositories/analysis_repository.py": """from typing import Dict, List
from app.schemas.analysis import AnalysisResponse, OutcomeResponse
from app.core.config import settings

class AnalysisRepository:
    def __init__(self):
        self.analyses: Dict[str, AnalysisResponse] = {}
        self.outcomes: Dict[str, OutcomeResponse] = {}

    async def save(self, analysis: AnalysisResponse):
        self.analyses[analysis.analysisId] = analysis

    async def get(self, analysis_id: str) -> AnalysisResponse | None:
        return self.analyses.get(analysis_id)
        
    async def get_by_project(self, project_id: str) -> List[dict]:
        res = []
        for a in self.analyses.values():
            if a.projectId == project_id:
                out = self.outcomes.get(a.analysisId)
                res.append({
                    "analysis": a.model_dump(),
                    "outcome": out.model_dump() if out else None
                })
        return res
        
    async def save_outcome(self, outcome: OutcomeResponse):
        self.outcomes[outcome.analysisId] = outcome

analysis_repo = AnalysisRepository()
""",
    "tests/conftest.py": """import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)
""",
    "tests/unit/test_health.py": """def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
""",
    "tests/unit/test_projects.py": """def test_create_project(client):
    response = client.post("/projects", json={
        "repo": "test/repo",
        "environment": "dev",
        "owner": "test",
        "awsEnvironment": "demo"
    })
    assert response.status_code == 200
    data = response.json()
    assert "projectId" in data
    assert data["repo"] == "test/repo"
""",
    "tests/unit/test_analyses.py": """def test_create_and_get_analysis(client):
    # 1. Create project
    proj_res = client.post("/projects", json={
        "repo": "test/repo",
        "environment": "dev",
        "owner": "test",
        "awsEnvironment": "demo"
    })
    project_id = proj_res.json()["projectId"]
    
    # 2. Create analysis
    ana_res = client.post(f"/projects/{project_id}/analyses", json={
        "prId": "123",
        "commitSha": "abc1234"
    })
    assert ana_res.status_code == 200
    analysis_id = ana_res.json()["analysisId"]
    assert ana_res.json()["status"] == "PENDING"
    
    # 3. Get analysis (worker might be running but let's check it's retrievable)
    get_res = client.get(f"/analyses/{analysis_id}")
    assert get_res.status_code == 200
    assert get_res.json()["analysisId"] == analysis_id
""",
    "Dockerfile": """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
""",
    "README.md": """# InfraShift Backend
    
## Running the server
`uvicorn app.main:app --reload`

## Tests
`pytest`

## LOCAL_MODE and MOCK_AI
This uses in-memory DB and mocked AI responses.
"""
}

for path, content in files.items():
    full_path = os.path.join(base_dir, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)
print("Files created.")
