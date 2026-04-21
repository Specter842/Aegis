try:
    import yara
    YARA_AVAILABLE = True
except ImportError:
    YARA_AVAILABLE = False

from pathlib import Path
from app.scanners.base import BaseScanner, ScannerHealth
from app.schemas.common import ChannelText
from app.schemas.scan import Detection
from app.core.constants import ScanStage, SourceType
from app.core.logging import get_logger

log = get_logger(__name__)

class YaraScanner(BaseScanner):
    def __init__(self, rules_path: str = "rules/injections.yar"):
        self._rules = None
        self._is_ready = False
        self._diagnostic = None
        self._warnings = []

        if not YARA_AVAILABLE:
            self._diagnostic = "yara-python not installed"
            return
            
        path = Path(rules_path)
        if not path.exists():
            self._diagnostic = f"YARA rules file not found: {rules_path}"
            return
            
        try:
            # We capture syntax warnings if compile provides them, though yara python
            # typically raises SyntaxError for bad rules.
            self._rules = yara.compile(filepath=str(path))
            self._is_ready = True
            log.info("yara_compiled", rules_path=rules_path)
        except Exception as e:
            self._diagnostic = f"YARA compilation failed: {str(e)}"
            log.error("yara_compile_error", error=str(e))

    @property
    def name(self) -> str:
        return "static_yara"

    @property
    def stage(self) -> ScanStage:
        return ScanStage.STATIC

    @property
    def supported_source_types(self) -> set[str]:
        return {SourceType.USER, SourceType.DOCUMENT_CHUNK, SourceType.URL_CONTENT}

    @property
    def is_critical(self) -> bool:
        # Depending on environments, YARA can fail to load. We want to be nice and let
        # local dev continue even if YARA fails.
        return True

    def readiness(self) -> ScannerHealth:
        return ScannerHealth(
            name=self.name,
            is_ready=self._is_ready,
            diagnostic=self._diagnostic
        )

    async def scan(self, channel: ChannelText) -> list[Detection]:
        detections = []
        if not self._is_ready or not self._rules:
            return detections
            
        try:
            matches = self._rules.match(data=channel.text.encode('utf-8'))
            for match in matches:
                
                # Rule tags mapping severity
                severity = "medium"
                score = 0.5
                if "critical" in match.tags:
                    severity = "critical"
                    score = 1.0
                elif "high" in match.tags:
                    severity = "high"
                    score = 0.8
                    
                matched_text = ""
                if match.strings:
                    # just grab the first matching string instance
                    matched_text_bytes = match.strings[0][2]
                    try:
                        matched_text = matched_text_bytes.decode('utf-8')
                    except UnicodeDecodeError:
                        matched_text = matched_text_bytes.hex()
                        
                detections.append(Detection(
                    scanner=self.name,
                    channel_id=channel.channel_id,
                    severity=severity,
                    score=score,
                    attack_type=match.rule,
                    explanation=f"YARA rule triggered: {match.rule}",
                    matched_text=matched_text[:100]
                ))
        except Exception as e:
            log.error("yara_scan_error", error=str(e))
            
        return detections
