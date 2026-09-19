import uuid
from datetime import UTC, datetime

from app.repositories.analysis_repository import analysis_repo
from app.repositories.project_repository import project_repo
from app.schemas.project import ProjectCreate, ProjectResponse


async def create_project(project_in: ProjectCreate) -> ProjectResponse:
    project_id = f"proj_{uuid.uuid4().hex[:8]}"
    now = datetime.now(UTC)
    
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
