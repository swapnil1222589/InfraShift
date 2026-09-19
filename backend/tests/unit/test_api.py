from unittest.mock import patch

from app.core.config import settings


def test_full_project_analysis_flow(client):
    res_proj = client.post("/api/v1/projects", json={
        "repo": "test/integration",
        "environment": "staging",
        "owner": "dev",
        "awsEnvironment": "demo"
    })
    assert res_proj.status_code == 200
    proj = res_proj.json()
    assert proj["repo"] == "test/integration"
    project_id = proj["projectId"]
    
    res_get_proj = client.get(f"/api/v1/projects/{project_id}")
    assert res_get_proj.status_code == 200
    assert res_get_proj.json()["projectId"] == project_id
    
    res_ana = client.post(f"/api/v1/projects/{project_id}/analyses", json={
        "prId": "99",
        "commitSha": "xyz"
    })
    assert res_ana.status_code == 200
    ana = res_ana.json()
    assert ana["status"] == "PENDING"
    analysis_id = ana["analysisId"]
    
    res_get_ana = client.get(f"/api/v1/analyses/{analysis_id}")
    assert res_get_ana.status_code == 200
    completed_ana = res_get_ana.json()
    assert completed_ana["status"] == "COMPLETED"
    
    res_out = client.post(f"/api/v1/analyses/{analysis_id}/outcome", json={
        "actualCost": "+$15/mo",
        "actualPerformance": "Same",
        "deploymentResult": "SUCCESS"
    })
    assert res_out.status_code == 200
    
    res_hist = client.get(f"/api/v1/projects/{project_id}/history")
    assert res_hist.status_code == 200
    assert len(res_hist.json()) > 0

def test_webhook_idempotency(client):
    payload = {
        "action": "opened",
        "pull_request": {"number": 55, "head": {"sha": "idemp123"}},
        "repository": {"full_name": "test/idempo", "owner": {"login": "usr"}}
    }
    
    res1 = client.post("/api/v1/github/webhook", json=payload)
    assert res1.status_code == 200
    
    client.post("/api/v1/projects", json={
        "repo": "test/idempo",
        "environment": "dev",
        "owner": "usr",
        "awsEnvironment": "demo"
    })
    
    res2 = client.post("/api/v1/github/webhook", json=payload)
    assert res2.status_code == 200

def test_invalid_webhook_signature(client):
    original_secret = settings.GITHUB_WEBHOOK_SECRET
    settings.GITHUB_WEBHOOK_SECRET = "secret123"
    settings.MOCK_GITHUB = False
    
    try:
        payload = b'{"action": "opened"}'
        res = client.post("/api/v1/github/webhook", content=payload, headers={"X-Hub-Signature-256": "sha256=invalid"})
        assert res.status_code == 403
    finally:
        settings.GITHUB_WEBHOOK_SECRET = original_secret
        settings.MOCK_GITHUB = True
        
def test_failed_analysis_worker(client):
    with patch("app.workers.analysis_worker.analyze_impact", side_effect=ValueError("AI error")):
        res_proj = client.post("/api/v1/projects", json={
            "repo": "test/fail",
            "environment": "staging",
            "owner": "dev",
            "awsEnvironment": "demo"
        })
        project_id = res_proj.json()["projectId"]
        
        res_ana = client.post(f"/api/v1/projects/{project_id}/analyses", json={
            "prId": "1",
            "commitSha": "111"
        })
        
        analysis_id = res_ana.json()["analysisId"]
        res_get = client.get(f"/api/v1/analyses/{analysis_id}")
        assert res_get.json()["status"] == "FAILED"
        assert res_get.json()["error"] == "AI error"
