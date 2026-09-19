"""Structured error responses for InfraShift API."""
from __future__ import annotations

import logging
from typing import Any

from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

logger = logging.getLogger(__name__)


class InfraShiftError(Exception):
    """Base application exception."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "INTERNAL_ERROR"

    def __init__(self, message: str, *, error_code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        if error_code:
            self.error_code = error_code


class NotFoundError(InfraShiftError):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "NOT_FOUND"


class ConflictError(InfraShiftError):
    status_code = status.HTTP_409_CONFLICT
    error_code = "CONFLICT"


class ValidationError_(InfraShiftError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "VALIDATION_ERROR"


class ServiceUnavailableError(InfraShiftError):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    error_code = "SERVICE_UNAVAILABLE"


class InvalidStateTransitionError(InfraShiftError):
    status_code = status.HTTP_409_CONFLICT
    error_code = "INVALID_STATE_TRANSITION"


class UnauthorizedError(InfraShiftError):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "UNAUTHORIZED"


class ForbiddenError(InfraShiftError):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "FORBIDDEN"


def error_response(
    error_code: str,
    message: str,
    request_id: str = "-",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build structured error response dict."""
    payload: dict[str, Any] = {
        "error": {
            "code": error_code,
            "message": message,
            "request_id": request_id,
        }
    }
    if extra:
        payload["error"].update(extra)
    return payload


def _get_request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "-")


async def infrashift_exception_handler(request: Request, exc: InfraShiftError) -> JSONResponse:
    request_id = _get_request_id(request)
    logger.warning("Application error [%s]: %s", exc.error_code, exc.message)
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(exc.error_code, exc.message, request_id),
    )


async def pydantic_validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
    request_id = _get_request_id(request)
    logger.warning("Validation error: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response(
            "VALIDATION_ERROR",
            "Request validation failed",
            request_id,
            extra={"details": exc.errors()},
        ),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = _get_request_id(request)
    logger.exception("Unhandled exception [request_id=%s]", request_id)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(
            "INTERNAL_ERROR",
            "An unexpected error occurred",
            request_id,
        ),
    )
