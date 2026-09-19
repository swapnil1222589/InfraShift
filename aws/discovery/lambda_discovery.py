import logging
from typing import List, Optional, Dict, Any
from botocore.exceptions import BotoCoreError, ClientError

from aws.config.aws_config import AWSClientFactory
from aws.models.aws_models import (
    NormalizedResource,
    ResourceType,
    LambdaMetadata,
    NormalizedDependency,
    EvidenceType,
    ConfidenceLevel,
    RelationshipType,
)

logger = logging.getLogger("infrashift.aws.discovery.lambda")


class LambdaDiscovery:
    """Discovers AWS Lambda resources in a specified region."""

    def __init__(self, client_factory: AWSClientFactory):
        self.factory = client_factory

    def get_client(self):
        return self.factory.get_client("lambda")

    def discover_all(self, region_override: Optional[str] = None) -> List[NormalizedResource]:
        """
        Discover all Lambda functions in the configured region.
        """
        resources: List[NormalizedResource] = []
        try:
            client = self.get_client()
            paginator = client.get_paginator("list_functions")
            
            for page in paginator.paginate():
                for fn in page.get("Functions", []):
                    try:
                        normalized = self.get_function_details(fn["FunctionName"])
                        if normalized:
                            resources.append(normalized)
                    except Exception as e:
                        logger.warning("Error fetching details for Lambda function '%s': %s", fn.get("FunctionName"), e)
        except (BotoCoreError, ClientError) as e:
            logger.error("Failed to list Lambda functions: %s", str(e))

        return resources

    def discover_inferred_dynamodb_dependencies(self) -> List[NormalizedDependency]:
        """
        Inspect Lambda function environment configurations to infer potential DynamoDB table access.
        Relationships inferred from environment variables are STRICTLY marked with confidence='inferred'.
        """
        dependencies: List[NormalizedDependency] = []
        try:
            client = self.get_client()
            paginator = client.get_paginator("list_functions")

            for page in paginator.paginate():
                for fn in page.get("Functions", []):
                    fn_name = fn.get("FunctionName")
                    fn_arn = fn.get("FunctionArn")
                    if not fn_arn:
                        continue

                    # Fetch environment variables
                    env_vars = fn.get("Environment", {}).get("Variables", {})
                    # If list_functions omitted Environment, query get_function_configuration
                    if not env_vars:
                        try:
                            config = client.get_function_configuration(FunctionName=fn_name)
                            env_vars = config.get("Environment", {}).get("Variables", {})
                        except (BotoCoreError, ClientError):
                            pass

                    for key, val in env_vars.items():
                        key_upper = key.upper()
                        # Check if env key or value suggests DynamoDB table
                        is_table_key = any(k in key_upper for k in ["TABLE", "DYNAMO", "DDB"])
                        is_table_arn = isinstance(val, str) and val.startswith("arn:aws:dynamodb:")

                        if is_table_key or is_table_arn:
                            target_arn = val if is_table_arn else f"arn:aws:dynamodb:{self.factory.config.region_name}::table/{val}"
                            table_name = val.split(":")[-1].split("/")[-1] if ":" in val or "/" in val else val

                            dep = NormalizedDependency(
                                source_resource_id=fn_arn,
                                source_type=ResourceType.LAMBDA,
                                target_resource_id=target_arn,
                                target_type=ResourceType.DYNAMODB,
                                relationship=RelationshipType.ACCESSES,
                                evidence_type=EvidenceType.APPLICATION_METADATA,
                                confidence=ConfidenceLevel.INFERRED,
                                metadata={
                                    "env_key": key,
                                    "inferred_table_name": table_name,
                                    "inference_reason": f"Lambda environment variable '{key}' points to table '{table_name}'",
                                },
                            )
                            dependencies.append(dep)
        except (BotoCoreError, ClientError) as e:
            logger.error("Failed to discover inferred Lambda → DynamoDB dependencies: %s", str(e))

        return dependencies

    def get_function_details(self, function_name: str) -> Optional[NormalizedResource]:
        """
        Discover details for a specific Lambda function by name or ARN.
        """
        try:
            client = self.get_client()
            response = client.get_function(FunctionName=function_name)
            config = response.get("Configuration", {})
            tags = response.get("Tags", {})

            # Process environment variables safely (redact sensitive values)
            env_vars = config.get("Environment", {}).get("Variables", {})
            env_keys = list(env_vars.keys())

            metadata = LambdaMetadata(
                function_arn=config["FunctionArn"],
                function_name=config["FunctionName"],
                runtime=config.get("Runtime"),
                memory_mb=config.get("MemorySize"),
                timeout_seconds=config.get("Timeout"),
                handler=config.get("Handler"),
                code_size_bytes=config.get("CodeSize"),
                last_modified=config.get("LastModified"),
                environment_keys=env_keys,
                role_arn=config.get("Role"),
                architectures=config.get("Architectures", []),
            )

            # Extract region and account from ARN
            arn_parts = config["FunctionArn"].split(":")
            region = arn_parts[3] if len(arn_parts) > 3 else self.factory.config.region_name
            account_id = arn_parts[4] if len(arn_parts) > 4 else None

            return NormalizedResource(
                resource_id=config["FunctionArn"],
                resource_type=ResourceType.LAMBDA,
                resource_name=config["FunctionName"],
                region=region,
                account_id=account_id,
                tags=tags,
                metadata=metadata.model_dump(),
                is_inferred=False,
            )
        except (BotoCoreError, ClientError) as e:
            logger.error("AWS error discovering Lambda '%s': %s", function_name, str(e))
            return None

