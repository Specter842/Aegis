import re
from app.scanners.base import BaseScanner, ScannerHealth
from app.schemas.common import ChannelText
from app.schemas.scan import Detection
from app.core.constants import ScanStage, SourceType

class UnicodeScanner(BaseScanner):
    def __init__(self):
        # Detect zero-width characters (ZWJ, ZWNJ, LRM, RLM, etc.)
        self.zero_width_re = re.compile(r'[\u200B-\u200D\uFEFF]')
        # Detect BIDI override characters
        self.bidi_re = re.compile(r'[\u202A-\u202E\u2066-\u2069]')

    @property
    def name(self) -> str:
        return "static_unicode"

    @property
    def stage(self) -> ScanStage:
        return ScanStage.PRE_PROCESS

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
        
        zw_matches = self.zero_width_re.findall(channel.text)
        if zw_matches:
            sanitized = self.zero_width_re.sub('', channel.text)
            detections.append(Detection(
                scanner=self.name,
                channel_id=channel.channel_id,
                severity="medium",
                score=0.6,
                attack_type="unicode_obfuscation",
                explanation="Zero-width characters detected (often used to evade token filters)",
                matched_text="<invisible_chars>",
                sanitized_text=sanitized
            ))
            channel.text = sanitized # update for next scanners if desired, though normally we'd rely on normalizer
            
        bidi_matches = self.bidi_re.findall(channel.text)
        if bidi_matches:
            sanitized = self.bidi_re.sub('', channel.text)
            detections.append(Detection(
                scanner=self.name,
                channel_id=channel.channel_id,
                severity="high",
                score=0.8,
                attack_type="bidi_override",
                explanation="BIDI override characters detected (often used to spoof execution order)",
                matched_text="<bidi_chars>",
                sanitized_text=sanitized
            ))
            
        return detections
