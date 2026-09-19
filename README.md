# InfraShift

## Problem

Engineering teams deploy code changes without knowing their infrastructure impact until **after** an incident occurs. Manual risk assessment is slow, error-prone, and doesn't scale with CI/CD velocity.

## Solution

InfraShift analyzes a GitHub Pull Request **before** deployment and returns:
- Predicted infrastructure risk (Low/Medium/High/Critical)
- AI-powered forecast (invocations, latency, error rate changes)
- Recommended actions with evidence
- Confidence scores with uncertainty flags

## Architecture

```
GitHub PR  →  InfraShift Backend  →  AI Analysis  →  Risk Report
                     ↕
              AWS Evidence + CloudWatch
```

## Team Roles

| Role | Responsibility |
|------|---------------|
| **Team Lead / Backend & Data** | REST API, GitHub integration, analysis pipeline, AWS/DynamoDB, testing |
| **AWS / Infrastructure** | DynamoDB tables, IAM policies, CloudWatch integration, AWS resource discovery |
| **AI / Forecasting** | Real AI adapter (Bedrock/Strands), impact models, confidence tuning |
| **Frontend / Developer Experience** | React UI, PR widgets, analysis dashboard, GitHub App |

## Backend Status

- [x] FastAPI REST API with all required endpoints
- [x] GitHub webhook with HMAC-SHA256 validation
- [x] Idempotent analysis creation
- [x] Analysis pipeline worker (GitHub → AWS → CloudWatch → AI)
- [x] Mock implementations for all external services
- [x] DynamoDB + local in-memory repositories
- [x] Structured audit logging
- [x] Deployment outcome recording
- [x] 92 passing tests
- [x] Ruff linting clean

## Local Setup

```bash
cd infrashift-backend/backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
```

Then visit: **http://localhost:8000/docs**

## Integration

See [backend/INTEGRATION.md](backend/INTEGRATION.md) for full API contracts and integration guide.
