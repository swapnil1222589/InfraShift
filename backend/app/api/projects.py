from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.schemas.analysis import AnalysisCreate, AnalysisResponse
from app.schemas.project import ProjectCreate, ProjectResponse
from app.services.analysis_service import start_analysis
from app.services.project_service import (
    create_project,
    get_project,
    get_project_history,
)

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
