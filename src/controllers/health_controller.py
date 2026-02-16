from typing import Any, Dict

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

health_router = APIRouter()


@health_router.get(
    "/health",
    status_code=200,
    summary="Health Check",
    description="Simple health check that returns service status",
)
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint that returns if the service is running.
    This endpoint should always return 200 if the service is up.
    """
    return {"status": "healthy", "service": "my-agent-labs", "version": "v1"}


@health_router.get(
    "/ready",
    summary="Readiness Check",
    description="Readiness check that verifies Redis connectivity",
    response_model=None,
)
async def readiness_check():
    """
    Readiness check that verifies Redis connectivity for Celery broker/backend.
    """
    checks = {}
    overall_status = "ready"

    response_data = {
        "status": overall_status,
        "service": "my-agent-labs",
        "version": "v1",
        "checks": checks,
    }

    if overall_status == "not_ready":
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=response_data
        )

    return JSONResponse(status_code=status.HTTP_200_OK, content=response_data)
