from typing import List, Dict, Any, Tuple

def compute_weighted_forecast(
    similar_deployments: List[Tuple[float, Dict[str, Any]]]
) -> Dict[str, List[Tuple[float, float]]]:
    """
    Returns a dictionary mapping metric names to a list of (similarity_score, percentage_delta) tuples.
    """
    if not similar_deployments:
        return {}
        
    metric_deltas = {
        "cost": [],
        "latency": [],
        "invocations": []
    }
    
    for sim, dep in similar_deployments:
        baseline = dep.get("baseline_metrics", {})
        observed = dep.get("observed_metrics", {})
        
        if baseline.get("cost_usd") and observed.get("cost_usd"):
            delta_pct = ((observed["cost_usd"] - baseline["cost_usd"]) / baseline["cost_usd"]) * 100
            metric_deltas["cost"].append((sim, delta_pct))
            
        if baseline.get("latency_p95_ms") and observed.get("latency_p95_ms"):
            delta_pct = ((observed["latency_p95_ms"] - baseline["latency_p95_ms"]) / baseline["latency_p95_ms"]) * 100
            metric_deltas["latency"].append((sim, delta_pct))
            
        if baseline.get("invocations") and observed.get("invocations"):
            delta_pct = ((observed["invocations"] - baseline["invocations"]) / baseline["invocations"]) * 100
            metric_deltas["invocations"].append((sim, delta_pct))
            
    return metric_deltas
