from dataclasses import dataclass
from typing import Tuple
from app.schemas.scan import Detection
from app.core.constants import Decision
from app.core.logging import get_logger

log = get_logger(__name__)

@dataclass
class PolicyResult:
    decision: Decision
    risk_score: float
    recommended_action: str

class PolicyEngine:
    def __init__(self):
        # Strict precedence: BLOCK > CHALLENGE > SANITIZE > ALLOW
        pass
        
    def evaluate(self, detections: list[Detection], channel_scores: dict[str, float]) -> PolicyResult:
        if not detections:
            return PolicyResult(
                decision=Decision.ALLOW,
                risk_score=0.0,
                recommended_action="pass"
            )
            
        # Overall risk is the max score across any detection
        overall_risk = max([d.score for d in detections] + [0.0])
        
        # Severity counts
        severities = {
            "critical": len([d for d in detections if d.severity == "critical"]),
            "high": len([d for d in detections if d.severity == "high"]),
            "medium": len([d for d in detections if d.severity == "medium"]),
            "low": len([d for d in detections if d.severity == "low"])
        }
        
        has_sanitization = any(d.sanitized_text is not None for d in detections)
        
        if severities["critical"] > 0:
            return PolicyResult(
                decision=Decision.BLOCK,
                risk_score=overall_risk,
                recommended_action="terminate_request"
            )
            
        if severities["high"] > 0:
            return PolicyResult(
                decision=Decision.CHALLENGE,
                risk_score=overall_risk,
                recommended_action="require_user_confirmation"
            )
            
        if severities["medium"] > 0 and has_sanitization:
            return PolicyResult(
                decision=Decision.SANITIZE,
                risk_score=overall_risk,
                recommended_action="use_sanitized"
            )
            
        # Default fallback for medium/low without sanitization
        return PolicyResult(
            decision=Decision.ALLOW,
            risk_score=overall_risk,
            recommended_action="log_only"
        )
