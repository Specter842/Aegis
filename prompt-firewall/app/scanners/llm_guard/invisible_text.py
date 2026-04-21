from typing import Optional
from app.scanners.base import BaseScanner, ScannerHealth
from app.schemas.common import ChannelText
from app.schemas.scan import Detection
from app.core.constants import ScanStage, SourceType
from app.core.config import settings
from app.core.logging import get_logger

log = get_logger(__name__)

class LLMGuardInvisibleText(BaseScanner):
    def __init__(self):
        self._is_ready = False
        self._diagnostic: Optional[str] = None
        self._scanner = None
        
        if not settings.ENABLE_LLM_GUARD:
            self._diagnostic = "Disabled via config"
            return
            
        try:
            from llm_guard.input_scanners import InvisibleText
            self._scanner = InvisibleText()
            self._is_ready = True
        except Exception as e:
            self._diagnostic = str(e)
            log.error("llm_guard_load_failed", error=str(e), scanner=self.name)

    @property
    def name(self) -> str:
        return "llm_guard_invisible_text"

    @property
    def stage(self) -> ScanStage:
        return ScanStage.PRE_PROCESS

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
        sanitized_text, is_valid, risk_score = await asyncio.to_thread(
            self._scanner.scan, channel.text
        )
        
        if not is_valid:
            return [Detection(
                scanner=self.name,
                channel_id=channel.channel_id,
                severity="medium",
                score=risk_score,
                attack_type="invisible_text",
                explanation="Invisible text characters detected",
                matched_text="<invisible_text>",
                sanitized_text=sanitized_text
            )]
        return []
