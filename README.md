# InfraShift

Predict the infrastructure impact of your code before production.

## Project Overview
InfraShift is an AWS-native pre-deployment infrastructure impact intelligence platform. It analyzes GitHub Pull Requests to detect changed components, cross-references them against real AWS infrastructure/telemetry, and utilizes AI to forecast cost and performance impacts *before* deployment.

## Problem Statement
Deploying code changes can have unintended consequences on cloud infrastructure costs and performance. Developers often lack visibility into these impacts during the PR review phase.

## Solution
By automatically analyzing PRs and fetching real AWS CloudWatch metrics, InfraShift empowers teams with a strict, evidence-based AI forecast of the deployment's impact.

## Architecture
- **GitHub**: Triggers webhooks on PRs.
- **Backend (FastAPI)**: Orchestrates the analysis, persists data, and serves the UI.
- **AI/Forecasting**: LLM-driven impact analysis using AWS telemetry context.
- **AWS Infrastructure**: DynamoDB for storage, CloudWatch for real-time read-only metrics.
- **Frontend**: React/Vite dashboard for visualization.

## Team Ownership
- **Person 1**: AI/Forecasting
- **Person 2**: AWS/Infrastructure
- **Person 3**: Backend/Data Engineering
- **Person 4**: Frontend UI/UX

## Status
- **Backend**: MVP ready for team integration.
- **AWS Integration**: Read-only Boto3 integration built. *Real AWS integration requires configured AWS credentials and AWS resources.*
- **AI Integration**: Strict Pydantic interface defined and mocked.
- **Frontend Integration**: API v1 published with Swagger docs.

## Quick Start (Local Backend)
```bash
cd backend
python -m venv venv
# Windows: .\\venv\\Scripts\\activate | Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Backend API & Testing
- **Swagger URL**: `http://localhost:8000/docs`
- **Testing**: Run `pytest` inside the `backend` folder.

## Environment Variables
See `backend/.env.example`. Controls include `LOCAL_MODE`, `LIVE_AWS`, `MOCK_AI`, and `MOCK_GITHUB`.
