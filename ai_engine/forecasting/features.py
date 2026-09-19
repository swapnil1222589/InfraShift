from typing import Dict, Any

def extract_features(change: Dict[str, Any], baseline: Dict[str, Any]) -> Dict[str, float]:
    """
    Convert raw change + telemetry data into a normalized numeric feature vector.
    These features are used for similarity comparison.
    """
    features = {}
    
    # 1. Change Features
    change_type = change.get("change_type", "")
    resource_type = change.get("resource_type", "")
    
    if "lambda_memory" in change_type or (resource_type == "lambda" and "memory" in change_type):
        details = change.get("details", {})
        
        # Handle both V1 and V2 JSON formats for memory details
        if "memory_mb" in details and isinstance(details["memory_mb"], dict):
            old_mem = float(details["memory_mb"].get("old", 1.0))
            new_mem = float(details["memory_mb"].get("new", 1.0))
        else:
            old_mem = float(details.get("old_memory_mb", 1.0))
            new_mem = float(details.get("new_memory_mb", 1.0))
            
        features["memory_delta"] = new_mem - old_mem
        features["memory_pct_change"] = ((new_mem - old_mem) / old_mem) if old_mem else 0.0
        # Categorical one-hot placeholder
        features["is_lambda_memory_change"] = 1.0
    else:
        features["memory_delta"] = 0.0
        features["memory_pct_change"] = 0.0
        features["is_lambda_memory_change"] = 0.0

    if "dynamodb_capacity" in change_type:
        old_rcu = float(change.get("details", {}).get("old_rcu", 1.0))
        new_rcu = float(change.get("details", {}).get("new_rcu", 1.0))
        features["rcu_delta"] = new_rcu - old_rcu
        features["rcu_pct_change"] = ((new_rcu - old_rcu) / old_rcu) if old_rcu else 0.0
        features["is_dynamodb_change"] = 1.0
    else:
        features["rcu_delta"] = 0.0
        features["rcu_pct_change"] = 0.0
        features["is_dynamodb_change"] = 0.0

    if "caching" in change_type:
        features["is_caching_change"] = 1.0
    else:
        features["is_caching_change"] = 0.0

    # 2. Baseline Features (normalized roughly to typical log scales or scaled)
    # Using raw values for MVP, but in production these would be StandardScaler transformed
    features["baseline_invocations"] = float(baseline.get("invocations") or 0.0) / 1000.0 # scaled per 1k
    features["baseline_latency_p95"] = float(baseline.get("latency_p95_ms") or 0.0)
    features["baseline_cost"] = float(baseline.get("cost_usd") or 0.0)
    
    return features
