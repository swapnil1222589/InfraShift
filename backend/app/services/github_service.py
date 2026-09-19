"""GitHub service — real API and mock implementations."""
from __future__ import annotations

import logging
from typing import Any

import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from app.core.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Retryable exceptions
# ---------------------------------------------------------------------------


def _is_transient(exc: BaseException) -> bool:
    """Return True for transient errors that should be retried."""
    if isinstance(exc, httpx.TimeoutException):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code >= 500
    if isinstance(exc, httpx.NetworkError):
        return True
    return False


_retry_policy = retry(
    retry=retry_if_exception(_is_transient),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    reraise=True,
)


# ---------------------------------------------------------------------------
# Mock data
# ---------------------------------------------------------------------------

MOCK_PR_FILES: list[dict[str, Any]] = [
    {"filename": "src/lambda/handler.py", "status": "modified", "additions": 32, "deletions": 8, "changes": 40},
    {"filename": "src/lambda/db.py", "status": "modified", "additions": 12, "deletions": 4, "changes": 16},
    {"filename": "template.yaml", "status": "modified", "additions": 5, "deletions": 2, "changes": 7},
    {"filename": "tests/test_handler.py", "status": "added", "additions": 45, "deletions": 0, "changes": 45},
]

MOCK_PR_METADATA: dict[str, Any] = {
    "number": 42,
    "title": "feat: optimize Lambda handler and add DB connection pooling",
    "body": "Improves performance by caching DB connections and adding retry logic.",
    "head_sha": "abc1234def5678",
    "base_branch": "main",
    "state": "open",
    "author": "demo-user",
    "is_mock": True,
}


# ---------------------------------------------------------------------------
# GitHub Service
# ---------------------------------------------------------------------------


class GitHubService:
    """Service for GitHub REST API interactions."""

    def __init__(self) -> None:
        self._timeout = httpx.Timeout(settings.GITHUB_TIMEOUT_SECONDS)

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {"Accept": "application/vnd.github.v3+json"}
        if settings.GITHUB_TOKEN:
            # Never log the token value
            headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"
        return headers

    async def get_pr_files(self, repo_full_name: str, pr_number: int) -> list[dict[str, Any]]:
        """Return list of changed files for a pull request."""
        if settings.MOCK_GITHUB:
            logger.info("MOCK: returning mock PR files (is_mock=True)")
            return MOCK_PR_FILES

        return await self._fetch_pr_files(repo_full_name, pr_number)

    @_retry_policy
    async def _fetch_pr_files(self, repo_full_name: str, pr_number: int) -> list[dict[str, Any]]:
        url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}/files"
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(url, headers=self._headers())

        if response.status_code == 401:
            raise PermissionError("GitHub API: unauthorized — check GITHUB_TOKEN")
        if response.status_code == 403:
            raise PermissionError("GitHub API: forbidden — rate limited or insufficient permissions")
        if response.status_code == 404:
            raise FileNotFoundError(f"GitHub PR not found: {repo_full_name}#{pr_number}")
        if response.status_code == 429:
            raise RuntimeError("GitHub API: rate limited (429)")
        response.raise_for_status()

        return response.json()  # type: ignore[no-any-return]

    async def get_pr_metadata(self, repo_full_name: str, pr_number: int) -> dict[str, Any]:
        """Return PR metadata."""
        if settings.MOCK_GITHUB:
            return {**MOCK_PR_METADATA, "number": pr_number}

        return await self._fetch_pr_metadata(repo_full_name, pr_number)

    @_retry_policy
    async def _fetch_pr_metadata(self, repo_full_name: str, pr_number: int) -> dict[str, Any]:
        url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}"
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(url, headers=self._headers())

        response.raise_for_status()
        data = response.json()
        return {
            "number": data["number"],
            "title": data.get("title", ""),
            "body": data.get("body", ""),
            "head_sha": data["head"]["sha"],
            "base_branch": data["base"]["ref"],
            "state": data["state"],
            "author": data["user"]["login"],
            "is_mock": False,
        }


github_service = GitHubService()
