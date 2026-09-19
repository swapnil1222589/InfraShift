from unittest.mock import MagicMock, patch

from app.core.config import settings
from app.services.cloudwatch_service import cloudwatch_service


def test_cloudwatch_mock_mode():
    res = cloudwatch_service.get_metrics('AWS/Lambda', 'Invocations', [])
    assert res["is_mock"] is True
    assert res["value"] == 1500

@patch('boto3.client')
def test_cloudwatch_real_mode_success(mock_boto_client):
    # Temporarily set LIVE_AWS = True
    settings.LIVE_AWS = True
    
    # Mock boto response
    mock_client_instance = MagicMock()
    mock_boto_client.return_value = mock_client_instance
    mock_client_instance.get_metric_data.return_value = {
        "MetricDataResults": [{"Values": [10, 20, 30]}]
    }
    
    # Instantiate a new service to pick up LOCAL_MODE = False
    from app.services.cloudwatch_service import CloudWatchService
    cw_service = CloudWatchService()
    
    res = cw_service.get_metrics('AWS/Lambda', 'Invocations', [])
    assert res["is_mock"] is False
    assert res["value"] == 60
    assert res["insufficient_evidence"] is False
    
    # Reset
    settings.LIVE_AWS = False
