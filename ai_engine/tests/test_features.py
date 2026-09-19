from ai_engine.forecasting.features import extract_features

def test_extract_lambda_memory_change():
    change = {
        "change_type": "lambda_memory_update",
        "details": {"old_memory_mb": 512, "new_memory_mb": 1024}
    }
    baseline = {
        "invocations": 1000,
        "latency_p95_ms": 200.0,
        "cost_usd": 10.0
    }
    
    features = extract_features(change, baseline)
    assert features["memory_delta"] == 512
    assert features["memory_pct_change"] == 1.0
    assert features["is_lambda_memory_change"] == 1.0
    assert features["baseline_latency_p95"] == 200.0
