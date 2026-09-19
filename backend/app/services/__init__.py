"""Services package."""
from app.services.ai_service import AIServiceProtocol, MockAIService, ai_service, create_ai_service
from app.services.analysis_service import (
    create_analysis,
    get_analysis,
    get_project_history,
    record_outcome,
    transition_status,
)
from app.services.aws_service import aws_service
from app.services.cloudwatch_service import cloudwatch_service
from app.services.evidence_service import evidence_service
from app.services.github_service import github_service
from app.services.outcome_service import submit_outcome
from app.services.project_service import (
    create_project,
    get_or_create_project_by_repo,
    get_project,
    get_project_or_none,
)

__all__ = [
    "AIServiceProtocol",
    "MockAIService",
    "ai_service",
    "create_ai_service",
    "create_analysis",
    "get_analysis",
    "get_project_history",
    "record_outcome",
    "transition_status",
    "aws_service",
    "cloudwatch_service",
    "evidence_service",
    "github_service",
    "submit_outcome",
    "create_project",
    "get_or_create_project_by_repo",
    "get_project",
    "get_project_or_none",
]
