from ai_engine.forecasting.model import compute_weighted_forecast

def test_forecast_logic():
    similar = [
        (0.9, {
            "baseline_metrics": {"cost_usd": 10.0},
            "observed_metrics": {"cost_usd": 11.0} # +10%
        }),
        (0.8, {
            "baseline_metrics": {"cost_usd": 20.0},
            "observed_metrics": {"cost_usd": 24.0} # +20%
        })
    ]
    
    deltas = compute_weighted_forecast(similar)
    assert "cost" in deltas
    assert len(deltas["cost"]) == 2
    assert round(deltas["cost"][0][1], 1) == 10.0
    assert round(deltas["cost"][1][1], 1) == 20.0
