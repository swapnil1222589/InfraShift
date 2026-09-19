def test_create_and_get_analysis(client):
    proj_res = client.post("/api/v1/projects", json={
        "repo": "test/repo2",
        "environment": "dev",
        "owner": "test",
        "awsEnvironment": "demo"
    })
    project_id = proj_res.json()["projectId"]
    
    ana_res = client.post(f"/api/v1/projects/{project_id}/analyses", json={
        "prId": "123",
        "commitSha": "abc1234"
    })
    assert ana_res.status_code == 200
    analysis_id = ana_res.json()["analysisId"]
    
    get_res = client.get(f"/api/v1/analyses/{analysis_id}")
    assert get_res.status_code == 200
    assert get_res.json()["analysisId"] == analysis_id
