"""GitHub webhook endpoint."""
from __future__ import annotations

import logging

from fastapi import APIRouter, BackgroundTasks, Request, status
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.errors import ConflictError, ForbiddenError, UnauthorizedError
from app.core.security import get_request_id, validate_github_signature
from app.repositories.project_repository import project_repository
from app.schemas.analysis import AnalysisCreate
from app.services.analysis_service import create_analysis
from app.workers.analysis_worker import run_analysis

logger = logging.getLogger(__name__)
router = APIRouter()

SUPPORTED_ACTIONS = {"opened", "synchronize", "reopened"}


@router.post("/webhook", summary="GitHub webhook receiver")
async def github_webhook(request: Request, background_tasks: BackgroundTasks) -> dict:
    request_id = get_request_id(request)
    payload_bytes = await request.body()

    # --- Signature validation ---
    if settings.GITHUB_WEBHOOK_SECRET:
        signature = request.headers.get("X-Hub-Signature-256", "")
        if not signature:
            logger.warning("Webhook missing signature [request_id=%s]", request_id)
            raise UnauthorizedError("Missing X-Hub-Signature-256 header")

        if not validate_github_signature(payload_bytes, signature, settings.GITHUB_WEBHOOK_SECRET):
            logger.warning("Webhook invalid signature [request_id=%s]", request_id)
            raise ForbiddenError("Invalid webhook signature")

    # --- Parse event type ---
    event_type = request.headers.get("X-GitHub-Event", "")

    if event_type != "pull_request":
        logger.info("Ignoring unsupported webhook event: %s", event_type)
        return {"status": "ignored", "reason": f"Unsupported event type: {event_type}"}

    # --- Parse payload ---
    try:
        data = await request.json()
    except Exception:  # noqa: BLE001
        return {"status": "ignored", "reason": "Invalid JSON payload"}

    action = data.get("action", "")
    if action not in SUPPORTED_ACTIONS:
        logger.info("Ignoring unsupported PR action: %s", action)
        return {"status": "ignored", "reason": f"Unsupported action: {action}"}

    pr = data.get("pull_request", {})
    repo = data.get("repository", {})

    repo_full_name = repo.get("full_name", "")
    pr_number = pr.get("number")
    commit_sha = pr.get("head", {}).get("sha", "")
    repo_html_url = repo.get("html_url", "")

    if not all([repo_full_name, pr_number, commit_sha]):
        logger.warning("Webhook missing required fields: repo=%s pr=%s sha=%s", repo_full_name, pr_number, commit_sha)
        return {"status": "ignored", "reason": "Missing required fields"}

    # Normalize repo URL
    if repo_html_url:
        repo_url = repo_html_url
    else:
        repo_url = f"https://github.com/{repo_full_name}"

    # --- Find project ---
    project_model = await project_repository.get_by_repo_url(repo_url)

    if not project_model:
        if settings.AUTO_CREATE_PROJECT:
            # Auto-create mode
            project_name = repo_full_name.split("/")[-1]
            from app.services.project_service import get_or_create_project_by_repo  # noqa: PLC0415
            project_resp = await get_or_create_project_by_repo(repo_url, project_name)
            project_id = project_resp.project_id
            logger.info("Auto-created project for webhook: project_id=%s", project_id)
        else:
            logger.info("No project found for repo '%s' — create a project first.", repo_url)
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "status": "not_found",
                    "reason": f"No project registered for repository: {repo_url}. Create a project first via POST /api/v1/projects.",
                },
            )
    else:
        project_id = project_model.project_id

    # --- Idempotency: don't create duplicate analyses ---
    analysis_in = AnalysisCreate(pr_number=pr_number, commit_sha=commit_sha)

    try:
        model = await create_analysis(project_id, analysis_in)
    except ConflictError as exc:
        logger.info("Idempotent webhook — returning existing analysis: %s", exc.message)
        return {
            "status": "duplicate",
            "reason": "Analysis already exists for this PR/commit",
        }

    background_tasks.add_task(run_analysis, model.analysis_id)

    logger.info(
        "Webhook queued analysis: analysis_id=%s project_id=%s pr=%d sha=%s",
        model.analysis_id, project_id, pr_number, commit_sha,
    )

    return {
        "status": "queued",
        "analysis_id": model.analysis_id,
        "project_id": project_id,
        "pr_number": pr_number,
        "commit_sha": commit_sha,
    }
