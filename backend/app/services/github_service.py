import httpx
from fastapi import BackgroundTasks

from app.core.config import settings
from app.repositories.analysis_repository import analysis_repo
from app.repositories.project_repository import project_repo
from app.schemas.analysis import AnalysisCreate
from app.schemas.project import ProjectCreate
from app.services.analysis_service import start_analysis
from app.services.project_service import create_project


async def get_pr_files(repo_full_name: str, pr_number: int) -> dict:
    if settings.MOCK_GITHUB:
        return {
            "changed_files": ["src/lambda/handler.py", "template.yaml"],
            "additions": 45,
            "deletions": 12
        }
    
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        resp = await client.get(f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}/files", headers=headers)
        if resp.status_code != 200:
            return {"changed_files": [], "additions": 0, "deletions": 0}
            
        files = resp.json()
        changed_files = [f["filename"] for f in files]
        additions = sum(f.get("additions", 0) for f in files)
        deletions = sum(f.get("deletions", 0) for f in files)
        return {"changed_files": changed_files, "additions": additions, "deletions": deletions}

async def process_webhook(data: dict, background_tasks: BackgroundTasks):
    action = data.get("action")
    if action not in ["opened", "synchronize", "reopened"]:
        return
        
    pr = data.get("pull_request", {})
    repo = data.get("repository", {})
    
    repo_full_name = repo.get("full_name")
    pr_number = pr.get("number")
    commit_sha = pr.get("head", {}).get("sha")
    
    if not all([repo_full_name, pr_number, commit_sha]):
        return
        
    # Get or create project
    project = await project_repo.get_by_repo(repo_full_name)
    if not project:
        proj_in = ProjectCreate(
            repo=repo_full_name,
            environment="development",
            owner=repo.get("owner", {}).get("login", "unknown"),
            awsEnvironment="demo"
        )
        project = await create_project(proj_in)
        
    # Idempotency check: Don't re-run for same PR and commit SHA
    history = await analysis_repo.get_by_project(project.projectId)
    for entry in history:
        a_data = entry["analysis"]
        if a_data["prId"] == str(pr_number) and a_data["commitSha"] == commit_sha:
            return # Already processed this commit
            
    analysis_in = AnalysisCreate(
        prId=str(pr_number),
        commitSha=commit_sha
    )
    
    await start_analysis(project.projectId, analysis_in, background_tasks)
