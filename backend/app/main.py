"""InfraShift FastAPI application entry point."""
from __future__ import annotations

import uuid
from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.api import analyses, demo_api, github, health, projects
from app.api.analyses import start_analysis_for_project
from app.core.config import settings
from app.core.errors import (
    InfraShiftError,
    error_response,
    generic_exception_handler,
    infrashift_exception_handler,
)
from app.core.logging import configure_logging
from app.schemas.analysis import AnalysisCreate, AnalysisCreatedResponse

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

configure_logging(settings.LOG_LEVEL)

import logging  # noqa: E402

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ANN201
    logger.info(
        "InfraShift backend starting | env=%s local_mode=%s live_aws=%s mock_ai=%s mock_github=%s",
        settings.ENVIRONMENT,
        settings.LOCAL_MODE,
        settings.LIVE_AWS,
        settings.MOCK_AI,
        settings.MOCK_GITHUB,
    )
    yield
    logger.info("InfraShift backend shutting down")


# ---------------------------------------------------------------------------
# Exception handlers (defined before app)
# ---------------------------------------------------------------------------


async def pydantic_validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "-")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response(
            "VALIDATION_ERROR",
            "Request validation failed",
            request_id,
            extra={"details": exc.errors()},
        ),
    )


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="InfraShift Backend",
    description=(
        "InfraShift predicts infrastructure impact of code changes before deployment.\n\n"
        "**Local mode**: Set `LOCAL_MODE=true`, `MOCK_AI=true`, `MOCK_GITHUB=true` — "
        "no AWS/GitHub credentials needed.\n\n"
        "**Live mode**: Set `LIVE_AWS=true`, `MOCK_AI=false`, `MOCK_GITHUB=false` with real credentials."
    ),
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Request ID middleware
# ---------------------------------------------------------------------------


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):  # noqa: ANN001, ANN201
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------

app.add_exception_handler(InfraShiftError, infrashift_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(ValidationError, pydantic_validation_handler)  # type: ignore[arg-type]
app.add_exception_handler(Exception, generic_exception_handler)  # type: ignore[arg-type]

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(analyses.router, prefix="/api/v1/analyses", tags=["Analyses"])
app.include_router(github.router, prefix="/api/v1/github", tags=["GitHub"])
app.include_router(demo_api.router, prefix="/api", tags=["Demo Workload API"])
app.include_router(demo_api.router, prefix="/api/v1", tags=["Demo Workload API"])


# ---------------------------------------------------------------------------
# Analysis creation (nested under projects for REST structure)
# ---------------------------------------------------------------------------


@app.post(
    "/api/v1/projects/{project_id}/analyses",
    response_model=AnalysisCreatedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Analyses"],
    summary="Create and queue analysis for a project",
)
async def create_project_analysis(
    project_id: str,
    analysis_in: AnalysisCreate,
    background_tasks: BackgroundTasks,
) -> AnalysisCreatedResponse:
    return await start_analysis_for_project(project_id, analysis_in, background_tasks)


# ---------------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------------


@app.get("/", include_in_schema=False)
async def root() -> dict:
    return {"service": "infrashift-backend", "docs": "/docs"}
