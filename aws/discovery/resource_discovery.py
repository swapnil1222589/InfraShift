"""
AWS Resource Discovery Orchestrator.
Discovers resources across API Gateway, Lambda, and DynamoDB in the target environment.
"""

import logging
from typing import List, Optional
from aws.config.aws_config import AWSClientFactory, AWSConfig
from aws.models.aws_models import NormalizedResource
from aws.discovery.lambda_discovery import LambdaDiscovery
from aws.discovery.dynamodb_discovery import DynamoDBDiscovery
from aws.discovery.api_gateway_discovery import APIGatewayDiscovery

logger = logging.getLogger("infrashift.aws.discovery")


class ResourceDiscovery:
    """Unified entry point for discovering all target AWS resources."""

    def __init__(self, client_factory: Optional[AWSClientFactory] = None, config: Optional[AWSConfig] = None):
        if client_factory:
            self.factory = client_factory
        else:
            self.factory = AWSClientFactory(config=config or AWSConfig())

        self.lambda_discovery = LambdaDiscovery(self.factory)
        self.dynamodb_discovery = DynamoDBDiscovery(self.factory)
        self.api_gateway_discovery = APIGatewayDiscovery(self.factory)

    def discover_all(self) -> List[NormalizedResource]:
        """
        Run discovery across API Gateway, Lambda, and DynamoDB.
        Returns a unified list of NormalizedResource instances.
        """
        logger.info("Starting AWS resource discovery in region: %s", self.factory.config.region_name)
        resources: List[NormalizedResource] = []

        # 1. Discover API Gateways
        try:
            apis = self.api_gateway_discovery.discover_all()
            logger.info("Discovered %d API Gateway resources.", len(apis))
            resources.extend(apis)
        except Exception as e:
            logger.error("API Gateway discovery encountered an error: %s", e)

        # 2. Discover Lambda Functions
        try:
            lambdas = self.lambda_discovery.discover_all()
            logger.info("Discovered %d Lambda functions.", len(lambdas))
            resources.extend(lambdas)
        except Exception as e:
            logger.error("Lambda discovery encountered an error: %s", e)

        # 3. Discover DynamoDB Tables
        try:
            tables = self.dynamodb_discovery.discover_all()
            logger.info("Discovered %d DynamoDB tables.", len(tables))
            resources.extend(tables)
        except Exception as e:
            logger.error("DynamoDB discovery encountered an error: %s", e)

        logger.info("Total discovered AWS resources: %d", len(resources))
        return resources
