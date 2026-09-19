from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

class ChangeDetails(BaseModel):
    resource_type: str = Field(..., description="Type of the AWS resource")
    change_type: str = Field(..., description="Type of change")
    resource_id: str = Field(..., description="Identifier of the resource")
    details: Dict[str, Any] = Field(default_factory=dict, description="Key-value pairs of change details")
    code_diff: Optional[str] = Field(None, description="The code diff associated with the change")

class BaselineMetrics(BaseModel):
    invocations: float
    latency_p95_ms: float
    error_rate_pct: float
    cost_usd: float
    cpu_utilization: Optional[float] = None
    memory_utilization: Optional[float] = None

class ForecastRequest(BaseModel):
    analysis_id: str
    change: ChangeDetails
    baseline_metrics: BaselineMetrics

class MetricForecast(BaseModel):
    point_estimate: Union[float, str, None]
    lower_bound: Union[float, str, None]
    upper_bound: Union[float, str, None]
    unit: str
    direction: str = ""

class ForecastMetrics(BaseModel):
    cost: Optional[MetricForecast] = None
    latency: Optional[MetricForecast] = None
    cpu: Optional[MetricForecast] = None
    memory: Optional[MetricForecast] = None
    invocations: Optional[MetricForecast] = None

class EvidenceRecord(BaseModel):
    id: str
    similarity: float
    result: str

class ForecastResponse(BaseModel):
    forecast: ForecastMetrics
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence: List[EvidenceRecord] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    affected_resources: List[str] = Field(default_factory=list)
    explanation: str = ""
    recommendations: List[str] = Field(default_factory=list)
