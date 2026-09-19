import time

import httpx

BASE_URL = "http://localhost:8000/api/v1"

def run_smoke_test():
    with httpx.Client(base_url=BASE_URL) as client:
        print("--- RUNNING SMOKE TEST ---")
        
        # 1. Health
        print("1. GET /health")
        r = client.get("/health")
        r.raise_for_status()
        print("✅", r.json())
        
        # 2. Create Project
        print("\n2. POST /projects")
        proj_data = {"repo": "infrashift/smoke-test", "environment": "dev", "owner": "tester", "awsEnvironment": "demo"}
        r = client.post("/projects", json=proj_data)
        r.raise_for_status()
        proj_id = r.json()["projectId"]
        print("✅ Created project:", proj_id)
        
        # 3. Get Project
        print(f"\n3. GET /projects/{proj_id}")
        r = client.get(f"/projects/{proj_id}")
        r.raise_for_status()
        print("✅", r.json()["repo"])
        
        # 4. Create Analysis
        print(f"\n4. POST /projects/{proj_id}/analyses")
        ana_data = {"prId": "100", "commitSha": "abc1234"}
        r = client.post(f"/projects/{proj_id}/analyses", json=ana_data)
        r.raise_for_status()
        ana_id = r.json()["analysisId"]
        print("✅ Created analysis:", ana_id)
        
        # Wait for background worker
        print("Waiting 2s for background worker...")
        time.sleep(2)
        
        # 5. Get Analysis
        print(f"\n5. GET /analyses/{ana_id}")
        r = client.get(f"/analyses/{ana_id}")
        r.raise_for_status()
        print("✅ Status:", r.json()["status"])
        
        # 6. Get Impact
        print(f"\n6. GET /analyses/{ana_id}/impact")
        r = client.get(f"/analyses/{ana_id}/impact")
        r.raise_for_status()
        print("✅", list(r.json().keys()))
        
        # 7. Get Forecast
        print(f"\n7. GET /analyses/{ana_id}/forecast")
        r = client.get(f"/analyses/{ana_id}/forecast")
        r.raise_for_status()
        print("✅", list(r.json().keys()))
        
        # 8. Get Evidence
        print(f"\n8. GET /analyses/{ana_id}/evidence")
        r = client.get(f"/analyses/{ana_id}/evidence")
        r.raise_for_status()
        print("✅", list(r.json().keys()))
        
        # 9. Get Recommendations
        print(f"\n9. GET /analyses/{ana_id}/recommendations")
        r = client.get(f"/analyses/{ana_id}/recommendations")
        r.raise_for_status()
        print("✅", list(r.json().keys()))
        
        # 10. Post Outcome
        print(f"\n10. POST /analyses/{ana_id}/outcome")
        out_data = {"actualCost": "+$20/mo", "actualPerformance": "Same", "deploymentResult": "SUCCESS"}
        r = client.post(f"/analyses/{ana_id}/outcome", json=out_data)
        r.raise_for_status()
        print("✅ Outcome recorded")
        
        # 11. Get History
        print(f"\n11. GET /projects/{proj_id}/history")
        r = client.get(f"/projects/{proj_id}/history")
        r.raise_for_status()
        print(f"✅ History count: {len(r.json())}")
        
        print("\n--- SMOKE TEST SUCCESSFUL ---")

if __name__ == "__main__":
    run_smoke_test()
