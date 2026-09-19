"""
Unit tests for AWS DynamoDB Discovery module.
"""

from unittest.mock import MagicMock
from botocore.exceptions import ClientError
from aws.config.aws_config import AWSClientFactory, AWSConfig
from aws.discovery.dynamodb_discovery import DynamoDBDiscovery
from aws.models.aws_models import ResourceType


def test_dynamodb_discovery_success():
    mock_config = AWSConfig(region_name="ap-south-1")
    mock_client = MagicMock()

    # Mock paginator for list_tables
    mock_paginator = MagicMock()
    mock_paginator.paginate.return_value = [{"TableNames": ["Payments"]}]
    mock_client.get_paginator.return_value = mock_paginator

    # Mock describe_table response
    mock_client.describe_table.return_value = {
        "Table": {
            "TableArn": "arn:aws:dynamodb:ap-south-1:123456789012:table/Payments",
            "TableName": "Payments",
            "TableStatus": "ACTIVE",
            "BillingModeSummary": {"BillingMode": "PAY_PER_REQUEST"},
            "ItemCount": 8500,
            "TableSizeBytes": 102400,
            "KeySchema": [
                {"AttributeName": "payment_id", "KeyType": "HASH"},
                {"AttributeName": "created_at", "KeyType": "RANGE"},
            ],
            "GlobalSecondaryIndexes": [{"IndexName": "UserPaymentsIndex"}],
            "CreationDateTime": 1700000000.0,
        }
    }

    factory = AWSClientFactory(config=mock_config, custom_clients={"dynamodb": mock_client})
    discovery = DynamoDBDiscovery(factory)

    results = discovery.discover_all()

    assert len(results) == 1
    res = results[0]

    assert res.resource_name == "Payments"
    assert res.resource_type == ResourceType.DYNAMODB
    assert res.region == "ap-south-1"
    assert res.account_id == "123456789012"

    metadata = res.metadata
    assert metadata["table_name"] == "Payments"
    assert metadata["table_status"] == "ACTIVE"
    assert metadata["billing_mode"] == "PAY_PER_REQUEST"
    assert metadata["item_count"] == 8500
    assert metadata["partition_key"] == "payment_id"
    assert metadata["sort_key"] == "created_at"
    assert metadata["global_secondary_indexes_count"] == 1


def test_dynamodb_discovery_api_failure():
    mock_config = AWSConfig(region_name="us-west-2")
    mock_client = MagicMock()

    error_response = {"Error": {"Code": "ResourceNotFoundException", "Message": "Requested table not found"}}
    mock_client.get_paginator.side_effect = ClientError(error_response, "ListTables")

    factory = AWSClientFactory(config=mock_config, custom_clients={"dynamodb": mock_client})
    discovery = DynamoDBDiscovery(factory)

    results = discovery.discover_all()
    assert results == []
