"""Project repository — local in-memory + DynamoDB implementations."""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod

import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

from app.core.config import settings
from app.models.project import ProjectModel

logger = logging.getLogger(__name__)


class BaseProjectRepository(ABC):
    """Abstract project repository interface."""

    @abstractmethod
    async def save(self, project: ProjectModel) -> None: ...

    @abstractmethod
    async def get(self, project_id: str) -> ProjectModel | None: ...

    @abstractmethod
    async def get_by_repo_url(self, repo_url: str) -> ProjectModel | None: ...

    @abstractmethod
    async def list_all(self) -> list[ProjectModel]: ...


class LocalProjectRepository(BaseProjectRepository):
    """In-memory project repository for local/test mode."""

    def __init__(self) -> None:
        self._store: dict[str, ProjectModel] = {}

    async def save(self, project: ProjectModel) -> None:
        self._store[project.project_id] = project

    async def get(self, project_id: str) -> ProjectModel | None:
        return self._store.get(project_id)

    async def get_by_repo_url(self, repo_url: str) -> ProjectModel | None:
        for p in self._store.values():
            if p.repo_url == repo_url:
                return p
        return None

    async def list_all(self) -> list[ProjectModel]:
        return list(self._store.values())

    def clear(self) -> None:
        """Clear all data — for tests."""
        self._store.clear()


class DynamoDBProjectRepository(BaseProjectRepository):
    """DynamoDB-backed project repository."""

    def __init__(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name=settings.AWS_REGION)
        self._table = dynamodb.Table(settings.DYNAMODB_PROJECTS_TABLE)

    async def save(self, project: ProjectModel) -> None:
        try:
            self._table.put_item(Item=project.model_dump(mode="json"))
        except ClientError as exc:
            code = exc.response["Error"]["Code"]
            logger.error("DynamoDB put_item failed [%s]: %s", code, exc)
            raise

    async def get(self, project_id: str) -> ProjectModel | None:
        try:
            resp = self._table.get_item(Key={"project_id": project_id})
            item = resp.get("Item")
            return ProjectModel(**item) if item else None
        except ClientError as exc:
            code = exc.response["Error"]["Code"]
            logger.error("DynamoDB get_item failed [%s]: %s", code, exc)
            return None

    async def get_by_repo_url(self, repo_url: str) -> ProjectModel | None:
        try:
            resp = self._table.scan(FilterExpression=Attr("repo_url").eq(repo_url))
            items = resp.get("Items", [])
            return ProjectModel(**items[0]) if items else None
        except ClientError as exc:
            code = exc.response["Error"]["Code"]
            logger.error("DynamoDB scan failed [%s]: %s", code, exc)
            return None

    async def list_all(self) -> list[ProjectModel]:
        try:
            resp = self._table.scan()
            return [ProjectModel(**item) for item in resp.get("Items", [])]
        except ClientError as exc:
            code = exc.response["Error"]["Code"]
            logger.error("DynamoDB scan failed [%s]: %s", code, exc)
            return []


def create_project_repository() -> BaseProjectRepository:
    """Factory: return the correct repository based on configuration."""
    if settings.LIVE_AWS:
        return DynamoDBProjectRepository()
    return LocalProjectRepository()


# Module-level singleton (re-created on import, so tests can reset)
project_repository: BaseProjectRepository = create_project_repository()
