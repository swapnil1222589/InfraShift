import uuid
from datetime import UTC, datetime

from fastapi import BackgroundTasks

from app.repositories.analysis_repository import analysis_repo
from app.repositories.project_repository import project_repo
from app.schemas.analysis import (
    AnalysisCreate,
    AnalysisResponse,
    OutcomeCreate,
    OutcomeResponse,
)
from app.workers.analysis_worker import run_analysis


async def start_analysis(project_id: str, analysis_in: AnalysisCreate, background_tasks: BackgroundTasks) -> AnalysisResponse:
    project = await project_repo.get(project_id)
    analysis_id = f"analysis_{uuid.uuid4().hex[:8]}"
    now = datetime.now(UTC)
    
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
    now = datetime.now(UTC)
    
    outcome = OutcomeResponse(
        analysisId=analysis_id,
        timestamp=now,
        forecastCost=analysis.forecast.get("costRange", "unknown") if analysis.forecast else "unknown",
        forecastPerformance=analysis.forecast.get("performanceRange", "unknown") if analysis.forecast else "unknown",
        **outcome_in.model_dump()
    )
    await analysis_repo.save_outcome(outcome)
    return outcome
