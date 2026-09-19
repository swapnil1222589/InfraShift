"""
AWS Lambda Handler for InfraShift Demo Workload.
Endpoint: GET /users/{id}
Performs a real DynamoDB read against 'infraShift-demo-users' table.
"""

import json
import os
import time
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TABLE_NAME = os.getenv("TABLE_NAME", "infraShift-demo-users")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):
    start_time = time.time()
    logger.info("Received event: %s", json.dumps(event))

    path_parameters = event.get("pathParameters") or {}
    user_id = path_parameters.get("id") or event.get("userId") or "user-001"

    try:
        response = table.get_item(Key={"userId": user_id})
        item = response.get("Item")

        duration_ms = round((time.time() - start_time) * 1000, 2)

        if not item:
            logger.warning("User '%s' not found in table '%s'", user_id, TABLE_NAME)
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error": "User not found",
                    "userId": user_id,
                    "duration_ms": duration_ms,
                    "table": TABLE_NAME,
                }),
            }

        logger.info("Successfully fetched user '%s' in %s ms", user_id, duration_ms)
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({
                "message": "User retrieved successfully",
                "user": item,
                "execution_metadata": {
                    "duration_ms": duration_ms,
                    "table": TABLE_NAME,
                    "read_capacity_consumed": 1,
                },
            }),
        }

    except ClientError as e:
        logger.error("DynamoDB error: %s", e.response["Error"]["Message"])
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "Internal Server Error",
                "message": e.response["Error"]["Message"],
            }),
        }
