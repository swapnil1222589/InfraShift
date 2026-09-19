"""InfraShift configuration — all values from environment variables."""
from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Application
    APP_NAME: str = "InfraShift"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Mode flags
    LOCAL_MODE: bool = True
    LIVE_AWS: bool = False
    MOCK_AI: bool = True
    MOCK_GITHUB: bool = True

    # AWS
    AWS_REGION: str = "us-east-1"

    # DynamoDB table names
    DYNAMODB_PROJECTS_TABLE: str = "infrashift-projects"
    DYNAMODB_ANALYSES_TABLE: str = "infrashift-analyses"
    DYNAMODB_AUDIT_TABLE: str = "infrashift-audit-events"

    # GitHub
    GITHUB_TOKEN: str = ""
    GITHUB_WEBHOOK_SECRET: str = ""

    # Frontend CORS
    FRONTEND_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Timeouts (seconds)
    GITHUB_TIMEOUT_SECONDS: int = 10
    AWS_TIMEOUT_SECONDS: int = 10
    AI_TIMEOUT_SECONDS: int = 30

    # CloudWatch lookback
    CLOUDWATCH_LOOKBACK_DAYS: int = 7

    # Auto-create project from webhook (optional extension)
    AUTO_CREATE_PROJECT: bool = False

    @field_validator("FRONTEND_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


settings = Settings()
