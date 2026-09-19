"""
Unit tests for AWS Lambda Discovery module.
"""

from unittest.mock import MagicMock
from botocore.exceptions import ClientError
from aws.config.aws_config import AWSClientFactory, AWSConfig
from aws.discovery.lambda_discovery import LambdaDiscovery
from aws.models.aws_models import ResourceType


def test_lambda_discovery_success():
    mock_config = AWSConfig(region_name="ap-south-1")
    mock_client = MagicMock()

    # Mock paginator for list_functions
    mock_paginator = MagicMock()
    mock_paginator.paginate.return_value = [
        {"Functions": [{"FunctionName": "order-processor"}]}
    ]
    mock_client.get_paginator.return_value = mock_paginator

    # Mock get_function response
    mock_client.get_function.return_value = {
        "Configuration": {
            "FunctionArn": "arn:aws:lambda:ap-south-1:123456789012:function:order-processor",
            "FunctionName": "order-processor",
            "Runtime": "python3.12",
            "MemorySize": 256,
            "Timeout": 15,
            "Handler": "index.handler",
            "CodeSize": 1024,
            "LastModified": "2026-09-19T10:00:00.000+0000",
            "Environment": {
                "Variables": {
                    "DB_PASSWORD": "super-secret-password-123",
                    "LOG_LEVEL": "INFO",
                }
            },
            "Role": "arn:aws:iam::123456789012:role/service-role",
            "Architectures": ["x86_64"],
        },
        "Tags": {"Environment": "Production", "Project": "InfraShift"},
    }

    factory = AWSClientFactory(config=mock_config, custom_clients={"lambda": mock_client})
    discovery = LambdaDiscovery(factory)

    results = discovery.discover_all()

    assert len(results) == 1
    res = results[0]

    assert res.resource_name == "order-processor"
    assert res.resource_type == ResourceType.LAMBDA
    assert res.region == "ap-south-1"
    assert res.account_id == "123456789012"
    assert res.tags == {"Environment": "Production", "Project": "InfraShift"}

    # SECURITY CHECK: Secret values MUST NOT be present in metadata
    metadata = res.metadata
    assert "super-secret-password-123" not in str(metadata)
    assert set(metadata["environment_keys"]) == {"DB_PASSWORD", "LOG_LEVEL"}
    assert metadata["runtime"] == "python3.12"
    assert metadata["memory_mb"] == 256
    assert metadata["timeout_seconds"] == 15


def test_lambda_discovery_api_failure():
    mock_config = AWSConfig(region_name="us-east-1")
    mock_client = MagicMock()

    # Simulate AccessDenied ClientError
    error_response = {"Error": {"Code": "AccessDeniedException", "Message": "User not authorized"}}
    mock_client.get_paginator.side_effect = ClientError(error_response, "ListFunctions")

    factory = AWSClientFactory(config=mock_config, custom_clients={"lambda": mock_client})
    discovery = LambdaDiscovery(factory)

    results = discovery.discover_all()

    # Gracefully returns empty list on ClientError without crashing
    assert results == []
