import numpy as np
import math
from typing import List, Tuple

def calculate_confidence_score(
    metric_deltas: List[Tuple[float, float]]
) -> float:
    """
    Calculates the overall confidence using:
    confidence = tanh(0.3 * sqrt(N)) * s_avg * (1 - min(1, std_dev / 100))
    """
    if not metric_deltas:
        return 0.0
        
    n = len(metric_deltas)
    similarities = [d[0] for d in metric_deltas]
    deltas = [d[1] for d in metric_deltas]
    
    s_avg = np.mean(similarities)
    std_dev = np.std(deltas)
    
    part1 = math.tanh(0.3 * math.sqrt(n))
    part2 = s_avg
    part3 = 1.0 - min(1.0, std_dev / 100.0)
    
    confidence = part1 * part2 * part3
    return float(max(0.0, min(1.0, confidence)))
