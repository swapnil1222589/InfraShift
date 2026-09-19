import json
from typing import List
from ..ingestion.deployments import generate_synthetic_deployments
from ..comparables.retriever import retrieve_top_k_comparables
from ..forecasting.predict import generate_forecast
from .metrics import mean_absolute_error, root_mean_squared_error, prediction_interval_coverage

def run_backtesting(deployments: List[dict]):
    """
    Hides the actual post-deployment outcome for each item, predicts it using the others, 
    and compares it to the actual truth.
    """
    y_true_cost_pct = []
    y_pred_cost_pct = []
    cost_lower = []
    cost_upper = []
    
    for i, target_dep in enumerate(deployments):
        # The comparable DB is everything EXCEPT the target
        historical = deployments[:i] + deployments[i+1:]
        
        target_change = {
            "resource_type": target_dep["resource_type"],
            "change_type": target_dep["change_type"],
            "details": target_dep["details"]
        }
        target_baseline = target_dep["baseline_metrics"]
        
        # 1. Retrieve
        comparables = retrieve_top_k_comparables(target_change, target_baseline, historical, k=5)
        
        # 2. Forecast
        forecast, conf = generate_forecast(comparables)
        
        # 3. Evaluate truth (Cost specifically for this demo)
        if target_baseline.get("cost_usd") and target_dep["observed_metrics"].get("cost_usd"):
            true_pct = ((target_dep["observed_metrics"]["cost_usd"] - target_baseline["cost_usd"]) / target_baseline["cost_usd"]) * 100
            
            if forecast.cost and forecast.cost.change_range != "N/A":
                # Parse range string "+5.0% to +11.0%"
                try:
                    parts = forecast.cost.change_range.split(" to ")
                    low = float(parts[0].replace("%", ""))
                    high = float(parts[1].replace("%", ""))
                    
                    pred_mid = (low + high) / 2.0
                    
                    y_true_cost_pct.append(true_pct)
                    y_pred_cost_pct.append(pred_mid)
                    cost_lower.append(low)
                    cost_upper.append(high)
                except Exception:
                    pass
                    
    # Metrics calculation
    mae = mean_absolute_error(y_true_cost_pct, y_pred_cost_pct)
    rmse = root_mean_squared_error(y_true_cost_pct, y_pred_cost_pct)
    coverage = prediction_interval_coverage(y_true_cost_pct, cost_lower, cost_upper)
    
    return {
        "samples_evaluated": len(y_true_cost_pct),
        "cost_MAE_pct": round(mae, 2),
        "cost_RMSE_pct": round(rmse, 2),
        "interval_coverage": round(coverage, 2)
    }

if __name__ == "__main__":
    deps = generate_synthetic_deployments(100)
    res = run_backtesting(deps)
    print("Evaluation Results:", json.dumps(res, indent=2))
