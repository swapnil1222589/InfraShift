"""
Unit tests for AWS API Gateway Discovery module.
"""

from unittest.mock import MagicMock
from botocore.exceptions import ClientError
from aws.config.aws_config import AWSClientFactory, AWSConfig
from aws.discovery.api_gateway_discovery import APIGatewayDiscovery
from aws.models.aws_models import ResourceType


def test_api_gateway_v1_discovery():
    mock_config = AWSConfig(region_name="eu-west-1")
    v1_client = MagicMock()
    v2_client = MagicMock()

    # Mock v1 REST API response
    paginator = MagicMock()
    paginator.paginate.return_value = [
        {"items": [{"id": "restapi123", "name": "order-service-api", "endpointConfiguration": {"types": ["REGIONAL"]}}]}
    ]
    v1_client.get_paginator.return_value = paginator

    v1_client.get_stages.return_value = {"item": [{"stageName": "prod"}, {"stageName": "dev"}]}
    v1_client.get_resources.return_value = {"items": [{"path": "/"}, {"path": "/orders"}]}

    # Mock empty v2 APIs
    v2_client.get_apis.return_value = {"Items": []}

    factory = AWSClientFactory(
        config=mock_config,
        custom_clients={"apigateway": v1_client, "apigatewayv2": v2_client},
    )
    discovery = APIGatewayDiscovery(factory)

    results = discovery.discover_all()

    assert len(results) == 1
    res = results[0]

    assert res.resource_name == "order-service-api"
    assert res.resource_type == ResourceType.API_GATEWAY
    assert res.region == "eu-west-1"

    metadata = res.metadata
    assert metadata["api_id"] == "restapi123"
    assert metadata["api_type"] == "REST"
    assert metadata["stages"] == ["prod", "dev"]
    assert metadata["routes_or_resources"] == ["/", "/orders"]


def test_api_gateway_v2_discovery():
    mock_config = AWSConfig(region_name="us-east-1")
    v1_client = MagicMock()
    v2_client = MagicMock()

    # Mock empty v1 APIs
    v1_paginator = MagicMock()
    v1_paginator.paginate.return_value = [{"items": []}]
    v1_client.get_paginator.return_value = v1_paginator

    # Mock v2 HTTP API
    v2_client.get_apis.return_value = {
        "Items": [
            {
                "ApiId": "httpapi456",
                "Name": "user-service-http",
                "ProtocolType": "HTTP",
                "ApiEndpoint": "https://httpapi456.execute-api.us-east-1.amazonaws.com",
            }
        ]
    }
    v2_client.get_stages.return_value = {"Items": [{"StageName": "$default"}]}
    v2_client.get_routes.return_value = {"Items": [{"RouteKey": "GET /users"}, {"RouteKey": "POST /users"}]}

    factory = AWSClientFactory(
        config=mock_config,
        custom_clients={"apigateway": v1_client, "apigatewayv2": v2_client},
    )
    discovery = APIGatewayDiscovery(factory)

    results = discovery.discover_all()

    assert len(results) == 1
    res = results[0]

    assert res.resource_name == "user-service-http"
    assert res.resource_type == ResourceType.API_GATEWAY

    metadata = res.metadata
    assert metadata["api_id"] == "httpapi456"
    assert metadata["stages"] == ["$default"]
    assert metadata["routes_or_resources"] == ["GET /users", "POST /users"]


def test_api_gateway_discovery_error_handling():
    mock_config = AWSConfig(region_name="ap-south-1")
    v1_client = MagicMock()
    v2_client = MagicMock()

    error_response = {"Error": {"Code": "AccessDeniedException", "Message": "Not authorized"}}
    v1_client.get_paginator.side_effect = ClientError(error_response, "GetRestApis")
    v2_client.get_apis.side_effect = ClientError(error_response, "GetApis")

    factory = AWSClientFactory(
        config=mock_config,
        custom_clients={"apigateway": v1_client, "apigatewayv2": v2_client},
    )
    discovery = APIGatewayDiscovery(factory)

    results = discovery.discover_all()
    assert results == []
