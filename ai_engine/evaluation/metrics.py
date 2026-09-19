import numpy as np
from typing import List

def mean_absolute_error(y_true: List[float], y_pred: List[float]) -> float:
    if not y_true or not y_pred:
        return 0.0
    return float(np.mean(np.abs(np.array(y_true) - np.array(y_pred))))

def root_mean_squared_error(y_true: List[float], y_pred: List[float]) -> float:
    if not y_true or not y_pred:
        return 0.0
    return float(np.sqrt(np.mean((np.array(y_true) - np.array(y_pred))**2)))

def prediction_interval_coverage(
    y_true: List[float], 
    lower_bounds: List[float], 
    upper_bounds: List[float]
) -> float:
    """
    Computes what fraction of actual outcomes fell within the predicted bounds.
    """
    if not y_true:
        return 0.0
        
    hits = 0
    for y, low, high in zip(y_true, lower_bounds, upper_bounds):
        if low <= y <= high:
            hits += 1
            
    return hits / len(y_true)
