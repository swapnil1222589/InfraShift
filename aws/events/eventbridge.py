"""
AWS EventBridge Integration Module.
Parses, validates, and normalizes incoming EventBridge deployment event payloads.
Provides interface for publishing deployment status events to AWS EventBridge.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from botocore.exceptions import BotoCoreError, ClientError

from aws.config.aws_config import AWSClientFactory, AWSConfig
from aws.models.aws_models import ResourceType
from aws.events.event_models import (
    DeploymentEvent,
    DeploymentStatus,
    DeploymentEnvironment,
    DeployedResource,
)

logger = logging.getLogger("infrashift.aws.events.eventbridge")


STATUS_MAP: Dict[str, DeploymentStatus] = {
    "PENDING": DeploymentStatus.PENDING,
    "QUEUED": DeploymentStatus.PENDING,
    "STARTING": DeploymentStatus.STARTED,
    "STARTED": DeploymentStatus.STARTED,
    "IN_PROGRESS": DeploymentStatus.STARTED,
    "SUCCESS": DeploymentStatus.COMPLETED,
    "SUCCEEDED": DeploymentStatus.COMPLETED,
    "COMPLETED": DeploymentStatus.COMPLETED,
    "FAIL": DeploymentStatus.FAILED,
    "FAILED": DeploymentStatus.FAILED,
    "FAILURE": DeploymentStatus.FAILED,
    "CANCELLED": DeploymentStatus.CANCELLED,
    "CANCELED": DeploymentStatus.CANCELLED,
}

ENV_MAP: Dict[str, DeploymentEnvironment] = {
    "SANDBOX": DeploymentEnvironment.SANDBOX,
    "DEV": DeploymentEnvironment.SANDBOX,
    "DEVELOPMENT": DeploymentEnvironment.SANDBOX,
    "STAGING": DeploymentEnvironment.STAGING,
    "STAGE": DeploymentEnvironment.STAGING,
    "PROD": DeploymentEnvironment.PRODUCTION,
    "PRODUCTION": DeploymentEnvironment.PRODUCTION,
}


class EventBridgeIntegration:
    """Handles EventBridge payload parsing and deployment event publishing."""

    def __init__(
        self,
        client_factory: Optional[AWSClientFactory] = None,
        config: Optional[AWSConfig] = None,
    ):
        if client_factory:
            self.factory = client_factory
        else:
            self.factory = AWSClientFactory(config=config or AWSConfig())

    def get_client(self):
        return self.factory.get_client("events")

    def parse_eventbridge_payload(self, payload: Dict[str, Any]) -> Optional[DeploymentEvent]:
        """
        Parse and validate a raw EventBridge event payload into a normalized DeploymentEvent.

        :param payload: Dictionary containing EventBridge envelope or payload.
        :return: DeploymentEvent instance or None if invalid/unparseable.
        """
        if not isinstance(payload, dict) or not payload:
            logger.warning("Received empty or non-dict EventBridge payload.")
            return None

        event_id = payload.get("id") or payload.get("event_id") or "event-unknown"
        detail = payload.get("detail", {}) if isinstance(payload.get("detail"), dict) else payload

        # Require explicit deployment_id or deploymentId field
        deployment_id = (
            detail.get("deployment_id")
            or detail.get("deploymentId")
            or payload.get("deployment_id")
            or payload.get("deploymentId")
        )

        if not deployment_id:
            logger.warning("EventBridge payload missing required 'deployment_id'. Event ID: %s", event_id)
            return None


        change_id = detail.get("change_id") or detail.get("changeId") or detail.get("pull_request_id")
        commit_sha = detail.get("commit_sha") or detail.get("commitSha") or detail.get("git_sha")

        # Normalize Environment
        raw_env = str(detail.get("environment") or detail.get("env") or "sandbox").upper()
        environment = ENV_MAP.get(raw_env, DeploymentEnvironment.SANDBOX)

        # Normalize Status
        raw_status = str(detail.get("status") or detail.get("state") or detail.get("deploymentStatus") or "PENDING").upper()
        status = STATUS_MAP.get(raw_status, DeploymentStatus.UNKNOWN)

        # Extract timestamps (strict null preservation)
        started_at = detail.get("started_at") or detail.get("startTime")
        completed_at = detail.get("completed_at") or detail.get("endTime")

        # Parse resources
        resources: List[DeployedResource] = []
        raw_resources = detail.get("resources") or payload.get("resources") or []
        if isinstance(raw_resources, list):
            for res_item in raw_resources:
                if isinstance(res_item, str) and (res_item.startswith("arn:aws:") or ":" in res_item):
                    res_type = self._infer_resource_type(res_item)
                    resources.append(DeployedResource(resource_id=res_item, resource_type=res_type))
                elif isinstance(res_item, dict) and "resource_id" in res_item:
                    res_type_val = res_item.get("resource_type", "lambda")
                    res_type = ResourceType(res_type_val) if res_type_val in ResourceType._value2member_map_ else ResourceType.LAMBDA
                    resources.append(
                        DeployedResource(
                            resource_id=res_item["resource_id"],
                            resource_type=res_type,
                            region=res_item.get("region", self.factory.config.region_name),
                        )
                    )

        region = payload.get("region") or detail.get("region") or self.factory.config.region_name

        return DeploymentEvent(
            event_id=event_id,
            deployment_id=str(deployment_id),
            change_id=str(change_id) if change_id else None,
            commit_sha=str(commit_sha) if commit_sha else None,
            environment=environment,
            status=status,
            started_at=str(started_at) if started_at else None,
            completed_at=str(completed_at) if completed_at else None,
            region=region,
            resources=resources,
            raw_payload=payload,
        )

    def put_deployment_event(
        self,
        event: DeploymentEvent,
        event_bus_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Publish a normalized DeploymentEvent to AWS EventBridge.

        :param event: DeploymentEvent to publish.
        :param event_bus_name: Optional target EventBridge event bus name (default: 'default').
        :return: Result dictionary containing status and FailedEntryCount.
        """
        try:
            client = self.get_client()
            bus_name = event_bus_name or "default"

            entry = {
                "Source": "infrashift.deployment",
                "DetailType": "Deployment Status Change",
                "Detail": json.dumps(event.model_dump()),
                "EventBusName": bus_name,
            }

            response = client.put_events(Entries=[entry])
            failed_count = response.get("FailedEntryCount", 0)
            if failed_count > 0:
                logger.warning("EventBridge put_events recorded %d failed entries.", failed_count)

            return {
                "status": "success" if failed_count == 0 else "partial_failure",
                "failed_count": failed_count,
                "response": response,
            }
        except (BotoCoreError, ClientError) as e:
            logger.error("Failed to publish deployment event to EventBridge: %s", str(e))
            return {
                "status": "error",
                "error": str(e),
                "failed_count": 1,
            }

    def _infer_resource_type(self, arn_or_id: str) -> ResourceType:
        """Infer ResourceType from ARN string."""
        lower = arn_or_id.lower()
        if "dynamodb" in lower:
            return ResourceType.DYNAMODB
        elif "apigateway" in lower or "api" in lower:
            return ResourceType.API_GATEWAY
        return ResourceType.LAMBDA
