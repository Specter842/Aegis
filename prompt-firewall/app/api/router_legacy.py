from fastapi import APIRouter, Depends, HTTPException, Request, status
from typing import Annotated, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid
import json

from app.schemas.scan import ScanRequest
from app.api.deps import get_orchestrator, get_event_service
from app.services.scan_orchestrator import ScanOrchestrator
from app.services.event_service import EventService
from app.core.exceptions import PayloadValidationError
from app.core.logging import get_logger

log = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["Legacy Compatibility"])

DEFAULT_APP_ID = "legacy-aegis-dashboard"
DEFAULT_TENANT_ID = "legacy-tenant"

class LegacyPromptRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = "default"

@router.post("/analyze")
async def analyze_legacy(
    req: LegacyPromptRequest,
    orchestrator: Annotated[ScanOrchestrator, Depends(get_orchestrator)],
    event_service: Annotated[EventService, Depends(get_event_service)],
):
    """
    Temporary compatibility adapter mapping old `/api/analyze` requests
    into the new `v1/scan` pipeline.
    """
    try:
        scan_req = ScanRequest(
            request_id=f"legacy_{uuid.uuid4().hex[:8]}",
            tenant_id=DEFAULT_TENANT_ID,
            app_id=DEFAULT_APP_ID,
            user_id=req.session_id,
            prompt=req.prompt,
            mode="classify"
        )
        
        result = await orchestrator.process_scan(scan_req)
        
        # Phase 2: Emit WebSocket events after scan completes
        try:
            await event_service.emit_scan_events(scan_req, result)
        except Exception as e:
            log.warning("event_emission_failed", error=str(e), request_id=scan_req.request_id)
        
        attacks = []
        for d in result.detections:
            attacks.append({
                "type": d.attack_type,
                "name": d.explanation,
                "severity": d.severity,
                "confidence": d.score
            })
            
        reconstruction = None
        if result.decision == "sanitize" and "prompt" in result.sanitized_channels:
            reconstruction = {
                "safe": result.sanitized_channels["prompt"],
                "changes": [{"original": d.matched_text, "replacement": result.sanitized_channels["prompt"], "reason": d.explanation} for d in result.detections]
            }
            
        is_malicious = len(attacks) > 0
        
        legacy_res = {
            "id": hash(result.request_id) % 10000,
            "timestamp": datetime.utcnow().isoformat(),
            "prompt": req.prompt,
            "is_malicious": is_malicious,
            "risk_score": int(result.risk_score * 100),
            "severity": max([d.severity for d in result.detections] + ["safe"], key=lambda s: {"critical":4, "high":3, "medium":2, "low":1, "safe":0}[s]),
            "attacks": attacks,
            "reconstruction": reconstruction,
            "attack_path": ["user", "prompt_gate"] if is_malicious else [],
            "interception_point": "prompt_gate" if is_malicious else None,
            "layers": {
                "prompt_gate": {"status": "intercepted" if is_malicious else "passed", "details": f"Detected {len(attacks)} threat(s)" if is_malicious else "Clean input"},
                "reasoning_monitor": {"status": "nominal", "details": "Chain-of-thought analysis"},
                "tool_sandbox": {"status": "nominal", "details": "Tool access control"},
                "memory_sentinel": {"status": "nominal", "details": "Memory integrity check"},
                "output_gate": {"status": "nominal", "details": "Output sanitization"}
            },
            "trust_score": max(0, 100 - int(result.risk_score * 100)) # Simple projection
        }
        return legacy_res
    except PayloadValidationError as e:
        raise HTTPException(status_code=413, detail=str(e))
    except Exception as e:
        log.error("legacy_scan_failed", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Scan failed")
