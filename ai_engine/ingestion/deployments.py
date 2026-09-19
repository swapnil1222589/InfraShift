import os
import json
from typing import List, Dict, Any

def get_historical_data() -> List[Dict[str, Any]]:
    path = os.path.join(os.path.dirname(__file__), '..', 'data', 'historical.json')
    if not os.path.exists(path):
        return []
    with open(path, 'r') as f:
        return json.load(f)
