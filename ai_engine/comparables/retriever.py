from typing import List, Dict, Any, Tuple
from .similarity import compute_similarity
from ..forecasting.features import extract_features

def retrieve_top_k_comparables(
    target_change: Dict[str, Any], 
    target_baseline: Dict[str, Any], 
    historical_deployments: List[Dict[str, Any]], 
    k: int = 5
) -> List[Tuple[float, Dict[str, Any]]]:
    """
    Find the top-K historical deployments that are most similar to the target change.
    Returns a list of tuples: (similarity_score, historical_deployment).
    """
    target_features = extract_features(target_change, target_baseline)
    
    scored_deployments = []
    
    for dep in historical_deployments:
        # A real implementation would have stored these features offline, but for MVP we compute on the fly
        dep_baseline = dep.get("baseline_metrics", {})
        dep_features = extract_features(dep, dep_baseline)
        
        sim = compute_similarity(target_features, dep_features)
        
        # Only keep deployments with some minimal similarity
        if sim > 0.05:
            scored_deployments.append((sim, dep))
            
    # Sort by similarity descending
    scored_deployments.sort(key=lambda x: x[0], reverse=True)
    
    return scored_deployments[:k]
