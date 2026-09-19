from fastapi import APIRouter, HTTPException

from app.schemas.analysis import AnalysisResponse, OutcomeCreate, OutcomeResponse
from app.services.analysis_service import get_analysis, record_outcome

router = APIRouter()

@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def read_analysis(analysis_id: str):
    analysis = await get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis

@router.get("/{analysis_id}/impact")
async def get_impact(analysis_id: str):
    analysis = await get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {
        "analysisId": analysis.analysisId,
        "affectedResources": analysis.affectedResources,
        "changedComponents": analysis.changedFiles,
        "dependencies": []
    }

@router.get("/{analysis_id}/forecast")
async def get_forecast(analysis_id: str):
    analysis = await get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {
        "analysisId": analysis.analysisId,
        **analysis.forecast,
        "evidence": analysis.evidence,
        "assumptions": analysis.assumptions
    }

@router.get("/{analysis_id}/evidence")
async def get_evidence(analysis_id: str):
    analysis = await get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {
        "analysisId": analysis.analysisId,
        "historicalEvidence": [],
        "awsEvidence": analysis.evidence,
        "telemetry": [],
        "dataCoverage": "partial"
    }

@router.get("/{analysis_id}/recommendations")
async def get_recommendations(analysis_id: str):
    analysis = await get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {
        "analysisId": analysis.analysisId,
        "recommendations": analysis.recommendations
    }

@router.post("/{analysis_id}/outcome", response_model=OutcomeResponse)
async def create_outcome(analysis_id: str, outcome: OutcomeCreate):
    return await record_outcome(analysis_id, outcome)
