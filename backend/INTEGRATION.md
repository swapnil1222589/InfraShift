# InfraShift Backend Integration Contract

## PERSON 1 — AI/Forecasting

**Goal**: Swap `MOCK_AI=true` with a live inference API call in `app/services/ai_service.py`.

### Payload sent to you
The backend will aggregate GitHub and AWS context and pass you a dictionary:
```json
{
  "changed_files": ["src/lambda/handler.py"],
  "additions": 45,
  "deletions": 12,
  "aws_evidence": {
    "metric": "Invocations",
    "value": 1500,
    "is_mock": false,
    "insufficient_evidence": false
  }
}
```

### Response Expected (Strict Schema)
You must return a dictionary that exactly matches `AIResponseModel`:
```json
{
  "forecast": {
    "costRange": "+$10 to +$50/mo",
    "performanceRange": "No significant change expected"
  },
  "confidence": 0.85,
  "evidence": [{"source": "mock_cloudwatch", "metric": "cpu_utilization", "value": "45%"}],
  "assumptions": ["Traffic remains constant"],
  "recommendations": [
    {
      "action": "Monitor DynamoDB consumed capacity",
      "reason": "New query pattern might increase costs",
      "priority": "MEDIUM",
      "affectedResource": "DynamoDB Table"
    }
  ]
}
```

### Local Testing
Run the backend with `MOCK_AI=false`, hit `POST /api/v1/projects/{id}/analyses`, and check the backend logs for Pydantic validation errors.

---

## PERSON 2 — AWS/Infrastructure

**Goal**: Create real tables and connect the read-only metrics.

### DynamoDB Schema
- Table 1: `infrashift-projects`, Partition Key: `projectId` (String)
- Table 2: `infrashift-analyses`, Partition Key: `analysisId` (String)
- Table 3: `infrashift-audit-events`, Partition Key: `analysisId` (String)

### Permissions Needed by Backend Execution Role
- `dynamodb:PutItem`, `dynamodb:GetItem`, `dynamodb:Scan`
- `cloudwatch:GetMetricData`, `cloudwatch:ListMetrics`

### Verification
1. Ensure AWS credentials are in your environment (`~/.aws/credentials` or `AWS_ACCESS_KEY_ID`).
2. Run `pytest -m aws`.
3. Hit `GET /api/v1/health/aws` with `LIVE_AWS=true` in `.env`.
*NOTE: The backend is currently running without live AWS verification since it was built in a local sandbox.*

---

## PERSON 4 — Frontend

**Goal**: Integrate the React dashboard with the API.

### Environment variables
Backend CORS requires `FRONTEND_ORIGINS` (e.g., `FRONTEND_ORIGINS=["http://localhost:5173"]`).

### API Endpoints
Base URL: `http://localhost:8000/api/v1` (Production URL: `https://api.infrashift.example.com/api/v1` - Placeholder)

- `GET /health`
- `POST /projects`
- `GET /projects/{id}`
- `GET /projects/{id}/history`
- `POST /projects/{id}/analyses`
- `GET /analyses/{id}` (Poll this! Status will transition `PENDING` -> `RUNNING` -> `COMPLETED` | `FAILED`)
- `GET /analyses/{id}/impact`
- `GET /analyses/{id}/forecast`
- `GET /analyses/{id}/evidence`
- `GET /analyses/{id}/recommendations`
- `POST /analyses/{id}/outcome`

### Workflow
1. When a PR arrives, backend creates an analysis (Status `PENDING`).
2. Frontend polls `GET /analyses/{id}` every 2 seconds.
3. If `COMPLETED`, UI renders the Forecast and Recommendations.
4. If `FAILED`, UI renders `analysis.error` string.
