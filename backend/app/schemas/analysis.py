from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AnalysisCreate(BaseModel):
    prId: str
    commitSha: str
    
class AnalysisResponse(BaseModel):
    analysisId: str
    projectId: str
    prId: str
    repo: str
    commitSha: str
    status: str
    createdAt: datetime
    updatedAt: datetime
    completedAt: datetime | None = None
    error: str | None = None
    changedFiles: list[str] | None = []
    affectedResources: list[str] | None = []
    forecast: dict[str, Any] | None = None
    confidence: float | None = None
    evidence: list[Any] | None = []
    recommendations: list[Any] | None = []
    assumptions: list[Any] | None = []
    
class OutcomeCreate(BaseModel):
    actualCost: str
    actualPerformance: str
    deploymentResult: str
    
class OutcomeResponse(OutcomeCreate):
    analysisId: str
    timestamp: datetime
    forecastCost: str
    forecastPerformance: str

class RecommendationModel(BaseModel):
    action: str
    reason: str
    priority: str
    affectedResource: str

class ForecastModel(BaseModel):
    costRange: str
    performanceRange: str

class AIResponseModel(BaseModel):
    forecast: ForecastModel
    confidence: float
    evidence: list[dict[str, Any]]
    assumptions: list[str]
    recommendations: list[RecommendationModel]
