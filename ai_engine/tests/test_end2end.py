from ai_engine.main import start_forecast, get_forecast
from ai_engine.schemas.contracts import ForecastRequest, ChangeDetails, BaselineMetrics
from ai_engine.agents import tools
import json

def test_fastapi_end_to_end():
    # Inject a guaranteed match
    tools._DB_MOCK.append({
        "deployment_id": "dep_guaranteed",
        "change_type": "lambda_memory_increase",
        "details": {"old_memory_mb": 512, "new_memory_mb": 1024},
        "baseline_metrics": {"cost_usd": 10.0, "latency_p95_ms": 200.0, "invocations": 1000},
        "observed_metrics": {"cost_usd": 12.0, "latency_p95_ms": 150.0, "invocations": 1000}
    })

    analysis_id = "demo123"
    
    req = ForecastRequest(
        analysis_id=analysis_id,
        change=ChangeDetails(
            resource_type="lambda",
            change_type="lambda_memory_increase",
            resource_id="payment-function",
            details={"old_memory_mb": 512, "new_memory_mb": 1024}
        ),
        baseline_metrics=BaselineMetrics(
            invocations=100000.0,
            latency_p95_ms=200.0,
            error_rate_pct=0.5,
            cost_usd=40.0
        )
    )
    
    # 1. POST request equivalent
    post_resp = start_forecast(analysis_id, req)
    assert post_resp["status"] == "in_progress"
    
    # 2. GET request equivalent
    data = get_forecast(analysis_id).model_dump()
    
    assert "forecast" in data
    assert "confidence" in data
    assert data["confidence"] >= 0.0
    
    # Confirm output schema fields
    assert "point_estimate" in data["forecast"]["cost"]
    assert "lower_bound" in data["forecast"]["cost"]
    assert "upper_bound" in data["forecast"]["cost"]
