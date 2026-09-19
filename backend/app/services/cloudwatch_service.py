import logging
from datetime import UTC, datetime, timedelta

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings

logger = logging.getLogger(__name__)

class CloudWatchService:
    def __init__(self):
        if settings.LIVE_AWS:
            self.client = boto3.client('cloudwatch', region_name=settings.AWS_REGION)

    def get_metrics(self, namespace: str, metric_name: str, dimensions: list, days: int = 7) -> dict:
        if not settings.LIVE_AWS:
            return {
                "metric": metric_name,
                "value": 1500,
                "is_mock": True,
                "insufficient_evidence": False
            }
            
        end_time = datetime.now(UTC)
        start_time = end_time - timedelta(days=days)
        
        try:
            response = self.client.get_metric_data(
                MetricDataQueries=[
                    {
                        'Id': 'query1',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': namespace,
                                'MetricName': metric_name,
                                'Dimensions': dimensions
                            },
                            'Period': 86400 * days,
                            'Stat': 'Sum'
                        }
                    }
                ],
                StartTime=start_time,
                EndTime=end_time
            )
            
            values = response.get('MetricDataResults', [{}])[0].get('Values', [])
            total = sum(values) if values else 0
            
            return {
                "metric": metric_name,
                "value": total,
                "is_mock": False,
                "insufficient_evidence": len(values) == 0
            }
        except ClientError as e:
            logger.error(f"CloudWatch Error: {e}")
            return {"error": str(e), "insufficient_evidence": True, "is_mock": False}

cloudwatch_service = CloudWatchService()
