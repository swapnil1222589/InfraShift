"""
Unit tests for AWS Configuration and Client Factory.
"""

import os
from unittest.mock import MagicMock, patch
import pytest
from botocore.exceptions import BotoCoreError

from aws.config.aws_config import AWSConfig, AWSClientFactory


def test_aws_config_default_region(monkeypatch):
    monkeypatch.delenv("AWS_REGION", raising=False)
    monkeypatch.delenv("AWS_DEFAULT_REGION", raising=False)
    monkeypatch.delenv("AWS_PROFILE", raising=False)

    mock_session = MagicMock()
    mock_session.region_name = "us-east-1"

    with patch("boto3.Session", return_value=mock_session):
        config = AWSConfig()
        assert config.region_name == "us-east-1"
        assert config.session == mock_session


def test_aws_config_custom_region_and_profile(monkeypatch):
    monkeypatch.setenv("AWS_REGION", "ap-south-1")
    monkeypatch.setenv("AWS_PROFILE", "my-profile")

    mock_session = MagicMock()
    mock_session.region_name = "ap-south-1"

    with patch("boto3.Session", return_value=mock_session) as mock_sess_cls:
        config = AWSConfig(region_name="eu-west-1", profile_name="custom-profile")
        mock_sess_cls.assert_called_once_with(profile_name="custom-profile", region_name="eu-west-1")
        assert config.region_name == "eu-west-1"


def test_client_factory_injection():
    mock_config = MagicMock()
    mock_lambda_client = MagicMock()
    
    factory = AWSClientFactory(
        config=mock_config,
        custom_clients={"lambda": mock_lambda_client}
    )

    # Injected client should be returned directly
    assert factory.get_client("lambda") == mock_lambda_client
    
    # Non-injected service delegates to config
    factory.get_client("dynamodb")
    mock_config.get_client.assert_called_once_with("dynamodb")


def test_aws_config_session_failure():
    with patch("boto3.Session", side_effect=BotoCoreError()):
        with pytest.raises(ValueError, match="AWS Session creation failed"):
            AWSConfig()
