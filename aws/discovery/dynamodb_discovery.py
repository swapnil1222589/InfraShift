"""
AWS DynamoDB Table Discovery.
Inspects DynamoDB tables, billing mode, capacity, item count, size, keys, and status.
"""

import logging
from typing import List, Optional
from botocore.exceptions import BotoCoreError, ClientError

from aws.config.aws_config import AWSClientFactory
from aws.models.aws_models import NormalizedResource, ResourceType, DynamoDBMetadata

logger = logging.getLogger("infrashift.aws.discovery.dynamodb")


class DynamoDBDiscovery:
    """Discovers AWS DynamoDB table resources."""

    def __init__(self, client_factory: AWSClientFactory):
        self.factory = client_factory

    def get_client(self):
        return self.factory.get_client("dynamodb")

    def discover_all(self) -> List[NormalizedResource]:
        """
        Discover all DynamoDB tables in the configured region.
        """
        resources: List[NormalizedResource] = []
        try:
            client = self.get_client()
            paginator = client.get_paginator("list_tables")

            for page in paginator.paginate():
                for table_name in page.get("TableNames", []):
                    try:
                        normalized = self.get_table_details(table_name)
                        if normalized:
                            resources.append(normalized)
                    except Exception as e:
                        logger.warning("Error fetching details for DynamoDB table '%s': %s", table_name, e)
        except (BotoCoreError, ClientError) as e:
            logger.error("Failed to list DynamoDB tables: %s", str(e))

        return resources

    def get_table_details(self, table_name: str) -> Optional[NormalizedResource]:
        """
        Discover details for a specific DynamoDB table by name.
        """
        try:
            client = self.get_client()
            response = client.describe_table(TableName=table_name)
            table = response.get("Table", {})

            # Key schema parsing
            partition_key = None
            sort_key = None
            for key in table.get("KeySchema", []):
                if key.get("KeyType") == "HASH":
                    partition_key = key.get("AttributeName")
                elif key.get("KeyType") == "RANGE":
                    sort_key = key.get("AttributeName")

            # Billing summary & provisioned capacity
            billing_summary = table.get("BillingModeSummary", {})
            billing_mode = billing_summary.get("BillingMode", "PROVISIONED")

            provisioned = table.get("ProvisionedThroughput", {})
            read_cap = provisioned.get("ReadCapacityUnits")
            write_cap = provisioned.get("WriteCapacityUnits")

            creation_dt = str(table.get("CreationDateTime")) if table.get("CreationDateTime") else None

            metadata = DynamoDBMetadata(
                table_arn=table.get("TableArn", f"arn:aws:dynamodb:{self.factory.config.region_name}::table/{table_name}"),
                table_name=table.get("TableName", table_name),
                table_status=table.get("TableStatus", "UNKNOWN"),
                billing_mode=billing_mode,
                read_capacity_units=read_cap,
                write_capacity_units=write_cap,
                item_count=table.get("ItemCount"),
                table_size_bytes=table.get("TableSizeBytes"),
                creation_date_time=creation_dt,
                partition_key=partition_key,
                sort_key=sort_key,
                global_secondary_indexes_count=len(table.get("GlobalSecondaryIndexes", [])),
                local_secondary_indexes_count=len(table.get("LocalSecondaryIndexes", [])),
            )

            arn = table.get("TableArn", "")
            arn_parts = arn.split(":") if arn else []
            region = arn_parts[3] if len(arn_parts) > 3 else self.factory.config.region_name
            account_id = arn_parts[4] if len(arn_parts) > 4 else None

            return NormalizedResource(
                resource_id=arn or f"arn:aws:dynamodb:{region}:table/{table_name}",
                resource_type=ResourceType.DYNAMODB,
                resource_name=table_name,
                region=region,
                account_id=account_id,
                metadata=metadata.model_dump(),
                is_inferred=False,
            )
        except (BotoCoreError, ClientError) as e:
            logger.error("AWS error discovering DynamoDB table '%s': %s", table_name, str(e))
            return None
