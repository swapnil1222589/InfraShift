"""
InfraShift AWS Module.
Provides AWS resource discovery, CloudWatch telemetry collection, dependency discovery,
code change impact mapping, deployment lifecycle tracking, forecast comparison loop,
and unified AWS evidence integration package.
"""

from aws.integration.evidence_models import AWSEvidencePackage, ResourceTraceability
from aws.integration.evidence_service import AWSEvidenceIntegrationService

__version__ = "0.1.0"

__all__ = [
    "AWSEvidencePackage",
    "ResourceTraceability",
    "AWSEvidenceIntegrationService",
]
