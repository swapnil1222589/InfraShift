import numpy as np
from typing import List, Dict, Any, Tuple
from .model import compute_weighted_forecast
from .confidence import calculate_confidence_score
from ..schemas.contracts import ForecastMetrics, MetricForecast

def generate_forecast(
    similar_deployments: List[Tuple[float, Dict[str, Any]]]
) -> Tuple[ForecastMetrics, float]:
    if not similar_deployments:
        return ForecastMetrics(), 0.0
        
    metric_deltas = compute_weighted_forecast(similar_deployments)
    
    forecasts = {}
    confidences = []
    
    for metric_name, deltas in metric_deltas.items():
        if not deltas:
            continue
            
        # Point Estimate: Weighted average
        sum_sim = sum(d[0] for d in deltas)
        if sum_sim == 0:
            point_est = np.mean([d[1] for d in deltas])
        else:
            point_est = sum((d[0] * d[1]) for d in deltas) / sum_sim
            
        # Prediction Range
        raw_deltas = [d[1] for d in deltas]
        lower_bound = float(np.min(raw_deltas))
        upper_bound = float(np.max(raw_deltas))
        
        direction = "increase" if point_est >= 0 else "decrease"
        
        forecast = MetricForecast(
            point_estimate=round(float(point_est), 2),
            lower_bound=round(lower_bound, 2),
            upper_bound=round(upper_bound, 2),
            unit="percent",
            direction=direction
        )
        forecasts[metric_name] = forecast
        
        # Confidence
        conf = calculate_confidence_score(deltas)
        confidences.append(conf)
        
    overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0
    return ForecastMetrics(**forecasts), overall_confidence
