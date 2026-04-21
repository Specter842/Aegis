from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from app.schemas.output import OutputScanResult

class TargetProvider(BaseModel):
    provider: str
    model: str

class ProxyChatRequest(BaseModel):
    request_id: str
    tenant_id: str
    app_id: str
    user_id: str = "anonymous"
    prompt: str
    history: List[Dict[str, str]] = Field(default_factory=list)
    target: TargetProvider
    proxy_mode: str = "enforce"

class ProxyChatResponse(BaseModel):
    request_id: str
    decision: str
    risk_score: float
    llm_called: bool = False
    model_response: Optional[Dict[str, Any]] = None
    output_scan: Optional[OutputScanResult] = None
    reason: Optional[str] = None

class ProviderErrorResponse(BaseModel):
    request_id: str
    error_type: str
    message: str
    llm_called: bool = True
