from typing import Optional
from app.scanners.base import BaseScanner, ScannerHealth
from app.schemas.common import ChannelText
from app.schemas.scan import Detection
from app.core.constants import ScanStage, SourceType
from app.core.config import settings
from app.core.logging import get_logger

log = get_logger(__name__)

class LLMGuardSecrets(BaseScanner):
    def __init__(self):
        self._is_ready = False
        self._diagnostic: Optional[str] = None
        self._scanner = None
        
        if not settings.ENABLE_LLM_GUARD:
            self._diagnostic = "Disabled via config"
            return
            
        try:
            from llm_guard.input_scanners import Secrets
            # Redact secrets instead of returning original text
            self._scanner = Secrets(redact_mode="all")
            self._is_ready = True
        except Exception as e:
            self._diagnostic = str(e)
            log.error("llm_guard_load_failed", error=str(e), scanner=self.name)

    @property
    def name(self) -> str:
        return "llm_guard_secrets"

    @property
    def stage(self) -> ScanStage:
        return ScanStage.ML

    @property
    def supported_source_types(self) -> set[str]:
        # both users and systems might leak secrets
        return {SourceType.USER, SourceType.SYSTEM, SourceType.TOOL, SourceType.DOC, SourceType.DOCUMENT_CHUNK, SourceType.URL_CONTENT}

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
                severity="high",
                score=risk_score,
                attack_type="secrets_leak",
                explanation="Secret or credential detected in input",
                matched_text="<redacted_secret>",
                sanitized_text=sanitized_text
            )]
        return []
