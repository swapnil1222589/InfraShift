"""
CloudWatch Metric Namespaces and Constants for InfraShift.
Defines supported metrics for AWS Lambda and AWS DynamoDB.
"""

from enum import Enum
from typing import Dict, List


class MetricNamespace(str, Enum):
    LAMBDA = "AWS/Lambda"
    DYNAMODB = "AWS/DynamoDB"
    API_GATEWAY = "AWS/ApiGateway"


class LambdaMetrics:
    INVOCATIONS = "Invocations"
    DURATION = "Duration"
    ERRORS = "Errors"
    THROTTLES = "Throttles"

    ALL_DEFAULT = [INVOCATIONS, DURATION, ERRORS, THROTTLES]


class DynamoDBMetrics:
    CONSUMED_READ_CAPACITY = "ConsumedReadCapacityUnits"
    CONSUMED_WRITE_CAPACITY = "ConsumedWriteCapacityUnits"
    READ_THROTTLE_EVENTS = "ReadThrottleEvents"
    WRITE_THROTTLE_EVENTS = "WriteThrottleEvents"

    ALL_DEFAULT = [
        CONSUMED_READ_CAPACITY,
        CONSUMED_WRITE_CAPACITY,
        READ_THROTTLE_EVENTS,
        WRITE_THROTTLE_EVENTS,
    ]


METRIC_STATISTICS: Dict[str, str] = {
    LambdaMetrics.INVOCATIONS: "Sum",
    LambdaMetrics.DURATION: "Average",
    LambdaMetrics.ERRORS: "Sum",
    LambdaMetrics.THROTTLES: "Sum",
    DynamoDBMetrics.CONSUMED_READ_CAPACITY: "Sum",
    DynamoDBMetrics.CONSUMED_WRITE_CAPACITY: "Sum",
    DynamoDBMetrics.READ_THROTTLE_EVENTS: "Sum",
    DynamoDBMetrics.WRITE_THROTTLE_EVENTS: "Sum",
}
