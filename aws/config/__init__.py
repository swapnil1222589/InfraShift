"""
AWS Configuration module for InfraShift.
Provides safe, credential-free AWS session management and client factories.
"""

from .aws_config import AWSConfig, AWSClientFactory

__all__ = ["AWSConfig", "AWSClientFactory"]
