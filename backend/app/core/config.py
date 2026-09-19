from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_ENV: str = "development"
    LOCAL_MODE: bool = True
    LIVE_AWS: bool = False
    MOCK_AI: bool = True
    MOCK_GITHUB: bool = True

    AWS_REGION: str = "us-east-1"
    
    GITHUB_TOKEN: str = ""
    GITHUB_WEBHOOK_SECRET: str = ""

    DYNAMODB_PROJECTS_TABLE: str = "infrashift-projects"
    DYNAMODB_ANALYSES_TABLE: str = "infrashift-analyses"
    DYNAMODB_AUDIT_TABLE: str = "infrashift-audit-events"

    S3_BUCKET: str = ""
    AI_SERVICE_URL: str = ""
    
    FRONTEND_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"

settings = Settings()
