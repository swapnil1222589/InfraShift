"""Analysis worker — orchestrates the full analysis pipeline."""
from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from app.core.config import settings
from app.models.analysis import AnalysisModel
from app.models.audit import AuditEventModel
from app.repositories.analysis_repository import analysis_repository
from app.repositories.audit_repository import audit_repository
from app.repositories.project_repository import project_repository
from app.schemas.analysis import AnalysisStatus
from app.services.ai_service import ai_service
from app.services.evidence_service import evidence_service

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Audit helpers
# ---------------------------------------------------------------------------


async def _audit(
    event_type: str,
    project_id: str | None = None,
    analysis_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    event = AuditEventModel(
        event_id=str(uuid.uuid4()),
        project_id=project_id,
        analysis_id=analysis_id,
        event_type=event_type,
        timestamp=datetime.now(UTC),
        metadata=metadata or {},
    )
    try:
        await audit_repository.save(event)
    except Exception:  # noqa: BLE001
        logger.warning("Failed to write audit event: %s", event_type)


# ---------------------------------------------------------------------------
# Main worker
# ---------------------------------------------------------------------------


class AnalysisWorker:
    """
    Executes the full analysis pipeline for a given analysis_id.

    Steps:
      1.  Load analysis + project
      2.  Transition → RUNNING
      3.  Fetch GitHub files/metadata (with timeout)
      4.  Collect AWS infrastructure evidence
      5.  Collect CloudWatch metrics (with timeout)
      6.  Build analysis context for AI
      7.  Call AIService (with timeout)
      8.  Validate AIResponseModel (Pydantic ensures this)
      9.  Build ImpactResponse schema
      10. Build ForecastResponse schema
      11. Build Recommendation schemas
      12. Save impact / forecast / evidence / recommendations to model
      13. Transition → COMPLETED
      14. Write audit events throughout

    On any unrecoverable failure:
      - Transition → FAILED with safe error message
      - Write ANALYSIS_FAILED audit event
    """

    async def run(self, analysis_id: str) -> None:
        logger.info("Worker starting: analysis_id=%s", analysis_id)

        # Step 1: Load analysis
        model = await analysis_repository.get(analysis_id)
        if not model:
            logger.error("Analysis not found in worker: %s", analysis_id)
            return

        if model.status != AnalysisStatus.QUEUED:
            logger.warning(
                "Worker called for non-QUEUED analysis %s (status=%s)",
                analysis_id,
                model.status,
            )
            return

        # Load project for repo info
        project = await project_repository.get(model.project_id)
        if not project:
            logger.error("Project not found for analysis: project_id=%s", model.project_id)
            await self._fail(model, "Project not found")
            return

        # Step 2: Transition → RUNNING
        await self._set_running(model)
        await _audit(
            "ANALYSIS_STARTED",
            project_id=model.project_id,
            analysis_id=analysis_id,
            metadata={"pr_number": model.pr_number, "commit_sha": model.commit_sha},
        )

        try:
            # Step 3: GitHub evidence
            repo_parts = project.repo_url.rstrip("/").split("/")
            repo_full_name = f"{repo_parts[-2]}/{repo_parts[-1]}"

            pr_files, github_evidence = await asyncio.wait_for(
                evidence_service.collect_github_evidence(repo_full_name, model.pr_number),
                timeout=float(settings.GITHUB_TIMEOUT_SECONDS),
            )
            await _audit(
                "GITHUB_FETCHED",
                project_id=model.project_id,
                analysis_id=analysis_id,
                metadata={"file_count": len(pr_files)},
            )

            # Step 4: AWS evidence (async method wrapping sync boto3)
            repo_name = repo_parts[-1]
            aws_evidence = await asyncio.wait_for(
                evidence_service.collect_aws_evidence(repo_name),
                timeout=float(settings.AWS_TIMEOUT_SECONDS),
            )
            await _audit(
                "AWS_EVIDENCE_COLLECTED",
                project_id=model.project_id,
                analysis_id=analysis_id,
                metadata={"resource_count": len(aws_evidence)},
            )

            # Step 5: CloudWatch metrics
            function_name = f"{repo_name}-handler"
            cw_evidence = await asyncio.wait_for(
                evidence_service.collect_cloudwatch_evidence(function_name),
                timeout=float(settings.AWS_TIMEOUT_SECONDS),
            )
            await _audit(
                "CLOUDWATCH_COLLECTED",
                project_id=model.project_id,
                analysis_id=analysis_id,
                metadata={"metric_count": len(cw_evidence)},
            )

            all_evidence = github_evidence + aws_evidence + cw_evidence

            # Step 6: Build AI context
            changed_filenames = [f["filename"] for f in pr_files] if pr_files else []
            context: dict[str, Any] = {
                "project_id": project.project_id,
                "project_name": project.name,
                "repo_url": project.repo_url,
                "pr_number": model.pr_number,
                "commit_sha": model.commit_sha,
                "changed_files": changed_filenames,
                "total_additions": sum(f.get("additions", 0) for f in pr_files),
                "total_deletions": sum(f.get("deletions", 0) for f in pr_files),
                "aws_evidence": [e.model_dump(mode="json") for e in aws_evidence],
                "cloudwatch_evidence": [e.model_dump(mode="json") for e in cw_evidence],
            }

            # Step 7: AI analysis (already validated by Pydantic inside MockAIService/RealAIService)
            ai_response = await asyncio.wait_for(
                ai_service.analyze(context),
                timeout=float(settings.AI_TIMEOUT_SECONDS),
            )
            await _audit(
                "AI_ANALYSIS_COMPLETED",
                project_id=model.project_id,
                analysis_id=analysis_id,
                metadata={
                    "confidence": ai_response.confidence,
                    "is_mock": ai_response.is_mock,
                    "overall_risk": ai_response.impact.overall_risk,
                },
            )

            # Step 9: Build ImpactResponse
            from app.schemas.impact import (  # noqa: PLC0415
                AffectedResource,
                ImpactCategories,
                ImpactResponse,
                RiskLevel,
            )

            affected_resources = [
                AffectedResource(
                    resource_type=r["resource_type"],
                    resource_id=r["resource_id"],
                    change_type=r.get("change_type", "modified"),
                    impact=RiskLevel(r.get("impact", "low")),
                )
                for r in ai_response.impact.affected_resources
            ]

            cats = ai_response.impact.categories
            impact = ImpactResponse(
                analysis_id=analysis_id,
                overall_risk=RiskLevel(ai_response.impact.overall_risk),
                affected_resources=affected_resources,
                categories=ImpactCategories(
                    compute=RiskLevel(cats.get("compute", "low")),
                    database=RiskLevel(cats.get("database", "low")),
                    network=RiskLevel(cats.get("network", "low")),
                    api=RiskLevel(cats.get("api", "low")),
                ),
                is_mock=ai_response.is_mock,
            )

            # Step 10: Build ForecastResponse
            from app.schemas.forecast import ForecastResponse, MetricPrediction  # noqa: PLC0415

            predicted = {
                k: MetricPrediction(
                    direction=v.get("direction", "stable") if isinstance(v, dict) else v.direction,
                    percentage=v.get("percentage", 0.0) if isinstance(v, dict) else v.percentage,
                )
                for k, v in ai_response.forecast.predicted_impact.items()
            }
            forecast = ForecastResponse(
                analysis_id=analysis_id,
                predicted_impact=predicted,
                confidence=ai_response.forecast.confidence,
                time_horizon=ai_response.forecast.time_horizon,
                signals=ai_response.forecast.signals,
                uncertainty=ai_response.forecast.uncertainty,
                insufficient_evidence=ai_response.forecast.insufficient_evidence,
                is_mock=ai_response.is_mock,
            )

            # Step 11: Build Recommendations
            from app.schemas.recommendation import Priority, Recommendation  # noqa: PLC0415

            recommendations = [
                Recommendation(
                    id=r.id,
                    priority=Priority(r.priority),
                    category=r.category,
                    title=r.title,
                    description=r.description,
                    reason=r.reason,
                    evidence_refs=r.evidence_refs,
                )
                for r in ai_response.recommendations
            ]

            # Step 12: Save all results into model
            model.impact = impact.model_dump(mode="json")
            model.forecast = forecast.model_dump(mode="json")
            model.evidence = [e.model_dump(mode="json") for e in all_evidence]
            model.recommendations = [r.model_dump(mode="json") for r in recommendations]

            # Step 13: Transition → COMPLETED
            model.status = AnalysisStatus.COMPLETED
            model.completed_at = datetime.now(UTC)
            model.updated_at = datetime.now(UTC)
            await analysis_repository.save(model)

            await _audit(
                "ANALYSIS_COMPLETED",
                project_id=model.project_id,
                analysis_id=analysis_id,
                metadata={"overall_risk": str(impact.overall_risk)},
            )
            logger.info("Worker completed successfully: analysis_id=%s", analysis_id)

        except TimeoutError:
            msg = "External service timeout (GitHub/AWS/AI)"
            logger.error("Analysis %s timed out", analysis_id)
            await self._fail(model, msg)

        except Exception as exc:  # noqa: BLE001
            msg = str(exc)
            logger.exception("Analysis %s failed: %s", analysis_id, msg)
            await self._fail(model, msg)

    async def _set_running(self, model: AnalysisModel) -> None:
        model.status = AnalysisStatus.RUNNING
        model.updated_at = datetime.now(UTC)
        await analysis_repository.save(model)

    async def _fail(self, model: AnalysisModel, error_message: str) -> None:
        model.status = AnalysisStatus.FAILED
        model.error = error_message[:500]  # Truncate for safety — never expose full stack traces
        model.completed_at = datetime.now(UTC)
        model.updated_at = datetime.now(UTC)
        try:
            await analysis_repository.save(model)
        except Exception:  # noqa: BLE001
            logger.exception("Failed to save FAILED analysis: %s", model.analysis_id)

        await _audit(
            "ANALYSIS_FAILED",
            project_id=model.project_id,
            analysis_id=model.analysis_id,
            metadata={"error": error_message[:200]},
        )


# ---------------------------------------------------------------------------
# Module-level entry points
# ---------------------------------------------------------------------------

analysis_worker = AnalysisWorker()


async def run_analysis(analysis_id: str) -> None:
    """Background task entry point called by FastAPI BackgroundTasks."""
    await analysis_worker.run(analysis_id)
