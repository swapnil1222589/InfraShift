import json
import os
from typing import Dict, Any

from ..schemas.contracts import ForecastRequest, ForecastResponse, ForecastMetrics, EvidenceRecord
from .tools import find_comparable_changes, run_forecast, get_affected_resources

def load_prompt(prompt_name: str) -> str:
    path = os.path.join(os.path.dirname(__file__), '..', 'prompts', prompt_name)
    with open(path, 'r') as f:
        return f.read()

def mock_bedrock_completion(prompt: str) -> str:
    if "recommendation_v1.txt" in prompt:
        return json.dumps({
            "assumptions": ["Traffic stays within historical range", "No simultaneous dependent changes"],
            "recommendations": ["Expect moderate cost increase; consider small roll-out first.", "Monitor CloudWatch for throttling."]
        })
    elif "explanation_v1.txt" in prompt:
        return "Based on historical deployments with similar Lambda memory increases, we observe cost increases and latency decreases. Forecasts assume similar traffic patterns."
    
    return "{}"

def analyze_and_forecast(request: ForecastRequest) -> ForecastResponse:
    change_dict = request.change.model_dump()
    baseline_dict = request.baseline_metrics.model_dump()
    
    # 1. Understand proposed change & get affected resources
    affected_str = get_affected_resources(change_dict)
    affected = json.loads(affected_str)
    
    # 2. Retrieve comparable deployments
    comparables_str = find_comparable_changes(change_dict, baseline_dict)
    comparables = json.loads(comparables_str)
    
    # 3. Run numerical forecast
    forecast_str = run_forecast(change_dict, baseline_dict)
    forecast_data = json.loads(forecast_str)
    
    # Extract evidence
    evidence_records = []
    for comp in comparables:
        evidence_records.append(
            EvidenceRecord(
                id=comp["id"],
                similarity=comp["similarity"],
                result=f"Sim {comp['similarity']}"
            )
        )
    
    # 4. Bedrock Explanation
    system_prompt = load_prompt("system_v1.txt")
    explanation_prompt = load_prompt("explanation_v1.txt") + f"\n\nEVIDENCE:\n{comparables_str}\n\nFORECAST:\n{forecast_str}"
    rec_prompt = load_prompt("recommendation_v1.txt")
    
    explanation_text = mock_bedrock_completion(explanation_prompt)
    rec_json_str = mock_bedrock_completion(rec_prompt)
    rec_data = json.loads(rec_json_str)
    
    forecast_metrics = ForecastMetrics(**forecast_data["forecast"])
    
    response = ForecastResponse(
        forecast=forecast_metrics,
        confidence=round(forecast_data["overall_confidence"], 2),
        evidence=evidence_records,
        assumptions=rec_data.get("assumptions", []),
        affected_resources=affected,
        explanation=explanation_text,
        recommendations=rec_data.get("recommendations", [])
    )
    
    return response
