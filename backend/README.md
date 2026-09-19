# InfraShift Backend MVP

## Architecture & Integration
The backend serves as the orchestration layer between GitHub (Webhooks), AWS (CloudWatch, DynamoDB), and the AI Forecasting layer.

### Workflow
1. **GitHub PR Webhook** hits `/github/webhook`.
2. Backend parses repo, PR, and commit. Idempotency checks prevent duplicates.
3. Analysis job is spawned.
4. **GitHub Service** fetches changed files.
5. **CloudWatch Service** fetches metrics for affected resources.
6. **AI Service** generates a forecast and recommendations.
7. Results are persisted to **DynamoDB**.

## Local Setup
```bash
python -m venv venv
# On Windows: .\venv\Scripts\activate
# On Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Environment Variables
- `LOCAL_MODE`: (true/false) Still present, but AWS connections now rely entirely on `LIVE_AWS`.
- `LIVE_AWS`: (true/false) Controls whether the backend connects to real AWS CloudWatch and DynamoDB. Defaults to false. NEVER enable locally unless you have valid credentials in your environment.
- `MOCK_GITHUB`: (true/false) If true, bypasses real GitHub PR API fetches and signature validation.
- `MOCK_AI`: (true/false) If true, bypasses real AI model and uses hard-coded response.
- `AWS_REGION`: AWS region (e.g. `us-east-1`).
- `GITHUB_WEBHOOK_SECRET`: HMAC signature for webhooks.

## DynamoDB Setup
When `LOCAL_MODE=false`, these tables are required:
- `infrashift-projects` (Partition Key: `projectId` String)
- `infrashift-analyses` (Partition Key: `analysisId` String)
- `infrashift-audit-events` (Partition Key: `analysisId` String)

## CloudWatch IAM Permissions
The role running this backend needs `cloudwatch:GetMetricData` to read metrics.

## API Examples
Check `/docs` on the running server for interactive Swagger UI.

### Create Project
`POST /projects`
```json
{
  "repo": "owner/repo",
  "environment": "development",
  "owner": "user",
  "awsEnvironment": "demo"
}
```

### Get Analysis
`GET /analyses/{analysisId}`
