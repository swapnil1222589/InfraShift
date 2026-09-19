"""Audit event repository."""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings
from app.models.audit import AuditEventModel

logger = logging.getLogger(__name__)


class BaseAuditRepository(ABC):
    @abstractmethod
    async def save(self, event: AuditEventModel) -> None: ...

    @abstractmethod
    async def get_by_analysis(self, analysis_id: str) -> list[AuditEventModel]: ...


class LocalAuditRepository(BaseAuditRepository):
    def __init__(self) -> None:
        self._store: list[AuditEventModel] = []

    async def save(self, event: AuditEventModel) -> None:
        self._store.append(event)

    async def get_by_analysis(self, analysis_id: str) -> list[AuditEventModel]:
        return [e for e in self._store if e.analysis_id == analysis_id]

    def clear(self) -> None:
        self._store.clear()


class DynamoDBAuditRepository(BaseAuditRepository):
    def __init__(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name=settings.AWS_REGION)
        self._table = dynamodb.Table(settings.DYNAMODB_AUDIT_TABLE)

    async def save(self, event: AuditEventModel) -> None:
        try:
            self._table.put_item(Item=event.model_dump(mode="json"))
        except ClientError as exc:
            code = exc.response["Error"]["Code"]
            logger.error("DynamoDB audit put_item failed [%s]: %s", code, exc)
            raise

    async def get_by_analysis(self, analysis_id: str) -> list[AuditEventModel]:
        try:
            from boto3.dynamodb.conditions import Attr  # noqa: PLC0415

            resp = self._table.scan(FilterExpression=Attr("analysis_id").eq(analysis_id))
            return [AuditEventModel(**item) for item in resp.get("Items", [])]
        except ClientError as exc:
            code = exc.response["Error"]["Code"]
            logger.error("DynamoDB scan failed [%s]: %s", code, exc)
            return []


def create_audit_repository() -> BaseAuditRepository:
    if settings.LIVE_AWS:
        return DynamoDBAuditRepository()
    return LocalAuditRepository()


audit_repository: BaseAuditRepository = create_audit_repository()
