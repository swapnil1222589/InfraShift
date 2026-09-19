from ai_engine.comparables.retriever import retrieve_top_k_comparables

def test_retrieval_logic():
    target_change = {
        "change_type": "lambda_memory_update",
        "details": {"old_memory_mb": 512, "new_memory_mb": 1024}
    }
    target_baseline = {
        "invocations": 1000,
        "latency_p95_ms": 200.0,
        "cost_usd": 10.0
    }
    
    hist = [
        {
            "deployment_id": "dep_1",
            "change_type": "lambda_memory_increase", # Handled in features.py
            "details": {"old_memory_mb": 512, "new_memory_mb": 1024},
            "baseline_metrics": target_baseline
        },
        {
            "deployment_id": "dep_2",
            "change_type": "dynamodb_capacity",
            "details": {"old_rcu": 100, "new_rcu": 200},
            "baseline_metrics": target_baseline
        }
    ]
    
    res = retrieve_top_k_comparables(target_change, target_baseline, hist, k=1)
    
    # It should retrieve dep_1 as the top hit
    assert len(res) == 1
    assert res[0][1]["deployment_id"] == "dep_1"
