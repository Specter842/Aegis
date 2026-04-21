from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from typing import Annotated
from app.api.deps import get_readiness_service
from app.services.readiness_service import ReadinessService
from app.core.config import settings

router = APIRouter()

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Simple liveness probe. If the app is responding, it's alive."""
    return {"status": "alive", "version": "0.1.0"}

@router.get("/ready")
async def readiness_check(
    readiness: Annotated[ReadinessService, Depends(get_readiness_service)]
):
    """Deep check of DB and scanners."""
    is_ready, details = await readiness.evaluate_readiness()
    
    status_code = status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return JSONResponse(status_code=status_code, content=details)
