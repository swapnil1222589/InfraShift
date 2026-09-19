# InfraShift Backend

## What is InfraShift?

InfraShift predicts the potential infrastructure impact of a code change **before** it reaches production. It analyzes GitHub Pull Requests, collects AWS evidence and CloudWatch telemetry, runs AI-powered impact forecasting, and returns structured risk assessments with actionable recommendations.

```
GitHub Pull Request
      ↓
Changed files / code changes
      ↓
InfraShift Backend
      ↓
AWS infrastructure evidence
      ↓
CloudWatch telemetry
      ↓
AI analysis / forecasting
      ↓
Infrastructure impact
      ↓
Confidence + uncertainty
      ↓
Recommendations
      ↓
Controlled deployment outcome
      ↓
Historical analysis
```

---

## Architecture

```
app/
├── api/           # FastAPI routers (health, projects, analyses, github)
├── core/          # Config, logging, errors, security
├── models/        # DynamoDB storage models (ProjectModel, AnalysisModel, AuditEventModel)
├── schemas/       # Pydantic v2 request/response schemas
├── repositories/  # Data access layer (local in-memory + DynamoDB)
├── services/      # Business logic (project, analysis, github, aws, cloudwatch, ai, evidence, outcome)
└── workers/       # Background analysis pipeline (AnalysisWorker)
```

**Data flow:**
1. REST API receives request → validates with Pydantic
2. Service layer executes business logic
3. Repository layer persists to DynamoDB (or in-memory in local mode)
4. Background worker runs async analysis pipeline
5. Worker stores structured results back to repository

---

## Features

- **GitHub Integration** — PR metadata, changed files via GitHub REST API (mock or real)
- **Webhook Support** — GitHub `pull_request` events with HMAC-SHA256 signature validation
- **Idempotency** — Duplicate webhooks/API calls return existing analysis (no duplicate processing)
- **AWS Evidence** — Read-only Lambda resource discovery (mock or real boto3)
- **CloudWatch Telemetry** — 7-day lookback for Invocations, Errors, Duration metrics
- **AI Analysis** — Structured impact/forecast/recommendations via pluggable AI service
- **Audit Trail** — Every pipeline step emits a typed audit event
- **Outcome Tracking** — Record actual deployment results for historical comparison
- **Structured Errors** — All API errors follow `{"error": {"code", "message", "request_id"}}` format
- **Request IDs** — Every request gets a traceable `X-Request-ID`

---

## Tech Stack

| Component | Library |
|-----------|---------|
| Web framework | FastAPI + Uvicorn |
| Validation | Pydantic v2 |
| Configuration | pydantic-settings |
| HTTP client | httpx |
| AWS SDK | boto3 |
| GitHub SDK | httpx (direct REST) |
| Retries | tenacity |
| Testing | pytest + pytest-asyncio + pytest-cov |
| Linting | Ruff |

---

## Project Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI app, middleware, routers
│   ├── dependencies.py            # DI providers
│   ├── api/
│   │   ├── health.py              # GET /health, GET /health/aws
│   │   ├── projects.py            # POST/GET /projects
│   │   ├── analyses.py            # GET /analyses/{id}/* endpoints
│   │   └── github.py              # POST /github/webhook
│   ├── core/
│   │   ├── config.py              # Pydantic Settings
│   │   ├── logging.py             # Structured logging
│   │   ├── errors.py              # Error classes + handlers
│   │   └── security.py            # HMAC validation, request IDs
│   ├── models/                    # Storage models (DynamoDB/in-memory)
│   ├── schemas/                   # Pydantic request/response schemas
│   ├── repositories/              # Repository pattern: local + DynamoDB
│   ├── services/                  # Business logic services
│   └── workers/
│       └── analysis_worker.py     # Full 13-step analysis pipeline
├── tests/                         # pytest test suite (92 tests)
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── pytest.ini
├── pyproject.toml
├── Dockerfile
└── smoke_test.py
```

---

## Local Setup

### Prerequisites
- Python 3.11+

### 1. Clone and enter the backend directory
```bash
cd infrashift-backend/backend
```

### 2. Create a virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements-dev.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# No changes needed for local mode — defaults work as-is
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | `InfraShift` | Application name |
| `ENVIRONMENT` | `development` | Environment name |
| `LOG_LEVEL` | `INFO` | Logging level |
| `LOCAL_MODE` | `true` | Use in-memory storage (no AWS needed) |
| `LIVE_AWS` | `false` | Use real DynamoDB/CloudWatch |
| `MOCK_AI` | `true` | Use deterministic mock AI |
| `MOCK_GITHUB` | `true` | Use mock GitHub data |
| `AWS_REGION` | `us-east-1` | AWS region |
| `DYNAMODB_PROJECTS_TABLE` | `infrashift-projects` | DynamoDB projects table |
| `DYNAMODB_ANALYSES_TABLE` | `infrashift-analyses` | DynamoDB analyses table |
| `DYNAMODB_AUDIT_TABLE` | `infrashift-audit-events` | DynamoDB audit table |
| `GITHUB_TOKEN` | _(empty)_ | GitHub personal access token (for MOCK_GITHUB=false) |
| `GITHUB_WEBHOOK_SECRET` | _(empty)_ | Webhook HMAC secret (recommended for production) |
| `FRONTEND_ORIGINS` | `http://localhost:3000,http://localhost:5173` | CORS origins |
| `GITHUB_TIMEOUT_SECONDS` | `10` | GitHub API timeout |
| `AWS_TIMEOUT_SECONDS` | `10` | AWS API timeout |
| `AI_TIMEOUT_SECONDS` | `30` | AI service timeout |
| `CLOUDWATCH_LOOKBACK_DAYS` | `7` | CloudWatch metric lookback |
| `AUTO_CREATE_PROJECT` | `false` | Auto-create projects from webhooks |

---

## Running the Server

### Local Mode (default — no AWS credentials needed)
```bash
uvicorn app.main:app --reload --port 8000
```

### Live AWS Mode
```bash
LOCAL_MODE=false LIVE_AWS=true MOCK_AI=false MOCK_GITHUB=false \
  uvicorn app.main:app --reload --port 8000
```

---

## Swagger

Interactive API docs available at: **http://localhost:8000/docs**

OpenAPI schema: **http://localhost:8000/openapi.json**

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/health` | Basic health check |
| `GET` | `/api/v1/health/aws` | AWS connectivity check |
| `POST` | `/api/v1/projects` | Create a project |
| `GET` | `/api/v1/projects/{project_id}` | Get project by ID |
| `GET` | `/api/v1/projects/{project_id}/history` | Get analysis history |
| `POST` | `/api/v1/projects/{project_id}/analyses` | Create and queue analysis |
| `GET` | `/api/v1/analyses/{analysis_id}` | Get full analysis |
| `GET` | `/api/v1/analyses/{analysis_id}/impact` | Get infrastructure impact |
| `GET` | `/api/v1/analyses/{analysis_id}/forecast` | Get forecast |
| `GET` | `/api/v1/analyses/{analysis_id}/evidence` | Get collected evidence |
| `GET` | `/api/v1/analyses/{analysis_id}/recommendations` | Get recommendations |
| `POST` | `/api/v1/analyses/{analysis_id}/outcome` | Record deployment outcome |
| `POST` | `/api/v1/github/webhook` | GitHub webhook receiver |

---

## GitHub Integration

### Mock Mode (default)
No token needed. Returns realistic demo data marked `is_mock: true`.

### Real Mode
Set in `.env`:
```bash
MOCK_GITHUB=false
GITHUB_TOKEN=ghp_your_token_here
```

Requires `repo` read scope on the GitHub token.

---

## Webhooks

Configure in your GitHub repository → Settings → Webhooks:
- **Payload URL**: `https://your-server/api/v1/github/webhook`
- **Content type**: `application/json`
- **Events**: Pull requests
- **Secret**: Set `GITHUB_WEBHOOK_SECRET` in your environment

The webhook creates an analysis automatically when a PR is opened/synchronized/reopened. Duplicate events (same PR + commit SHA) are safely ignored.

> **Important**: A project with the matching `repo_url` must exist first (create via `POST /api/v1/projects`), or set `AUTO_CREATE_PROJECT=true`.

---

## DynamoDB

### Tables Required (LIVE_AWS=true)
| Table | Partition Key |
|-------|--------------|
| `infrashift-projects` | `project_id` (String) |
| `infrashift-analyses` | `analysis_id` (String) |
| `infrashift-audit-events` | `event_id` (String) |

### Minimum IAM Permissions
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/infrashift-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:GetMetricData",
        "cloudwatch:ListMetrics"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": ["lambda:ListFunctions"],
      "Resource": "*"
    }
  ]
}
```

---

## CloudWatch

The backend reads CloudWatch metrics for Lambda functions over the past 7 days:
- `Invocations` (Sum)
- `Errors` (Sum)
- `Duration` (Average)

All CloudWatch calls are **read-only**. If no data exists for a function, `insufficient_evidence: true` is returned — never fabricated values.

---

## AI Integration

### Mock AI (default)
Returns deterministic realistic analysis. All output marked `is_mock: true`.

### Real AI Adapter
The `AIService` uses a `Protocol` interface defined in `app/services/ai_service.py`. To integrate:
1. Implement `RealAIService.analyze(context: dict) -> AIResponseModel` in `app/services/ai_service.py`
2. Set `MOCK_AI=false`
3. All AI output is **validated by Pydantic** before use — invalid AI responses are rejected

See `INTEGRATION.md` for full API contract.

---

## Testing

```bash
# Run all tests (no AWS credentials needed)
pytest

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Run only AWS tests (requires LIVE_AWS=true)
pytest -m aws
```

**Test coverage**: 92 tests across 11 test modules.

---

## Docker

```bash
# Build
docker build -t infrashift-backend .

# Run (local mode)
docker run -p 8000:8000 \
  -e LOCAL_MODE=true \
  -e MOCK_AI=true \
  -e MOCK_GITHUB=true \
  infrashift-backend

# Run (live AWS mode)
docker run -p 8000:8000 \
  -e LOCAL_MODE=false \
  -e LIVE_AWS=true \
  -e MOCK_AI=false \
  -e MOCK_GITHUB=false \
  -e GITHUB_TOKEN=ghp_... \
  -e AWS_REGION=us-east-1 \
  infrashift-backend
```

> The Dockerfile **never** copies `.env` into the image. All secrets come from environment variables at runtime.

---

## Security

- **No hardcoded credentials** anywhere in source code
- **Webhook signature validation** using HMAC-SHA256 + constant-time comparison
- **CORS** restricted to `FRONTEND_ORIGINS` — not `*`
- **Request IDs** on every request for traceability
- **Error messages** never expose Python tracebacks or internal paths
- **AWS operations** are read-only — no create/delete/deploy operations
- **GitHub token** never logged

---

## AWS Deployment

For production deployment on AWS:

1. **ECS Fargate** or **Lambda** — containerize with provided Dockerfile
2. **Secrets Manager** — store `GITHUB_TOKEN`, `GITHUB_WEBHOOK_SECRET`
3. **DynamoDB** — provision the three tables (On-Demand billing recommended)
4. **IAM Role** — attach the minimum permission policy above
5. **API Gateway** — front the service with HTTPS
6. **CloudWatch Logs** — structured logs are written to stdout

> **NOTE**: Live AWS connectivity has not been verified in CI. DynamoDB and CloudWatch integration is designed to work with real AWS but has only been tested with the in-memory local implementation.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ANALYSIS_ALREADY_EXISTS` on webhook | Normal — idempotency working correctly |
| Analysis stuck in `RUNNING` | Worker ran before startup; restart is safe |
| `FORECAST_NOT_AVAILABLE` | Analysis not yet COMPLETED — poll status first |
| DynamoDB `ResourceNotFoundException` | Create tables first or set `LOCAL_MODE=true` |
| `403` on webhook | Check `GITHUB_WEBHOOK_SECRET` matches GitHub config |
| `429` from GitHub API | Token rate-limited; retries with backoff are automatic |
