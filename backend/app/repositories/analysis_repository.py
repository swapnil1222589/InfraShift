"""Analysis repository — local in-memory + DynamoDB implementations."""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod

import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

from app.core.config import settings
from app.models.analysis import AnalysisModel

logger = logging.getLogger(__name__)


class BaseAnalysisRepository(ABC):
    """Abstract analysis repository interface."""

    @abstractmethod
    async def save(self, analysis: AnalysisModel) -> None: ...

    @abstractmethod
    async def get(self, analysis_id: str) -> AnalysisModel | None: ...

    @abstractmethod
    async def get_by_project(self, project_id: str) -> list[AnalysisModel]: ...

    @abstractmethod
    async def find_duplicate(self, project_id: str, pr_number: int, commit_sha: str) -> AnalysisModel | None: ...


class LocalAnalysisRepository(BaseAnalysisRepository):
    """In-memory analysis repository for local/test mode."""

    def __init__(self) -> None:
        self._store: dict[str, AnalysisModel] = {}

    async def save(self, analysis: AnalysisModel) -> None:
        self._store[analysis.analysis_id] = analysis

    async def get(self, analysis_id: str) -> AnalysisModel | None:
        return self._store.get(analysis_id)

    async def get_by_project(self, project_id: str) -> list[AnalysisModel]:
        return [a for a in self._store.values() if a.project_id == project_id]

    async def find_duplicate(
        self, project_id: str, pr_number: int, commit_sha: str
    ) -> AnalysisModel | None:
        for a in self._store.values():
            if (
                a.project_id == project_id
                and a.pr_number == pr_number
                and a.commit_sha == commit_sha
            ):
                return a
        return None

    def clear(self) -> None:
        """Clear all data — for tests."""
        self._store.clear()


class DynamoDBAnalysisRepository(BaseAnalysisRepository):
    """DynamoDB-backed analysis repository."""

    def __init__(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name=settings.AWS_REGION)
        self._table = dynamodb.Table(settings.DYNAMODB_ANALYSES_TABLE)

    async def save(self, analysis: AnalysisModel) -> None:
        try:
            self._table.put_item(Item=analysis.model_dump(mode="json"))
        except ClientError as exc:
            code = exc.response["Error"]["Code"]
            logger.error("DynamoDB put_item failed [%s]: %s", code, exc)
            raise

    async def get(self, analysis_id: str) -> AnalysisModel | None:
        try:
            resp = self._table.get_item(Key={"analysis_id": analysis_id})
            item = resp.get("Item")
            return AnalysisModel(**item) if item else None
        except ClientError as exc:
            code = exc.response["Error"]["Code"]
            logger.error("DynamoDB get_item failed [%s]: %s", code, exc)
            return None

    async def get_by_project(self, project_id: str) -> list[AnalysisModel]:
        try:
            resp = self._table.scan(FilterExpression=Attr("project_id").eq(project_id))
            return [AnalysisModel(**item) for item in resp.get("Items", [])]
        except ClientError as exc:
            code = exc.response["Error"]["Code"]
            logger.error("DynamoDB scan failed [%s]: %s", code, exc)
            return []

    async def find_duplicate(
        self, project_id: str, pr_number: int, commit_sha: str
    ) -> AnalysisModel | None:
        try:
            resp = self._table.scan(
                FilterExpression=(
                    Attr("project_id").eq(project_id)
                    & Attr("pr_number").eq(pr_number)
                    & Attr("commit_sha").eq(commit_sha)
                )
            )
            items = resp.get("Items", [])
            return AnalysisModel(**items[0]) if items else None
        except ClientError as exc:
            code = exc.response["Error"]["Code"]
            logger.error("DynamoDB scan failed [%s]: %s", code, exc)
            return None


def create_analysis_repository() -> BaseAnalysisRepository:
    if settings.LIVE_AWS:
        return DynamoDBAnalysisRepository()
    return LocalAnalysisRepository()


analysis_repository: BaseAnalysisRepository = create_analysis_repository()
