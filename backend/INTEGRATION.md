# InfraShift — Integration Guide

## API Base URL

```
http://localhost:8000/api/v1
```

---

## Integration Overview

```
Person 1 (AI/Forecasting)
  → Implements RealAIService.analyze() in app/services/ai_service.py
  → Input: analysis context dict
  → Output: AIResponseModel (validated by Pydantic)

Person 2 (AWS/Infrastructure)
  → Configures LIVE_AWS=true, DynamoDB tables, IAM roles
  → Implements additional resource types in aws_service.py
  → Verifies CloudWatch metrics collection

Person 4 (Frontend/DX)
  → Calls REST API endpoints documented below
  → Reads analysis_id from 202 response, polls /analyses/{id}
  → Displays impact, forecast, recommendations
```

---

## Environment Variables for Integration

```bash
# .env for local integration testing
LOCAL_MODE=true
LIVE_AWS=false
MOCK_AI=true          # Person 1: set false when Bedrock is connected
MOCK_GITHUB=true      # Set false with real GitHub token
GITHUB_TOKEN=         # Person 4: needed for real PR data
GITHUB_WEBHOOK_SECRET=
FRONTEND_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## Integration Sequence

```
1. Person 4 (Frontend) → POST /api/v1/projects  (register GitHub repo)
2. Person 4 (Frontend) → POST /api/v1/projects/{id}/analyses  (trigger analysis)
3. Backend worker runs automatically:
      → GitHub evidence (Person 4: MOCK_GITHUB=false for real data)
      → AWS evidence (Person 2: LIVE_AWS=true for real AWS)
      → CloudWatch metrics (Person 2)
      → AI analysis (Person 1: MOCK_AI=false for real AI)
4. Person 4 polls GET /api/v1/analyses/{id} until status=COMPLETED
5. Person 4 fetches /impact, /forecast, /evidence, /recommendations
6. Person 4 submits POST /api/v1/analyses/{id}/outcome after deployment
```

---

## Person 1 — AI / Forecasting Integration

**File to implement**: `app/services/ai_service.py` → `RealAIService.analyze()`

**Input context** passed to `analyze()`:
```json
{
  "project_id": "uuid",
  "project_name": "My App",
  "repo_url": "https://github.com/example/my-app",
  "pr_number": 42,
  "commit_sha": "abc1234",
  "changed_files": ["src/handler.py", "template.yaml"],
  "total_additions": 45,
  "total_deletions": 12,
  "aws_evidence": [...],
  "cloudwatch_evidence": [...]
}
```

**Required output** — must be a valid `AIResponseModel`:
```json
{
  "impact": {
    "overall_risk": "medium",
    "affected_resources": [
      {
        "resource_type": "AWS::Lambda::Function",
        "resource_id": "my-app-handler",
        "change_type": "modified",
        "impact": "medium"
      }
    ],
    "categories": {
      "compute": "medium",
      "database": "low",
      "network": "low",
      "api": "medium"
    }
  },
  "forecast": {
    "predicted_impact": {
      "invocations": {"direction": "increase", "percentage": 15},
      "latency": {"direction": "increase", "percentage": 8},
      "errors": {"direction": "stable", "percentage": 0}
    },
    "confidence": 0.78,
    "time_horizon": "24h",
    "signals": ["Lambda handler modified"],
    "uncertainty": ["Limited telemetry"],
    "insufficient_evidence": false
  },
  "recommendations": [
    {
      "id": "rec-001",
      "priority": "high",
      "category": "observability",
      "title": "Enable enhanced monitoring",
      "description": "...",
      "reason": "...",
      "evidence_refs": ["cloudwatch:Invocations"]
    }
  ],
  "confidence": 0.78,
  "evidence_summary": ["14,520 invocations in 7 days"],
  "uncertainty": ["Traffic may vary"],
  "insufficient_evidence": false,
  "is_mock": false
}
```

**Allowed values:**
- `overall_risk`, `impact`: `"low"` | `"medium"` | `"high"` | `"critical"`
- `priority`: `"low"` | `"medium"` | `"high"` | `"critical"`
- `direction`: `"increase"` | `"decrease"` | `"stable"`
- `confidence`: float `[0.0, 1.0]`

**To activate**: Set `MOCK_AI=false` in your `.env`

---

## Person 2 — AWS / Infrastructure Integration

**Files to extend**:
- `app/services/aws_service.py` — add more resource types (API Gateway, S3, DynamoDB)
- `app/services/cloudwatch_service.py` — add more metrics or namespaces

**To activate**: Set in `.env`:
```bash
LIVE_AWS=true
LOCAL_MODE=false
AWS_REGION=us-east-1
```

**DynamoDB tables** to create:
```bash
aws dynamodb create-table \
  --table-name infrashift-projects \
  --attribute-definitions AttributeName=project_id,AttributeType=S \
  --key-schema AttributeName=project_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

aws dynamodb create-table \
  --table-name infrashift-analyses \
  --attribute-definitions AttributeName=analysis_id,AttributeType=S \
  --key-schema AttributeName=analysis_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

aws dynamodb create-table \
  --table-name infrashift-audit-events \
  --attribute-definitions AttributeName=event_id,AttributeType=S \
  --key-schema AttributeName=event_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

**Verify AWS health**:
```bash
curl http://localhost:8000/api/v1/health/aws
```

---

## Person 4 — Frontend / Developer Experience

### Create a Project

```http
POST /api/v1/projects
Content-Type: application/json

{
  "name": "My Application",
  "repo_url": "https://github.com/example/my-app",
  "default_branch": "main",
  "aws_region": "us-east-1"
}
```

**Response 201:**
```json
{
  "project_id": "uuid",
  "name": "My Application",
  "repo_url": "https://github.com/example/my-app",
  "default_branch": "main",
  "aws_region": "us-east-1",
  "created_at": "2026-09-19T...",
  "updated_at": "2026-09-19T..."
}
```

---

### Trigger Analysis

```http
POST /api/v1/projects/{project_id}/analyses
Content-Type: application/json

{
  "pr_number": 42,
  "commit_sha": "abc1234def5678"
}
```

**Response 202:**
```json
{
  "analysis_id": "uuid",
  "status": "QUEUED"
}
```

---

### Poll Analysis Status

```http
GET /api/v1/analyses/{analysis_id}
```

Poll until `status` is `COMPLETED` or `FAILED`. Recommended interval: 500ms–1s.

**Analysis statuses:** `QUEUED` → `RUNNING` → `COMPLETED` | `FAILED`

---

### Get Impact

```http
GET /api/v1/analyses/{analysis_id}/impact
```

```json
{
  "analysis_id": "uuid",
  "overall_risk": "medium",
  "affected_resources": [...],
  "categories": {
    "compute": "medium",
    "database": "low",
    "network": "low",
    "api": "medium"
  },
  "is_mock": true
}
```

---

### Get Forecast

```http
GET /api/v1/analyses/{analysis_id}/forecast
```

```json
{
  "analysis_id": "uuid",
  "predicted_impact": {
    "invocations": {"direction": "increase", "percentage": 15},
    "latency": {"direction": "increase", "percentage": 8},
    "errors": {"direction": "stable", "percentage": 0}
  },
  "confidence": 0.78,
  "time_horizon": "24h",
  "signals": ["Lambda handler modification detected"],
  "uncertainty": ["Limited telemetry"],
  "insufficient_evidence": false,
  "is_mock": true
}
```

---

### Get Recommendations

```http
GET /api/v1/analyses/{analysis_id}/recommendations
```

```json
{
  "analysis_id": "uuid",
  "recommendations": [
    {
      "id": "rec-001",
      "priority": "high",
      "category": "observability",
      "title": "Enable enhanced Lambda monitoring",
      "description": "Turn on Lambda Insights before deploying.",
      "reason": "Handler changes detected.",
      "evidence_refs": ["cloudwatch:Invocations"]
    }
  ]
}
```

---

### Record Deployment Outcome

```http
POST /api/v1/analyses/{analysis_id}/outcome
Content-Type: application/json

{
  "deployment_id": "deploy-001",
  "deployment_status": "success",
  "observed_metrics": {
    "invocations": 1500,
    "errors": 12,
    "duration_ms": 210
  },
  "notes": "Controlled rollout to 10%"
}
```

**deployment_status values:** `success` | `failure` | `partial` | `rollback`

---

### Get Project History

```http
GET /api/v1/projects/{project_id}/history
```

Returns array of all analyses for the project, including outcomes if recorded.

---

## Error Response Format

All errors follow this structure:

```json
{
  "error": {
    "code": "PROJECT_NOT_FOUND",
    "message": "Project not found: uuid",
    "request_id": "uuid"
  }
}
```

| HTTP Status | Error Code |
|-------------|------------|
| 404 | `PROJECT_NOT_FOUND`, `ANALYSIS_NOT_FOUND`, `IMPACT_NOT_AVAILABLE`, `FORECAST_NOT_AVAILABLE` |
| 409 | `PROJECT_ALREADY_EXISTS`, `ANALYSIS_ALREADY_EXISTS`, `INVALID_STATE_TRANSITION` |
| 401 | `UNAUTHORIZED` |
| 403 | `FORBIDDEN` |
| 422 | `VALIDATION_ERROR` |
| 503 | `SERVICE_UNAVAILABLE` |
| 500 | `INTERNAL_ERROR` |

---

## Notes on `is_mock` Fields

All response schemas include `is_mock: bool`. When running locally with `MOCK_AI=true` and `MOCK_GITHUB=true`, this will always be `true`. The frontend should surface this information so users know they're looking at demo data vs. real production analysis.

Never treat `is_mock: true` data as production measurements.
