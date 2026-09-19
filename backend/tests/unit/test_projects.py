def test_create_project(client):
    response = client.post("/api/v1/projects", json={
        "repo": "test/repo",
        "environment": "dev",
        "owner": "test",
        "awsEnvironment": "demo"
    })
    assert response.status_code == 200
    data = response.json()
    assert "projectId" in data
