def test_github_webhook(client):
    payload = {
        "action": "opened",
        "pull_request": {"number": 123, "head": {"sha": "abcdef123"}},
        "repository": {"full_name": "test/webhook-repo2", "owner": {"login": "test_user"}}
    }
    res = client.post("/api/v1/github/webhook", json=payload)
    assert res.status_code == 200
