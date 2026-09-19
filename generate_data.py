import random
import datetime
import json
import os

def generate_synthetic_deployments(count=50):
    deployments = []
    change_types = [
        "lambda_memory_increase", "lambda_memory_decrease", 
        "dynamodb_capacity_increase", "api_gateway_caching_enable"
    ]
    for i in range(count):
        dep_id = f"dep_{i+100}"
        change_type = random.choice(change_types)
        deployment = {
            "deployment_id": dep_id,
            "timestamp": (datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 365))).isoformat(),
            "resource_type": "",
            "resource_id": "",
            "change_type": change_type,
            "details": {},
            "baseline_metrics": {},
            "observed_metrics": {}
        }
        
        if change_type == "lambda_memory_increase":
            deployment["resource_type"] = "lambda"
            deployment["resource_id"] = f"payment-func-{random.randint(1,5)}"
            old_mem = random.choice([128, 256, 512])
            new_mem = old_mem * 2
            deployment["details"] = {"old_memory_mb": old_mem, "new_memory_mb": new_mem}
            baseline_lat = random.uniform(200.0, 500.0)
            baseline_cost = random.uniform(10.0, 50.0)
            deployment["baseline_metrics"] = {
                "latency_p95_ms": baseline_lat,
                "cost_usd": baseline_cost,
                "invocations": random.uniform(10000, 50000)
            }
            lat_drop = random.uniform(0.1, 0.3)
            cost_inc = random.uniform(0.05, 0.2)
            deployment["observed_metrics"] = {
                "latency_p95_ms": baseline_lat * (1 - lat_drop),
                "cost_usd": baseline_cost * (1 + cost_inc),
                "invocations": deployment["baseline_metrics"]["invocations"] * random.uniform(0.95, 1.05)
            }
        elif change_type == "lambda_memory_decrease":
            deployment["resource_type"] = "lambda"
            deployment["resource_id"] = f"notification-func-{random.randint(1,3)}"
            old_mem = random.choice([1024, 2048])
            new_mem = old_mem // 2
            deployment["details"] = {"old_memory_mb": old_mem, "new_memory_mb": new_mem}
            baseline_lat = random.uniform(50.0, 150.0)
            baseline_cost = random.uniform(100.0, 300.0)
            deployment["baseline_metrics"] = {"latency_p95_ms": baseline_lat, "cost_usd": baseline_cost, "invocations": random.uniform(50000, 150000)}
            lat_inc = random.uniform(0.1, 0.4)
            cost_drop = random.uniform(0.1, 0.3)
            deployment["observed_metrics"] = {"latency_p95_ms": baseline_lat * (1 + lat_inc), "cost_usd": baseline_cost * (1 - cost_drop), "invocations": deployment["baseline_metrics"]["invocations"]}
        elif change_type == "dynamodb_capacity_increase":
            deployment["resource_type"] = "dynamodb"
            deployment["details"] = {"old_rcu": 100, "new_rcu": 500}
            deployment["baseline_metrics"] = {"latency_p95_ms": 20.0, "cost_usd": 50.0, "invocations": 1000}
            deployment["observed_metrics"] = {"latency_p95_ms": 18.0, "cost_usd": 70.0, "invocations": 1000}
        else:
            deployment["resource_type"] = "api_gateway"
            deployment["details"] = {"caching_enabled": True}
            deployment["baseline_metrics"] = {"latency_p95_ms": 150.0, "cost_usd": 20.0, "invocations": 200000}
            deployment["observed_metrics"] = {"latency_p95_ms": 50.0, "cost_usd": 22.0, "invocations": 200000}
            
        deployments.append(deployment)
    return deployments

os.makedirs('ai_engine/data', exist_ok=True)
with open('ai_engine/data/historical.json', 'w') as f:
    json.dump(generate_synthetic_deployments(50), f, indent=2)
