from typing import List, Dict, Any, Optional

def get_normalized_cloudwatch_metrics(
    resource_id: str, 
    resource_type: str, 
    metric_names: List[str], 
    start_time: str, 
    end_time: str
) -> List[Dict[str, Any]]:
    """
    Interface for Person 2's telemetry pipeline.
    This module expects normalized metrics.
    
    Returns structured metric snapshots.
    """
    # For MVP, this will just return empty or mock data until Person 2 connects it.
    metrics = []
    for m in metric_names:
        metrics.append({
            "resource_id": resource_id,
            "resource_type": resource_type,
            "metric_name": m,
            "timestamp": start_time,
            "value": 0.0 # Placeholder
        })
    return metrics
