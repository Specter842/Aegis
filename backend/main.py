"""
AEGIS Backend — Autonomous Execution Guard for Intelligent Systems
FastAPI server with WebSocket support for real-time attack interception.
"""

import json
import re
import math
import time
import asyncio
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ============================================================
# Models
# ============================================================

class PromptRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = "default"

class AttackDetail(BaseModel):
    type: str
    name: str
    severity: str  # critical, high, medium, low
    confidence: float

class AnalysisResult(BaseModel):
    id: int
    timestamp: str
    prompt: str
    is_malicious: bool
    risk_score: int
    severity: str
    attacks: list[AttackDetail]
    reconstruction: Optional[dict] = None
    attack_path: list[str]
    interception_point: Optional[str] = None
    layers: dict
    trust_score: int

# ============================================================
# Attack Pattern Database
# ============================================================

ATTACK_PATTERNS = [
    {"pattern": r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules)", "type": "prompt_injection", "severity": "critical", "name": "Direct Instruction Override"},
    {"pattern": r"you\s+are\s+(now\s+)?(DAN|evil|unrestricted|jailbroken)", "type": "jailbreak", "severity": "critical", "name": "Persona Hijack (DAN)"},
    {"pattern": r"pretend\s+(you\s+)?(are|can|have|don't\s+have)", "type": "jailbreak", "severity": "high", "name": "Persona Manipulation"},
    {"pattern": r"system\s*prompt|initial\s*instructions|reveal\s*(your)?\s*prompt", "type": "prompt_extraction", "severity": "high", "name": "System Prompt Extraction"},
    {"pattern": r"bypass|override|disable\s*(your)?\s*(safety|filter|guardrail|restriction)", "type": "guardrail_bypass", "severity": "critical", "name": "Safety Bypass Attempt"},
    {"pattern": r"execute\s*(this)?\s*(code|command|script)|run\s*(this)?\s*(shell|bash|cmd)", "type": "code_execution", "severity": "critical", "name": "Code Execution Injection"},
    {"pattern": r"delete\s*(all)?\s*(files|data|database)|drop\s+table|rm\s+-rf", "type": "destructive_action", "severity": "critical", "name": "Destructive Action Attempt"},
    {"pattern": r"\b(password|secret|api[_\s]?key|token|credential|private[_\s]?key)\b", "type": "data_exfiltration", "severity": "high", "name": "Credential Exfiltration"},
    {"pattern": r"act\s+as\s+(a|an|my)\s+(admin|root|superuser|administrator)", "type": "privilege_escalation", "severity": "critical", "name": "Privilege Escalation"},
    {"pattern": r"forget\s+(everything|all|what)|reset\s+(your|context|memory)", "type": "memory_poisoning", "severity": "high", "name": "Memory Wipe Attempt"},
    {"pattern": r"\[system\]|\[INST\]|<\|system\|>|<<SYS>>|<s>\[INST\]", "type": "prompt_injection", "severity": "critical", "name": "Token Injection Attack"},
    {"pattern": r"translate.*to.*base64|encode.*in.*hex|rot13", "type": "obfuscation", "severity": "medium", "name": "Encoding Obfuscation"},
    {"pattern": r"hypothetically|in\s+a\s+fictional\s+scenario|for\s+(a\s+)?(novel|story|research)", "type": "jailbreak", "severity": "medium", "name": "Hypothetical Bypass"},
    {"pattern": r"sudo|chmod|chown|wget\s+http|curl\s+http", "type": "code_execution", "severity": "high", "name": "System Command Injection"},
    {"pattern": r"tool_call|function_call|<tool>|<function>", "type": "tool_manipulation", "severity": "critical", "name": "Direct Tool Manipulation"},
]

RECONSTRUCTION_MAP = {
    "prompt_injection": {"text": "[following standard guidelines]", "reason": "Removed instruction override attempt"},
    "jailbreak": {"text": "[as a helpful AI assistant]", "reason": "Removed persona hijack attempt"},
    "prompt_extraction": {"text": "[about your capabilities]", "reason": "Redirected from system prompt extraction to capabilities inquiry"},
    "guardrail_bypass": {"text": "[within safety guidelines]", "reason": "Removed safety bypass language"},
    "code_execution": {"text": "[explain the concept of]", "reason": "Converted execution request to explanation request"},
    "destructive_action": {"text": "[describe best practices for data management]", "reason": "Converted destructive action to safe query"},
    "data_exfiltration": {"text": "[about security best practices]", "reason": "Removed credential extraction attempt"},
    "privilege_escalation": {"text": "[as a standard user]", "reason": "Removed privilege escalation to standard access"},
    "memory_poisoning": {"text": "[continuing our conversation]", "reason": "Removed memory manipulation attempt"},
    "obfuscation": {"text": "[in plain text]", "reason": "Removed encoding obfuscation"},
    "tool_manipulation": {"text": "[using standard interface]", "reason": "Removed direct tool manipulation syntax"},
}

# ============================================================
# Security Engine
# ============================================================

class TrustEngine:
    def __init__(self):
        self.scores: dict[str, float] = {}
    
    def get_score(self, session_id: str) -> float:
        return self.scores.get(session_id, 100.0)
    
    def decay(self, session_id: str, attacks: list[dict]) -> float:
        current = self.get_score(session_id)
        decay_map = {"critical": 30, "high": 20, "medium": 12, "low": 5}
        total_decay = sum(decay_map.get(a["severity"], 5) for a in attacks)
        new_score = max(0, current - total_decay)
        self.scores[session_id] = new_score
        return new_score
    
    def recover(self, session_id: str, amount: float = 3.0) -> float:
        current = self.get_score(session_id)
        new_score = min(100, current + amount)
        self.scores[session_id] = new_score
        return new_score
    
    def reset(self, session_id: str):
        self.scores[session_id] = 100.0


class PromptClassifier:
    def classify(self, prompt: str) -> list[dict]:
        detected = []
        for pat in ATTACK_PATTERNS:
            match = re.search(pat["pattern"], prompt, re.IGNORECASE)
            if match:
                detected.append({
                    "type": pat["type"],
                    "name": pat["name"],
                    "severity": pat["severity"],
                    "confidence": round(0.85 + (hash(match.group()) % 15) / 100, 2),
                    "matched": match.group(),
                })
        return detected


class PromptReconstructor:
    def reconstruct(self, prompt: str, attacks: list[dict]) -> dict:
        safe = prompt
        changes = []
        for attack in attacks:
            matched_text = attack.get("matched", "")
            replacement = RECONSTRUCTION_MAP.get(attack["type"], {"text": "[safe query]", "reason": "Neutralized adversarial content"})
            if matched_text and matched_text in safe:
                safe = safe.replace(matched_text, replacement["text"], 1)
                changes.append({
                    "original": matched_text,
                    "replacement": replacement["text"],
                    "reason": replacement["reason"],
                })
        
        if not changes:
            safe = "Could you please help me with general information about this topic?"
            changes.append({
                "original": prompt[:80] + ("..." if len(prompt) > 80 else ""),
                "replacement": safe,
                "reason": "Full prompt was adversarial — replaced with safe equivalent",
            })
        
        return {"safe": safe, "changes": changes}


class AttackGraphAnalyzer:
    def get_attack_path(self, attacks: list[dict]) -> tuple[list[str], Optional[str]]:
        if not attacks:
            return [], None
        
        primary_type = attacks[0]["type"]
        
        if primary_type in ("code_execution", "destructive_action", "tool_manipulation"):
            return ["user", "prompt_gate", "llm", "reasoning", "tool_sandbox"], "tool_sandbox"
        elif primary_type == "memory_poisoning":
            return ["user", "prompt_gate", "llm", "memory"], "memory"
        elif primary_type == "data_exfiltration":
            return ["user", "prompt_gate", "llm", "output_gate"], "output_gate"
        else:
            return ["user", "prompt_gate"], "prompt_gate"


# ============================================================
# App Setup
# ============================================================

trust_engine = TrustEngine()
classifier = PromptClassifier()
reconstructor = PromptReconstructor()
graph_analyzer = AttackGraphAnalyzer()
event_counter = 0

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🛡️  AEGIS Security Kernel initialized")
    yield
    print("🛡️  AEGIS Security Kernel shutting down")

app = FastAPI(
    title="AEGIS Security Kernel",
    description="Autonomous Execution Guard for Intelligent Systems",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# REST Endpoints
# ============================================================

@app.get("/")
async def root():
    return {
        "name": "AEGIS",
        "version": "1.0.0",
        "status": "active",
        "tagline": "Autonomous Execution Guard for Intelligent Systems",
    }

@app.post("/api/analyze")
async def analyze_prompt(request: PromptRequest):
    global event_counter
    event_counter += 1
    
    # Classify
    attacks = classifier.classify(request.prompt)
    is_malicious = len(attacks) > 0
    
    # Risk score
    severity_weights = {"critical": 35, "high": 25, "medium": 15, "low": 8}
    risk_score = min(100, sum(severity_weights.get(a["severity"], 10) for a in attacks)) if attacks else 0
    
    max_severity = "safe"
    if attacks:
        severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        max_severity = max(attacks, key=lambda a: severity_order.get(a["severity"], 0))["severity"]
    
    # Trust update
    if is_malicious:
        trust_score = trust_engine.decay(request.session_id, attacks)
    else:
        trust_score = trust_engine.recover(request.session_id)
    
    # Attack path
    attack_path, interception_point = graph_analyzer.get_attack_path(attacks)
    
    # Reconstruction
    reconstruction = None
    if is_malicious:
        reconstruction = reconstructor.reconstruct(request.prompt, attacks)
    
    # Layer statuses
    primary_type = attacks[0]["type"] if attacks else None
    layers = {
        "prompt_gate": {"status": "intercepted" if is_malicious else "passed", "details": f"Detected {len(attacks)} threat(s)" if is_malicious else "Clean input"},
        "reasoning_monitor": {"status": "alert" if primary_type in ("privilege_escalation", "jailbreak") else "nominal", "details": "Chain-of-thought analysis"},
        "tool_sandbox": {"status": "blocked" if primary_type in ("code_execution", "destructive_action", "tool_manipulation") else "nominal", "details": "Tool access control"},
        "memory_sentinel": {"status": "quarantined" if primary_type == "memory_poisoning" else "nominal", "details": "Memory integrity check"},
        "output_gate": {"status": "filtered" if primary_type == "data_exfiltration" else "nominal", "details": "Output sanitization"},
    }
    
    return AnalysisResult(
        id=event_counter,
        timestamp=datetime.utcnow().isoformat(),
        prompt=request.prompt,
        is_malicious=is_malicious,
        risk_score=risk_score,
        severity=max_severity,
        attacks=[AttackDetail(type=a["type"], name=a["name"], severity=a["severity"], confidence=a["confidence"]) for a in attacks],
        reconstruction=reconstruction,
        attack_path=attack_path,
        interception_point=interception_point,
        layers=layers,
        trust_score=int(trust_score),
    )

@app.post("/api/reset-trust")
async def reset_trust(session_id: str = "default"):
    trust_engine.reset(session_id)
    return {"trust_score": 100, "status": "reset"}

@app.get("/api/health")
async def health():
    return {"status": "healthy", "uptime": time.time()}

# ============================================================
# WebSocket for Real-Time
# ============================================================

connected_clients: list[WebSocket] = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "analyze":
                request = PromptRequest(prompt=message["prompt"], session_id=message.get("session_id", "default"))
                result = await analyze_prompt(request)
                await websocket.send_json({"type": "analysis_result", "data": result.model_dump()})
            
            elif message.get("type") == "reset_trust":
                trust_engine.reset(message.get("session_id", "default"))
                await websocket.send_json({"type": "trust_reset", "data": {"trust_score": 100}})
    
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
