import logging

import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

from app.core.config import settings
from app.schemas.analysis import AnalysisResponse, OutcomeResponse

logger = logging.getLogger(__name__)

class AnalysisRepository:
    def __init__(self):
        self.analyses: dict[str, AnalysisResponse] = {}
        self.outcomes: dict[str, OutcomeResponse] = {}
        if settings.LIVE_AWS:
            self.dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
            self.analyses_table = self.dynamodb.Table(settings.DYNAMODB_ANALYSES_TABLE)
            self.outcomes_table = self.dynamodb.Table(settings.DYNAMODB_AUDIT_TABLE)

    async def save(self, analysis: AnalysisResponse):
        if not settings.LIVE_AWS:
            self.analyses[analysis.analysisId] = analysis
        else:
            try:
                self.analyses_table.put_item(Item=analysis.model_dump(mode='json'))
            except ClientError as e:
                logger.error(f"DynamoDB Error: {e}")
                raise

    async def get(self, analysis_id: str) -> AnalysisResponse | None:
        if not settings.LIVE_AWS:
            return self.analyses.get(analysis_id)
        else:
            try:
                response = self.analyses_table.get_item(Key={'analysisId': analysis_id})
                item = response.get('Item')
                return AnalysisResponse(**item) if item else None
            except ClientError as e:
                logger.error(f"DynamoDB Error: {e}")
                return None
        
    async def get_by_project(self, project_id: str) -> list[dict]:
        res = []
        if not settings.LIVE_AWS:
            analyses_list = [a for a in self.analyses.values() if a.projectId == project_id]
            for a in analyses_list:
                out = self.outcomes.get(a.analysisId)
                res.append({"analysis": a.model_dump(), "outcome": out.model_dump() if out else None})
        else:
            try:
                response = self.analyses_table.scan(FilterExpression=Attr('projectId').eq(project_id))
                items = response.get('Items', [])
                for item in items:
                    a = AnalysisResponse(**item)
                    out_resp = self.outcomes_table.get_item(Key={'analysisId': a.analysisId})
                    out_item = out_resp.get('Item')
                    res.append({
                        "analysis": a.model_dump(),
                        "outcome": OutcomeResponse(**out_item).model_dump() if out_item else None
                    })
            except ClientError as e:
                logger.error(f"DynamoDB Error: {e}")
        return res
        
    async def save_outcome(self, outcome: OutcomeResponse):
        if not settings.LIVE_AWS:
            self.outcomes[outcome.analysisId] = outcome
        else:
            try:
                self.outcomes_table.put_item(Item=outcome.model_dump(mode='json'))
            except ClientError as e:
                logger.error(f"DynamoDB Error: {e}")
                raise

analysis_repo = AnalysisRepository()
