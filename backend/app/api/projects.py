"""Projects API endpoints."""
from __future__ import annotations

import logging

from fastapi import APIRouter, Request, status

from app.schemas.analysis import AnalysisResponse
from app.schemas.project import ProjectCreate, ProjectResponse
from app.services.analysis_service import get_project_history
from app.services.project_service import create_project, get_project

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
)
async def create_new_project(project_in: ProjectCreate, request: Request) -> ProjectResponse:
    return await create_project(project_in)


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get project by ID",
)
async def read_project(project_id: str, request: Request) -> ProjectResponse:
    return await get_project(project_id)


@router.get(
    "/{project_id}/history",
    response_model=list[AnalysisResponse],
    summary="Get project analysis history",
)
async def read_project_history(project_id: str, request: Request) -> list[AnalysisResponse]:
    # Verify project exists first
    await get_project(project_id)
    return await get_project_history(project_id)
