import asyncio
import logging
from datetime import UTC, datetime

from app.repositories.analysis_repository import analysis_repo
from app.services.ai_service import analyze_impact
from app.services.cloudwatch_service import cloudwatch_service

logger = logging.getLogger(__name__)

async def run_analysis(analysis_id: str):
    from app.services.github_service import get_pr_files
    
    analysis = await analysis_repo.get(analysis_id)
    if not analysis or analysis.status != "PENDING":
        return
        
    analysis.status = "RUNNING"
    analysis.updatedAt = datetime.now(UTC)
    await analysis_repo.save(analysis)
    
    try:
        # 1. Fetch GitHub PR Files with Timeout
        pr_data = await asyncio.wait_for(get_pr_files(analysis.repo, int(analysis.prId)), timeout=10.0)
        analysis.changedFiles = pr_data.get("changed_files", [])
        
        # 2. Map Affected Resources
        function_name = f"{analysis.repo.split('/')[-1]}-main-func"
        analysis.affectedResources = [f"arn:aws:lambda:region:account:function:{function_name}"]
        
        # 3. Collect AWS Evidence (synchronous call wrapped in executor)
        loop = asyncio.get_running_loop()
        cw_evidence = await loop.run_in_executor(
            None, 
            cloudwatch_service.get_metrics, 
            'AWS/Lambda', 'Invocations', [{'Name': 'FunctionName', 'Value': function_name}], 7
        )
        
        # 4. AI Service
        ai_payload = {
            "changed_files": analysis.changedFiles,
            "additions": pr_data.get("additions", 0),
            "deletions": pr_data.get("deletions", 0),
            "aws_evidence": cw_evidence
        }
        
        ai_response = await asyncio.wait_for(analyze_impact(ai_payload), timeout=30.0)
        
        analysis.forecast = ai_response.get("forecast")
        analysis.confidence = ai_response.get("confidence")
        
        evidence = ai_response.get("evidence", [])
        evidence.append({"source": "cloudwatch", "metrics": cw_evidence})
        analysis.evidence = evidence
        
        analysis.assumptions = ai_response.get("assumptions")
        analysis.recommendations = ai_response.get("recommendations")
        
        analysis.status = "COMPLETED"
        
    except TimeoutError:
        analysis.status = "FAILED"
        analysis.error = "External service timeout (GitHub or AI)"
        logger.error(f"Analysis {analysis_id} timed out.")
    except Exception as e:
        analysis.status = "FAILED"
        analysis.error = str(e)
        logger.exception(f"Analysis {analysis_id} failed.")
        
    analysis.completedAt = datetime.now(UTC)
    analysis.updatedAt = datetime.now(UTC)
    await analysis_repo.save(analysis)
