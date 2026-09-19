"""Evidence collection service — aggregates GitHub, AWS, and CloudWatch evidence."""
from __future__ import annotations

import logging
from typing import Any

from app.schemas.evidence import EvidenceItem
from app.services.aws_service import aws_service
from app.services.cloudwatch_service import cloudwatch_service
from app.services.github_service import github_service

logger = logging.getLogger(__name__)


class EvidenceService:
    """Orchestrates evidence collection from all sources."""

    async def collect_github_evidence(
        self,
        repo_full_name: str,
        pr_number: int,
    ) -> tuple[list[dict[str, Any]], list[EvidenceItem]]:
        """
        Fetch PR files and build GitHub evidence items.

        Returns:
            (pr_files_raw, evidence_items)
        """
        pr_files = await github_service.get_pr_files(repo_full_name, pr_number)
        pr_meta = await github_service.get_pr_metadata(repo_full_name, pr_number)

        evidence_items: list[EvidenceItem] = [
            EvidenceItem(
                source="github",
                metric="changed_files",
                value=float(len(pr_files)),
                raw={
                    "files": [f["filename"] for f in pr_files],
                    "total_additions": sum(f.get("additions", 0) for f in pr_files),
                    "total_deletions": sum(f.get("deletions", 0) for f in pr_files),
                    "pr_title": pr_meta.get("title", ""),
                    "pr_author": pr_meta.get("author", ""),
                },
                is_mock=pr_meta.get("is_mock", False),
                insufficient_evidence=False,
            )
        ]

        return pr_files, evidence_items

    async def collect_aws_evidence(self, repo_name: str) -> list[EvidenceItem]:
        """Collect AWS infrastructure evidence."""
        return aws_service.get_lambda_resources(repo_name)

    async def collect_cloudwatch_evidence(
        self,
        function_name: str,
        days: int | None = None,
    ) -> list[EvidenceItem]:
        """Collect CloudWatch telemetry."""
        return await cloudwatch_service.get_lambda_metrics(function_name, days)


evidence_service = EvidenceService()
