import logging

import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

from app.core.config import settings
from app.schemas.project import ProjectResponse

logger = logging.getLogger(__name__)

class ProjectRepository:
    def __init__(self):
        self.db: dict[str, ProjectResponse] = {}
        if settings.LIVE_AWS:
            self.dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
            self.table = self.dynamodb.Table(settings.DYNAMODB_PROJECTS_TABLE)

    async def save(self, project: ProjectResponse):
        if not settings.LIVE_AWS:
            self.db[project.projectId] = project
        else:
            try:
                self.table.put_item(Item=project.model_dump(mode='json'))
            except ClientError as e:
                logger.error(f"DynamoDB Error: {e}")
                raise

    async def get(self, project_id: str) -> ProjectResponse | None:
        if not settings.LIVE_AWS:
            return self.db.get(project_id)
        else:
            try:
                response = self.table.get_item(Key={'projectId': project_id})
                item = response.get('Item')
                return ProjectResponse(**item) if item else None
            except ClientError as e:
                logger.error(f"DynamoDB Error: {e}")
                return None

    async def get_by_repo(self, repo: str) -> ProjectResponse | None:
        if not settings.LIVE_AWS:
            for p in self.db.values():
                if p.repo == repo:
                    return p
            return None
        else:
            try:
                response = self.table.scan(FilterExpression=Attr('repo').eq(repo))
                items = response.get('Items', [])
                return ProjectResponse(**items[0]) if items else None
            except ClientError as e:
                logger.error(f"DynamoDB Error: {e}")
                return None

project_repo = ProjectRepository()
