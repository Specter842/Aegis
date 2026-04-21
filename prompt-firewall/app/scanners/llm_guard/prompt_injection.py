from typing import Optional
from app.scanners.base import BaseScanner, ScannerHealth
from app.schemas.common import ChannelText
from app.schemas.scan import Detection
from app.core.constants import ScanStage, SourceType
from app.core.config import settings
from app.core.logging import get_logger

log = get_logger(__name__)

class LLMGuardPromptInjection(BaseScanner):
    def __init__(self):
        self._is_ready = False
        self._diagnostic: Optional[str] = None
        self._scanner = None
        
        if not settings.ENABLE_LLM_GUARD:
            self._diagnostic = "Disabled via config (ENABLE_LLM_GUARD=False)"
            return
            
        try:
            from llm_guard.input_scanners import PromptInjection
            # Use deterministic thresholds and models where possible.
            self._scanner = PromptInjection(threshold=0.5)
            self._is_ready = True
            log.info("llm_guard_prompt_injection_ready")
        except Exception as e:
            self._diagnostic = f"Failed to initialize: {e}"
            log.error("llm_guard_load_failed", error=str(e), scanner=self.name)

    @property
    def name(self) -> str:
        return "llm_guard_prompt_injection"

    @property
    def stage(self) -> ScanStage:
        return ScanStage.ML

    @property
    def supported_source_types(self) -> set[str]:
        return {SourceType.USER, SourceType.DOCUMENT_CHUNK, SourceType.URL_CONTENT}

    @property
    def is_critical(self) -> bool:
        return settings.LLM_GUARD_READINESS_MODE == "strict"

    def readiness(self) -> ScannerHealth:
        return ScannerHealth(
            name=self.name,
            is_ready=self._is_ready,
            diagnostic=self._diagnostic
        )

    async def scan(self, channel: ChannelText) -> list[Detection]:
        if not self._is_ready or not self._scanner:
            return []
            
        import asyncio
        # llm-guard can be CPU intensive, wrap in to_thread
        sanitized_text, is_valid, risk_score = await asyncio.to_thread(
            self._scanner.scan, channel.text
        )
        
        if not is_valid:
            severity = "critical" if risk_score > 0.8 else "high"
            return [Detection(
                scanner=self.name,
                channel_id=channel.channel_id,
                severity=severity,
                score=risk_score,
                attack_type="prompt_injection_ml",
                explanation="ML-based prompt injection detection triggered",
                matched_text=channel.text[:100], # Cannot isolate exact match easily from this scanner
                sanitized_text=sanitized_text if sanitized_text != channel.text else None
            )]
        return []
