import re
from app.scanners.base import BaseScanner, ScannerHealth
from app.schemas.common import ChannelText
from app.schemas.scan import Detection
from app.core.constants import ScanStage, SourceType

class EncodedTextScanner(BaseScanner):
    def __init__(self):
        # Look for base64 looking strings (min length 16)
        self.b64_re = re.compile(r'(?:[A-Za-z0-9+/]{4}){4,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?')
        # Look for hex encoded strings (min length 16)
        self.hex_re = re.compile(r'\\x[0-9a-fA-F]{2}(?:\\x[0-9a-fA-F]{2}){7,}')

    @property
    def name(self) -> str:
        return "static_encoded_text"

    @property
    def stage(self) -> ScanStage:
        return ScanStage.STATIC

    @property
    def supported_source_types(self) -> set[str]:
        return {SourceType.USER, SourceType.DOCUMENT_CHUNK, SourceType.URL_CONTENT}

    @property
    def is_critical(self) -> bool:
        return True

    def readiness(self) -> ScannerHealth:
        return ScannerHealth(name=self.name, is_ready=True)

    async def scan(self, channel: ChannelText) -> list[Detection]:
        detections = []
        
        for match in self.b64_re.finditer(channel.text):
            detections.append(Detection(
                scanner=self.name,
                channel_id=channel.channel_id,
                severity="medium",
                score=0.5,
                attack_type="encoding_obfuscation",
                explanation="Suspicious base64-like string detected",
                matched_text=match.group(0)[:64] + ("..." if len(match.group(0)) > 64 else "")
            ))
            
        for match in self.hex_re.finditer(channel.text):
            detections.append(Detection(
                scanner=self.name,
                channel_id=channel.channel_id,
                severity="high",
                score=0.7,
                attack_type="encoding_obfuscation",
                explanation="Suspicious hex-encoded byte-sequence detected",
                matched_text=match.group(0)[:64] + ("..." if len(match.group(0)) > 64 else "")
            ))
            
        return detections
