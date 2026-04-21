from collections import defaultdict
import uuid
from app.schemas.scan import ScanRequest, ScanResult
from app.services.normalizer import NormalizerService
from app.services.policy_engine import PolicyEngine
from app.services.persistence_service import PersistenceService
from app.scanners.engine import ScanEngine
from app.core.constants import Decision
from app.core.security import enforce_payload_limits, get_payload_size
from app.core.logging import get_logger

log = get_logger(__name__)

class ScanOrchestrator:
    def __init__(self, 
                 normalizer: NormalizerService,
                 scan_engine: ScanEngine,
                 policy_engine: PolicyEngine,
                 persistence: PersistenceService):
        self.normalizer = normalizer
        self.scan_engine = scan_engine
        self.policy_engine = policy_engine
        self.persistence = persistence
        
    async def process_scan(self, request: ScanRequest) -> ScanResult:
        # 1. Enforce payload limits
        enforce_payload_limits(
            payload_bytes=get_payload_size(request),
            prompt_length=len(request.prompt),
            history_items=len(request.history),
            max_message_length=max([len(m.content) for m in request.history] + [0])
        )
        
        trace_id = f"trace_{uuid.uuid4().hex[:8]}"
        log.info("scan_started", request=request.request_id, trace_id=trace_id)
        
        # 2. Normalize
        channels = self.normalizer.normalize_request(request)
        
        # 3. Execute Scanners
        all_detections = []
        for channel in channels:
            # Skip trusted channels unless specifically requested 
            if channel.is_trusted: 
                continue
                
            channel_detections = await self.scan_engine.scan_channel(channel)
            all_detections.extend(channel_detections)
            
        # 4. Compute scores & Policy
        channel_scores = defaultdict(float)
        channel_sanitizations = {}
        
        for d in all_detections:
            channel_scores[d.channel_id] = max(channel_scores[d.channel_id], d.score)
            if d.sanitized_text:
                channel_sanitizations[d.channel_id] = d.sanitized_text
                
        policy = self.policy_engine.evaluate(all_detections, channel_scores)
        
        # 5. Build Result
        result = ScanResult(
            request_id=request.request_id,
            trace_id=trace_id,
            decision=policy.decision.value,
            risk_score=policy.risk_score,
            channel_scores=dict(channel_scores),
            detections=all_detections,
            recommended_action=policy.recommended_action,
            sanitized_channels=channel_sanitizations if policy.decision == Decision.SANITIZE else {}
        )
        
        # 6. Persist Async
        await self.persistence.save_scan_result(request, channels, result)
        
        return result
