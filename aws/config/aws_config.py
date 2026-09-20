"""
AWS Configuration and Client Management.
Handles boto3 session creation using standard credential provider chain.
Supports AWS_PROFILE, AWS_REGION, and dependency injection for unit testing.
"""

import os
import logging
from typing import Optional, Any, Dict
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv

# Load environment variables if .env file is present
load_dotenv()

logger = logging.getLogger("infrashift.aws.config")


class AWSConfig:
    """
    Encapsulates AWS session configuration.
    Uses AWS credential provider chain and supports local profiles.
    """

    def __init__(
        self,
        region_name: Optional[str] = None,
        profile_name: Optional[str] = None,
        session: Optional[boto3.Session] = None,
    ):
        """
        Initialize AWS configuration.

        :param region_name: Explicit region override or None to read from env/config.
        :param profile_name: Explicit AWS profile override or None to read from AWS_PROFILE.
        :param session: Existing boto3.Session (useful for testing/dependency injection).
        """
        self.profile_name = profile_name or os.getenv("AWS_PROFILE")
        self.requested_region = (
            region_name
            or os.getenv("AWS_REGION")
            or os.getenv("AWS_DEFAULT_REGION")
        )

        if session:
            self._session = session
        else:
            self._session = self._create_session()

        # Resolve region from session if not explicitly set
        self.region_name = self.requested_region or self._session.region_name or "us-east-1"
        logger.info("AWSConfig initialized for region: %s", self.region_name)

    def _create_session(self) -> boto3.Session:
        """Create boto3 Session using standard credential provider chain."""
        try:
            kwargs: Dict[str, Any] = {}
            if self.profile_name:
                kwargs["profile_name"] = self.profile_name
            if self.requested_region:
                kwargs["region_name"] = self.requested_region

            return boto3.Session(**kwargs)
        except (BotoCoreError, ClientError) as e:
            from botocore.exceptions import NoCredentialsError, NoRegionError
            if isinstance(e, (NoCredentialsError, NoRegionError)):
                logger.error("AWS CLI Error: Missing credentials or region. Run 'aws configure'.")
                raise ValueError(f"AWS CLI Error: Missing credentials or region. Run 'aws configure'.") from e
            logger.error("Failed to create boto3 Session: %s", str(e))
            raise ValueError(f"AWS Session creation failed: {e}") from e

    @property
    def session(self) -> boto3.Session:
        """Get the underlying boto3 Session."""
        return self._session

    def get_client(self, service_name: str, region_name: Optional[str] = None) -> Any:
        """
        Create boto3 client for a given AWS service.

        :param service_name: AWS service identifier (e.g., 'lambda', 'dynamodb').
        :param region_name: Optional region override for this specific client.
        :return: boto3 client instance.
        """
        target_region = region_name or self.region_name
        try:
            return self._session.client(service_name, region_name=target_region)
        except (BotoCoreError, ClientError) as e:
            logger.error("Failed to create AWS client for %s in %s: %s", service_name, target_region, str(e))
            raise RuntimeError(f"Unable to create AWS client for '{service_name}': {e}") from e


class AWSClientFactory:
    """
    Factory class providing boto3 clients with support for client injection (mocking).
    """

    def __init__(
        self,
        config: Optional[AWSConfig] = None,
        custom_clients: Optional[Dict[str, Any]] = None,
    ):
        """
        :param config: AWSConfig instance. Creates default if None.
        :param custom_clients: Dictionary of pre-instantiated or mocked clients for dependency injection.
        """
        self.config = config or AWSConfig()
        self.custom_clients = custom_clients or {}

    def get_client(self, service_name: str) -> Any:
        """Return injected custom client or create new client from config."""
        if service_name in self.custom_clients:
            return self.custom_clients[service_name]
        return self.config.get_client(service_name)
