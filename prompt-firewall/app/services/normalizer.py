import unicodedata
from app.schemas.common import ChannelText, HistoryMessage
from app.schemas.scan import ScanRequest
from app.core.constants import SourceType, TrustLevel

class NormalizerService:
    def __init__(self):
        pass
        
    def normalize_request(self, request: ScanRequest) -> list[ChannelText]:
        """
        Convert a raw request into clean, isolated channels.
        Trust Model:
            Prompt -> UNTRUSTED
            History (User) -> UNTRUSTED
            History (Assistant/System) -> TRUSTED
        """
        channels = []
        
        # 1. Normalize primary prompt
        clean_prompt = self._clean_text(request.prompt)
        prompt_channel = ChannelText(
            channel_id="prompt",
            source_type=SourceType.USER,
            text=clean_prompt,
            trust_level=TrustLevel.UNTRUSTED
        )
        channels.append(prompt_channel)
        
        # 2. Normalize history
        for i, msg in enumerate(request.history):
            clean_msg = self._clean_text(msg.content)
            
            source_type = SourceType.USER if msg.role == "user" else SourceType.SYSTEM
            if msg.role == "tool":
                source_type = SourceType.TOOL
                
            trust_level = TrustLevel.UNTRUSTED if msg.role == "user" else TrustLevel.TRUSTED
            
            chan = ChannelText(
                channel_id=f"history_{i}",
                source_type=source_type,
                text=clean_msg,
                trust_level=trust_level
            )
            channels.append(chan)
            
        return channels
        
    def _clean_text(self, text: str) -> str:
        # Strip null bytes
        text = text.replace('\x00', '')
        # Normalize whitespace (but preserve structure)
        # Apply strict NFC normalization
        text = unicodedata.normalize('NFC', text)
        return text
