from pydantic import BaseModel
from typing import Optional

class OutputScanResult(BaseModel):
    risk_score: float = 0.0
    blocked: bool = False
    canary_leaked: bool = False
    pii_detected: bool = False
    secret_detected: bool = False
    action: str = "allow"
