from typing import Optional, Any
from pydantic import BaseModel, Field
from app.schemas.common import HistoryMessage, TargetModel

# --------------------------
# Request
# --------------------------
class ScanRequest(BaseModel):
    request_id: str
    tenant_id: str
    app_id: str
    user_id: str
    prompt: str = Field(..., description="The main text input to scan")
    history: list[HistoryMessage] = Field(default_factory=list)
    target: Optional[TargetModel] = None
    mode: str = "classify"

# --------------------------
# Response inner models
# --------------------------
class Detection(BaseModel):
    scanner: str
    channel_id: str
    severity: str
    score: float
    attack_type: str
    explanation: str
    matched_text: str
    sanitized_text: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

# --------------------------
# Response
# --------------------------
class ScanResult(BaseModel):
    request_id: str
    trace_id: str
    decision: str
    risk_score: float
    channel_scores: dict[str, float]
    detections: list[Detection]
    recommended_action: str
    sanitized_channels: dict[str, str] = Field(default_factory=dict)
