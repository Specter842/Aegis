from fastapi import APIRouter, Depends, HTTPException, Request, status
from typing import Annotated
from app.schemas.scan import ScanRequest, ScanResult
from app.api.deps import get_orchestrator, get_event_service
from app.services.scan_orchestrator import ScanOrchestrator
from app.services.event_service import EventService
from app.core.exceptions import PayloadValidationError
from app.core.logging import get_logger

log = get_logger(__name__)

router = APIRouter(prefix="/v1", tags=["Scan"])

@router.post("/scan", response_model=ScanResult, status_code=status.HTTP_200_OK)
async def scan_prompt(
    request: ScanRequest,
    orchestrator: Annotated[ScanOrchestrator, Depends(get_orchestrator)],
    event_service: Annotated[EventService, Depends(get_event_service)],
):
    try:
        result = await orchestrator.process_scan(request)
        
        # Phase 2: Emit WebSocket events after scan completes
        try:
            await event_service.emit_scan_events(request, result)
        except Exception as e:
            log.warning("event_emission_failed", error=str(e), request_id=request.request_id)
            # Event emission failure should not break the scan response
        
        return result
    except PayloadValidationError as e:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Scan processing failed")
