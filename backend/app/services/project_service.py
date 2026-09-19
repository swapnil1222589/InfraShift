"""Project service — business logic layer."""
from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime

from app.core.errors import ConflictError, NotFoundError
from app.models.project import ProjectModel
from app.repositories.project_repository import project_repository
from app.schemas.project import ProjectCreate, ProjectResponse

logger = logging.getLogger(__name__)


def _model_to_response(model: ProjectModel) -> ProjectResponse:
    return ProjectResponse(
        project_id=model.project_id,
        name=model.name,
        repo_url=model.repo_url,
        default_branch=model.default_branch,
        aws_region=model.aws_region,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


async def create_project(project_in: ProjectCreate) -> ProjectResponse:
    """Create a new project. Raises ConflictError if repo_url already exists."""
    existing = await project_repository.get_by_repo_url(project_in.repo_url)
    if existing:
        raise ConflictError(
            f"A project for repository '{project_in.repo_url}' already exists",
            error_code="PROJECT_ALREADY_EXISTS",
        )

    now = datetime.now(UTC)
    project = ProjectModel(
        project_id=str(uuid.uuid4()),
        name=project_in.name,
        repo_url=project_in.repo_url,
        default_branch=project_in.default_branch,
        aws_region=project_in.aws_region,
        created_at=now,
        updated_at=now,
    )

    await project_repository.save(project)
    logger.info("Project created: project_id=%s repo_url=%s", project.project_id, project.repo_url)
    return _model_to_response(project)


async def get_project(project_id: str) -> ProjectResponse:
    """Get project by ID. Raises NotFoundError if not found."""
    model = await project_repository.get(project_id)
    if not model:
        raise NotFoundError(f"Project not found: {project_id}", error_code="PROJECT_NOT_FOUND")
    return _model_to_response(model)


async def get_project_or_none(project_id: str) -> ProjectResponse | None:
    model = await project_repository.get(project_id)
    return _model_to_response(model) if model else None


async def get_or_create_project_by_repo(
    repo_url: str,
    name: str,
) -> ProjectResponse:
    """Get existing project by repo URL or create a new one."""
    existing = await project_repository.get_by_repo_url(repo_url)
    if existing:
        return _model_to_response(existing)

    project_in = ProjectCreate(
        name=name,
        repo_url=repo_url,
        default_branch="main",
        aws_region="us-east-1",
    )
    return await create_project(project_in)
