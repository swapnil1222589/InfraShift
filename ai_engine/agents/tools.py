import json
from typing import Dict, Any, List
from ..ingestion.deployments import get_historical_data
from ..comparables.retriever import retrieve_top_k_comparables
from ..forecasting.predict import generate_forecast

_DB_MOCK = get_historical_data()

def get_historical_deployments(service: str, resource: str, change_type: str) -> List[Dict[str, Any]]:
    return _DB_MOCK

def get_cloudwatch_metrics(deployment_id: str) -> Dict[str, Any]:
    for dep in _DB_MOCK:
        if dep["deployment_id"] == deployment_id:
            return {
                "baseline": dep["baseline_metrics"],
                "observed": dep["observed_metrics"]
            }
    return {}

def find_comparable_changes(target_change: Dict[str, Any], target_baseline: Dict[str, Any]) -> str:
    comparables = retrieve_top_k_comparables(target_change, target_baseline, _DB_MOCK, k=5)
    
    results = []
    for sim, dep in comparables:
        results.append({
            "id": dep["deployment_id"],
            "similarity": round(sim, 2),
            "historical_change_type": dep["change_type"],
            "baseline": dep["baseline_metrics"],
            "observed": dep["observed_metrics"]
        })
    return json.dumps(results)

def run_forecast(target_change: Dict[str, Any], target_baseline: Dict[str, Any]) -> str:
    comparables = retrieve_top_k_comparables(target_change, target_baseline, _DB_MOCK, k=5)
    forecast_metrics, confidence = generate_forecast(comparables)
    
    return json.dumps({
        "forecast": forecast_metrics.model_dump(exclude_none=True),
        "overall_confidence": round(confidence, 2),
        "evidence_ids": [dep["deployment_id"] for _, dep in comparables]
    })

def get_affected_resources(change_dict: Dict[str, Any]) -> str:
    res_type = change_dict.get("resource_type", "unknown")
    res_id = change_dict.get("resource_id", "unknown")
    
    affected = [f"{res_id} ({res_type})"]
    if res_type == "lambda":
        affected.append("CloudWatch Logs")
    elif res_type == "api_gateway":
        affected.append("Lambda integrations")
        
    return json.dumps(affected)
