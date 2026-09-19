"""InfraShift smoke test â€” verifies the full local workflow end-to-end."""
from __future__ import annotations

import sys
import time

import httpx

BASE_URL = "http://localhost:8000/api/v1"
MAX_POLL_SECONDS = 30
POLL_INTERVAL = 0.5


def check(condition: bool, msg: str) -> None:
    if not condition:
        print(f"  âŒ FAIL: {msg}")
        sys.exit(1)
    print(f"  âœ… {msg}")


def run_smoke_test() -> None:
    print("=" * 60)
    print("  InfraShift Smoke Test â€” Local Mode")
    print("=" * 60)

    with httpx.Client(base_url=BASE_URL, timeout=15) as client:

        # 1. Health check
        print("\n[1] GET /health")
        r = client.get("/health")
        check(r.status_code == 200, "Health check returns 200")
        data = r.json()
        check(data["status"] == "ok", f"Status is 'ok' (got {data['status']})")
        check(data["service"] == "infrashift-backend", "Service name is correct")
        print(f"      â†’ {data}")

        # 2. AWS health (local mode)
        print("\n[2] GET /health/aws")
        r = client.get("/health/aws")
        check(r.status_code == 200, "AWS health returns 200")
        data = r.json()
        check(data["status"] == "local", f"Status is 'local' in local mode (got {data['status']})")
        check(data["aws_enabled"] is False, "aws_enabled=false in local mode")

        # 3. Create project
        print("\n[3] POST /projects")
        proj_payload = {
            "name": "Smoke Test App",
            "repo_url": "https://github.com/example/smoke-test-app",
            "default_branch": "main",
            "aws_region": "us-east-1",
        }
        r = client.post("/projects", json=proj_payload)
        check(r.status_code == 201, f"Create project returns 201 (got {r.status_code})")
        proj = r.json()
        check("project_id" in proj, "Response has project_id")
        project_id = proj["project_id"]
        print(f"      â†’ project_id={project_id}")

        # 4. Get project
        print(f"\n[4] GET /projects/{project_id}")
        r = client.get(f"/projects/{project_id}")
        check(r.status_code == 200, "Get project returns 200")
        check(r.json()["project_id"] == project_id, "Project ID matches")

        # 5. Create analysis
        print(f"\n[5] POST /projects/{project_id}/analyses")
        ana_payload = {"pr_number": 42, "commit_sha": "abc1234def5678"}
        r = client.post(f"/projects/{project_id}/analyses", json=ana_payload)
        check(r.status_code == 202, f"Create analysis returns 202 (got {r.status_code})")
        ana = r.json()
        check("analysis_id" in ana, "Response has analysis_id")
        check(ana["status"] == "QUEUED", f"Initial status is QUEUED (got {ana['status']})")
        analysis_id = ana["analysis_id"]
        print(f"      â†’ analysis_id={analysis_id}")

        # 6. Poll analysis until completed
        print(f"\n[6] Polling GET /analyses/{analysis_id}...")
        deadline = time.time() + MAX_POLL_SECONDS
        final_status = None
        while time.time() < deadline:
            r = client.get(f"/analyses/{analysis_id}")
            check(r.status_code == 200, "Get analysis returns 200")
            final_status = r.json()["status"]
            if final_status in {"COMPLETED", "FAILED"}:
                break
            time.sleep(POLL_INTERVAL)

        check(final_status == "COMPLETED", f"Analysis COMPLETED (got {final_status})")
        print(f"      â†’ status={final_status}")

        # 7. Get impact
        print(f"\n[7] GET /analyses/{analysis_id}/impact")
        r = client.get(f"/analyses/{analysis_id}/impact")
        check(r.status_code == 200, f"Get impact returns 200 (got {r.status_code})")
        impact = r.json()
        check("overall_risk" in impact, "Impact has overall_risk")
        check("affected_resources" in impact, "Impact has affected_resources")
        check("categories" in impact, "Impact has categories")
        check(impact["is_mock"] is True, "Impact is marked is_mock=True in local mode")
        print(f"      â†’ overall_risk={impact['overall_risk']}, is_mock={impact['is_mock']}")

        # 8. Get forecast
        print(f"\n[8] GET /analyses/{analysis_id}/forecast")
        r = client.get(f"/analyses/{analysis_id}/forecast")
        check(r.status_code == 200, f"Get forecast returns 200 (got {r.status_code})")
        forecast = r.json()
        check("confidence" in forecast, "Forecast has confidence")
        check(0.0 <= forecast["confidence"] <= 1.0, f"Confidence in [0,1] (got {forecast['confidence']})")
        check("predicted_impact" in forecast, "Forecast has predicted_impact")
        check(forecast["is_mock"] is True, "Forecast is marked is_mock=True")
        print(f"      â†’ confidence={forecast['confidence']}, time_horizon={forecast.get('time_horizon')}")

        # 9. Get evidence
        print(f"\n[9] GET /analyses/{analysis_id}/evidence")
        r = client.get(f"/analyses/{analysis_id}/evidence")
        check(r.status_code == 200, f"Get evidence returns 200 (got {r.status_code})")
        evidence = r.json()
        check("items" in evidence, "Evidence has items")
        check(len(evidence["items"]) > 0, f"Evidence has at least 1 item (got {len(evidence['items'])})")
        print(f"      â†’ {len(evidence['items'])} evidence items")

        # 10. Get recommendations
        print(f"\n[10] GET /analyses/{analysis_id}/recommendations")
        r = client.get(f"/analyses/{analysis_id}/recommendations")
        check(r.status_code == 200, f"Get recommendations returns 200 (got {r.status_code})")
        recs = r.json()
        check("recommendations" in recs, "Response has recommendations")
        check(len(recs["recommendations"]) > 0, f"At least 1 recommendation (got {len(recs['recommendations'])})")
        print(f"      â†’ {len(recs['recommendations'])} recommendations")
        for rec in recs["recommendations"]:
            check(rec["priority"] in {"low", "medium", "high", "critical"}, f"Rec priority is valid (got {rec['priority']})")

        # 11. Idempotency â€” duplicate analysis returns 409
        print(f"\n[11] POST /projects/{project_id}/analyses (idempotency check)")
        r2 = client.post(f"/projects/{project_id}/analyses", json=ana_payload)
        check(r2.status_code == 409, f"Duplicate analysis returns 409 (got {r2.status_code})")
        check(r2.json()["error"]["code"] == "ANALYSIS_ALREADY_EXISTS", "Error code is ANALYSIS_ALREADY_EXISTS")

        # 12. Submit outcome
        print(f"\n[12] POST /analyses/{analysis_id}/outcome")
        outcome_payload = {
            "deployment_id": "deploy-smoke-001",
            "deployment_status": "success",
            "observed_metrics": {"invocations": 1500, "errors": 12, "duration_ms": 210},
            "notes": "Smoke test deployment",
        }
        r = client.post(f"/analyses/{analysis_id}/outcome", json=outcome_payload)
        check(r.status_code == 201, f"Submit outcome returns 201 (got {r.status_code})")
        outcome = r.json()
        check(outcome["analysis_id"] == analysis_id, "Outcome analysis_id matches")
        check(outcome["deployment_status"] == "success", "Outcome status is 'success'")
        check("outcome_id" in outcome, "Outcome has outcome_id")
        print(f"      â†’ outcome_id={outcome['outcome_id']}")

        # 13. Outcome appears in analysis
        print(f"\n[13] GET /analyses/{analysis_id} â€” verify outcome embedded")
        r = client.get(f"/analyses/{analysis_id}")
        check(r.status_code == 200, "Get analysis returns 200")
        full = r.json()
        check(full["outcome"] is not None, "Outcome embedded in analysis")
        check(full["outcome"]["deployment_id"] == "deploy-smoke-001", "Correct deployment_id")

        # 14. Project history
        print(f"\n[14] GET /projects/{project_id}/history")
        r = client.get(f"/projects/{project_id}/history")
        check(r.status_code == 200, f"Get history returns 200 (got {r.status_code})")
        history = r.json()
        check(len(history) > 0, f"History has at least 1 entry (got {len(history)})")
        check(any(a["analysis_id"] == analysis_id for a in history), "Analysis appears in history")
        check(any(a.get("outcome") is not None for a in history), "History entry has outcome")
        print(f"      â†’ {len(history)} analyses in history")

        # 15. Error handling â€” project not found
        print("\n[15] GET /projects/nonexistent â€” error handling")
        r = client.get("/projects/nonexistent-project")
        check(r.status_code == 404, f"Missing project returns 404 (got {r.status_code})")
        error = r.json()
        check("error" in error, "Error response has 'error' key")
        check("code" in error["error"], "Error has 'code'")
        check("message" in error["error"], "Error has 'message'")
        check("request_id" in error["error"], "Error has 'request_id'")
        check("Traceback" not in r.text, "No raw traceback exposed in error response")

    print("\n" + "=" * 60)
    print("  âœ… ALL SMOKE TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    run_smoke_test()
