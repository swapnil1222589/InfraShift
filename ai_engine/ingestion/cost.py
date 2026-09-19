from typing import Dict, Any

def get_normalized_cost_data(
    resource_id: str, 
    resource_type: str, 
    start_time: str, 
    end_time: str
) -> Dict[str, Any]:
    """
    Interface for Person 2's cost pipeline (Cost Explorer/CUR).
    
    Returns structured cost data for a given resource and time window.
    """
    # Placeholder for MVP
    return {
        "resource_id": resource_id,
        "resource_type": resource_type,
        "total_cost_usd": 0.0,
        "currency": "USD",
        "granularity": "HOURLY"
    }
