import hashlib
from typing import Tuple, List
from app.schemas.common import ChannelText
from app.schemas.scan import Detection
from app.schemas.output import OutputScanResult
from app.scanners.engine import ScanEngine
from app.core.constants import SourceType, OutputAction

class OutputScanService:
    def __init__(self, scan_engine: ScanEngine):
        self.scan_engine = scan_engine
        
    async def process_output(self, trace_id: str, raw_output: str, canary_token: str = None) -> Tuple[OutputScanResult, List[Detection], str, str]:
        channel = ChannelText(
            channel_id=f"out_{trace_id}",
            text=raw_output,
            source_type=SourceType.OUTPUT_CONTENT,
            trust_level=0
        )
        
        detections = await self.scan_engine.scan_channel(channel)
        
        canary_leaked = bool(canary_token and canary_token in raw_output)
        secret_detected = any(d.attack_type == "secrets" for d in detections)
        pii_detected = any(d.attack_type == "pii_leak" for d in detections)
        
        overall_risk = max([d.score for d in detections] + [0.0])
        
        if canary_leaked:
            overall_risk = 1.0
            
        action = OutputAction.ALLOW
        if canary_leaked or secret_detected:
            action = OutputAction.BLOCK
        elif pii_detected:
            action = OutputAction.REDACT
        elif overall_risk >= 0.8:
            action = OutputAction.BLOCK
        elif overall_risk >= 0.5:
            action = OutputAction.TRUNCATE
            
        # generate excerpt & hash
        output_hash = hashlib.sha256(raw_output.encode("utf-8")).hexdigest()
        
        safe_excerpt = raw_output[:100] + "..." if len(raw_output) > 100 else raw_output
        if action in (OutputAction.BLOCK, OutputAction.REDACT):
            safe_excerpt = "[REDACTED_OR_BLOCKED]"
            
        result = OutputScanResult(
            risk_score=overall_risk,
            blocked=(action == OutputAction.BLOCK),
            canary_leaked=canary_leaked,
            pii_detected=pii_detected,
            secret_detected=secret_detected,
            action=action.value
        )
        return result, detections, safe_excerpt, output_hash
