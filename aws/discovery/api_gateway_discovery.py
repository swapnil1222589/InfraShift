import logging
import re
from typing import List, Optional, Dict, Any
from botocore.exceptions import BotoCoreError, ClientError

from aws.config.aws_config import AWSClientFactory
from aws.models.aws_models import (
    NormalizedResource,
    ResourceType,
    APIGatewayMetadata,
    NormalizedDependency,
    EvidenceType,
    ConfidenceLevel,
    RelationshipType,
)

logger = logging.getLogger("infrashift.aws.discovery.api_gateway")


def extract_lambda_arn_from_uri(uri: str) -> Optional[str]:
    """
    Extract canonical Lambda function ARN from API Gateway integration URI.
    Supports formats like:
    arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:123456789012:function:my-function/invocations
    """
    if not uri:
        return None
    if uri.startswith("arn:aws:lambda:"):
        return uri.split("/invocations")[0]
    match = re.search(r"functions/(arn:aws:lambda:[^/]+)", uri)
    if match:
        return match.group(1)
    return None


class APIGatewayDiscovery:
    """Discovers AWS API Gateway resources (both v1 REST and v2 HTTP/WebSocket)."""

    def __init__(self, client_factory: AWSClientFactory):
        self.factory = client_factory

    def get_v1_client(self):
        return self.factory.get_client("apigateway")

    def get_v2_client(self):
        return self.factory.get_client("apigatewayv2")

    def discover_all(self) -> List[NormalizedResource]:
        """
        Discover both v1 (REST) and v2 (HTTP/WebSocket) APIs in the region.
        """
        resources: List[NormalizedResource] = []
        resources.extend(self._discover_v1_rest_apis())
        resources.extend(self._discover_v2_apis())
        return resources

    def discover_dependencies(self) -> List[NormalizedDependency]:
        """
        Discover API Gateway → Lambda route dependencies supported by AWS configuration.
        """
        dependencies: List[NormalizedDependency] = []
        dependencies.extend(self._discover_v1_dependencies())
        dependencies.extend(self._discover_v2_dependencies())
        return dependencies

    def _discover_v1_dependencies(self) -> List[NormalizedDependency]:
        """Discover v1 REST API integrations targeting Lambda functions."""
        dependencies: List[NormalizedDependency] = []
        try:
            client = self.get_v1_client()
            paginator = client.get_paginator("get_rest_apis")

            for page in paginator.paginate():
                for api in page.get("items", []):
                    api_id = api["id"]
                    api_name = api.get("name", api_id)
                    region = self.factory.config.region_name
                    api_arn = f"arn:aws:apigateway:{region}::/restapis/{api_id}"

                    try:
                        res_resp = client.get_resources(restApiId=api_id)
                        for resource in res_resp.get("items", []):
                            resource_path = resource.get("path", "/")
                            methods = resource.get("resourceMethods", {})
                            for method in methods.keys():
                                try:
                                    integ = client.get_integration(
                                        restApiId=api_id,
                                        resourceId=resource["id"],
                                        httpMethod=method,
                                    )
                                    uri = integ.get("uri", "")
                                    target_lambda_arn = extract_lambda_arn_from_uri(uri)
                                    if target_lambda_arn:
                                        dep = NormalizedDependency(
                                            source_resource_id=api_arn,
                                            source_type=ResourceType.API_GATEWAY,
                                            target_resource_id=target_lambda_arn,
                                            target_type=ResourceType.LAMBDA,
                                            relationship=RelationshipType.ROUTES_TO,
                                            evidence_type=EvidenceType.AWS_CONFIGURATION,
                                            confidence=ConfidenceLevel.OBSERVED,
                                            metadata={
                                                "api_id": api_id,
                                                "api_name": api_name,
                                                "route_path": resource_path,
                                                "http_method": method,
                                                "integration_type": integ.get("type"),
                                            },
                                        )
                                        dependencies.append(dep)
                                except (BotoCoreError, ClientError) as e:
                                    logger.debug(
                                        "Could not fetch integration for REST API '%s' resource '%s' method '%s': %s",
                                        api_id,
                                        resource_path,
                                        method,
                                        e,
                                    )
                    except (BotoCoreError, ClientError) as e:
                        logger.warning("Could not list resources for REST API '%s': %s", api_id, e)
        except (BotoCoreError, ClientError) as e:
            logger.error("Failed to discover v1 REST API dependencies: %s", str(e))

        return dependencies

    def _discover_v2_dependencies(self) -> List[NormalizedDependency]:
        """Discover v2 HTTP/WebSocket API integrations targeting Lambda functions."""
        dependencies: List[NormalizedDependency] = []
        try:
            client = self.get_v2_client()
            response = client.get_apis()

            for api in response.get("Items", []):
                api_id = api["ApiId"]
                api_name = api.get("Name", api_id)
                region = self.factory.config.region_name
                api_arn = f"arn:aws:apigateway:{region}::/apis/{api_id}"

                try:
                    integ_resp = client.get_integrations(ApiId=api_id)
                    for integ in integ_resp.get("Items", []):
                        uri = integ.get("IntegrationUri", "")
                        target_lambda_arn = extract_lambda_arn_from_uri(uri)
                        if target_lambda_arn:
                            dep = NormalizedDependency(
                                source_resource_id=api_arn,
                                source_type=ResourceType.API_GATEWAY,
                                target_resource_id=target_lambda_arn,
                                target_type=ResourceType.LAMBDA,
                                relationship=RelationshipType.ROUTES_TO,
                                evidence_type=EvidenceType.AWS_CONFIGURATION,
                                confidence=ConfidenceLevel.OBSERVED,
                                metadata={
                                    "api_id": api_id,
                                    "api_name": api_name,
                                    "integration_id": integ.get("IntegrationId"),
                                    "integration_type": integ.get("IntegrationType"),
                                },
                            )
                            dependencies.append(dep)
                except (BotoCoreError, ClientError) as e:
                    logger.warning("Could not fetch integrations for v2 API '%s': %s", api_id, e)
        except (BotoCoreError, ClientError) as e:
            logger.error("Failed to discover v2 API dependencies: %s", str(e))

        return dependencies

    def _discover_v1_rest_apis(self) -> List[NormalizedResource]:
        """Discover v1 REST APIs using 'apigateway' client."""
        results: List[NormalizedResource] = []
        try:
            client = self.get_v1_client()
            paginator = client.get_paginator("get_rest_apis")

            for page in paginator.paginate():
                for api in page.get("items", []):
                    try:
                        normalized = self.get_v1_api_details(api["id"], api)
                        if normalized:
                            results.append(normalized)
                    except Exception as e:
                        logger.warning("Failed to parse REST API '%s': %s", api.get("id"), e)
        except (BotoCoreError, ClientError) as e:
            logger.error("Failed to list v1 REST APIs: %s", str(e))

        return results

    def get_v1_api_details(self, api_id: str, api_data: Optional[dict] = None) -> Optional[NormalizedResource]:
        """Get details for a v1 REST API."""
        try:
            client = self.get_v1_client()
            if not api_data:
                api_data = client.get_rest_api(restApiId=api_id)

            # Fetch stages
            stages = []
            try:
                stage_resp = client.get_stages(restApiId=api_id)
                stages = [s["stageName"] for s in stage_resp.get("item", [])]
            except Exception:
                pass

            # Fetch resources/paths
            paths = []
            try:
                res_resp = client.get_resources(restApiId=api_id)
                paths = [r.get("path", "/") for r in res_resp.get("items", [])]
            except Exception:
                pass

            types = api_data.get("endpointConfiguration", {}).get("types", ["EDGE"])
            region = self.factory.config.region_name
            arn = f"arn:aws:apigateway:{region}::/restapis/{api_id}"

            metadata = APIGatewayMetadata(
                api_id=api_id,
                api_name=api_data.get("name", api_id),
                api_type="REST",
                protocol_type="REST",
                stages=stages,
                endpoint_types=types,
                routes_or_resources=paths,
                created_date=str(api_data.get("createdDate")),
                endpoint_url=f"https://{api_id}.execute-api.{region}.amazonaws.com",
            )

            return NormalizedResource(
                resource_id=arn,
                resource_type=ResourceType.API_GATEWAY,
                resource_name=api_data.get("name", api_id),
                region=region,
                metadata=metadata.model_dump(),
                tags=api_data.get("tags", {}),
                is_inferred=False,
            )
        except (BotoCoreError, ClientError) as e:
            logger.error("AWS error fetching REST API '%s': %s", api_id, str(e))
            return None

    def _discover_v2_apis(self) -> List[NormalizedResource]:
        """Discover v2 HTTP/WebSocket APIs using 'apigatewayv2' client."""
        results: List[NormalizedResource] = []
        try:
            client = self.get_v2_client()
            response = client.get_apis()

            for api in response.get("Items", []):
                try:
                    normalized = self.get_v2_api_details(api["ApiId"], api)
                    if normalized:
                        results.append(normalized)
                except Exception as e:
                    logger.warning("Failed to parse v2 API '%s': %s", api.get("ApiId"), e)
        except (BotoCoreError, ClientError) as e:
            logger.error("Failed to list v2 APIs: %s", str(e))

        return results

    def get_v2_api_details(self, api_id: str, api_data: Optional[dict] = None) -> Optional[NormalizedResource]:
        """Get details for a v2 HTTP/WebSocket API."""
        try:
            client = self.get_v2_client()
            if not api_data:
                api_data = client.get_api(ApiId=api_id)

            # Fetch stages
            stages = []
            try:
                stage_resp = client.get_stages(ApiId=api_id)
                stages = [s["StageName"] for s in stage_resp.get("Items", [])]
            except Exception:
                pass

            # Fetch routes
            routes = []
            try:
                route_resp = client.get_routes(ApiId=api_id)
                routes = [r.get("RouteKey", "") for r in route_resp.get("Items", [])]
            except Exception:
                pass

            region = self.factory.config.region_name
            protocol = api_data.get("ProtocolType", "HTTP")
            arn = f"arn:aws:apigateway:{region}::/apis/{api_id}"

            metadata = APIGatewayMetadata(
                api_id=api_id,
                api_name=api_data.get("Name", api_id),
                api_type=f"HTTP/v2 ({protocol})",
                protocol_type=protocol,
                stages=stages,
                endpoint_types=["REGIONAL"],
                routes_or_resources=routes,
                created_date=str(api_data.get("CreatedDate")),
                endpoint_url=api_data.get("ApiEndpoint"),
            )

            return NormalizedResource(
                resource_id=arn,
                resource_type=ResourceType.API_GATEWAY,
                resource_name=api_data.get("Name", api_id),
                region=region,
                metadata=metadata.model_dump(),
                tags=api_data.get("Tags", {}),
                is_inferred=False,
            )
        except (BotoCoreError, ClientError) as e:
            logger.error("AWS error fetching v2 API '%s': %s", api_id, str(e))
            return None

