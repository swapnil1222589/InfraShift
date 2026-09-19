from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import analyses, github, health, projects
from app.core.config import settings

app = FastAPI(
    title="InfraShift Backend",
    description="Backend API for InfraShift MVP",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(analyses.router, prefix="/api/v1/analyses", tags=["Analyses"])
app.include_router(github.router, prefix="/api/v1/github", tags=["GitHub"])
