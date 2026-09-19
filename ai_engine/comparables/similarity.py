import math
from typing import Dict

def compute_similarity(f1: Dict[str, float], f2: Dict[str, float], alpha: float = 0.7) -> float:
    """
    Computes similarity using the formula:
    similarity = alpha * I[match on type] + (1 - alpha) * exp(-d)
    where d is the weighted Euclidean distance on numeric features.
    """
    # 1. Indicator for match on type
    match_on_type = 0.0
    if f1.get("is_lambda_memory_change") == f2.get("is_lambda_memory_change") and \
       f1.get("is_dynamodb_change") == f2.get("is_dynamodb_change") and \
       f1.get("is_caching_change") == f2.get("is_caching_change"):
        match_on_type = 1.0

    # 2. Weighted distance for numeric features
    distance_sq = 0.0
    weights = {
        "memory_pct_change": 2.0,
        "rcu_pct_change": 2.0,
        "baseline_latency_p95": 0.01,
        "baseline_cost": 0.05,
        "baseline_invocations": 0.01
    }
    
    all_keys = set(f1.keys()).union(set(f2.keys()))
    for key in all_keys:
        if "is_" in key:
            continue
            
        v1 = f1.get(key, 0.0)
        v2 = f2.get(key, 0.0)
        w = weights.get(key, 1.0)
        
        distance_sq += w * ((v1 - v2) ** 2)
        
    d = math.sqrt(distance_sq)
    
    # 3. Combined score
    similarity = (alpha * match_on_type) + ((1.0 - alpha) * math.exp(-d))
    return max(0.0, min(1.0, similarity))
