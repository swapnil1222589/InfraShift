import sys
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from ai_engine.schemas.contracts import ForecastRequest, ForecastResponse
from ai_engine.agents.forecasting_agent import analyze_and_forecast

# Add the parent directory to sys.path so it can be run directly without -m
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

app = FastAPI(title="InfraShift AI Engine")

@app.get("/")
def read_root():
    return {"message": "Welcome to the InfraShift AI Engine. The API is running! Check /docs for the Swagger UI."}

# Dictionary to hold mock async job states for the hackathon MVP
_ANALYSIS_JOBS = {}

@app.post("/analyses/{analysis_id}/forecast")
def start_forecast(analysis_id: str, request: ForecastRequest):
    # In a real async system, this would queue a job and return 'in_progress'.
    # For MVP, we process immediately but store the result to mimic the async GET flow.
    try:
        response = analyze_and_forecast(request)
        _ANALYSIS_JOBS[analysis_id] = response
        return {"analysis_id": analysis_id, "status": "in_progress"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyses/{analysis_id}/forecast", response_model=ForecastResponse)
def get_forecast(analysis_id: str):
    if analysis_id not in _ANALYSIS_JOBS:
        raise HTTPException(status_code=404, detail="analysis_id not found")
    return _ANALYSIS_JOBS[analysis_id]

if __name__ == "__main__":
    uvicorn.run("ai_engine.main:app", host="0.0.0.0", port=8000, reload=True)
