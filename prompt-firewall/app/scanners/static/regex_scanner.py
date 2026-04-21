import json
import re
from pathlib import Path
from app.scanners.base import BaseScanner, ScannerHealth
from app.schemas.common import ChannelText
from app.schemas.scan import Detection
from app.core.constants import ScanStage, SourceType

class RegexScanner(BaseScanner):
    def __init__(self, rules_path: str = "rules/suspicious_patterns.regex.json"):
        self._patterns = []
        self._is_ready = False
        self._error = None
        
        try:
            path = Path(rules_path)
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    raw_patterns = json.load(f)
                    for rp in raw_patterns:
                        self._patterns.append({
                            "compiled": re.compile(rp["pattern"], re.IGNORECASE),
                            "type": rp["type"],
                            "severity": rp["severity"],
                            "name": rp["name"]
                        })
                self._is_ready = True
            else:
                self._error = f"Rules file not found at {rules_path}"
        except Exception as e:
            self._error = str(e)

    @property
    def name(self) -> str:
        return "static_regex"

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
        return ScannerHealth(
            name=self.name,
            is_ready=self._is_ready,
            diagnostic=self._error
        )

    async def scan(self, channel: ChannelText) -> list[Detection]:
        detections = []
        if not self._is_ready:
            return detections
            
        for p in self._patterns:
            match = p["compiled"].search(channel.text)
            if match:
                score = 1.0 if p["severity"] == "critical" else 0.8 if p["severity"] == "high" else 0.5
                detections.append(Detection(
                    scanner=self.name,
                    channel_id=channel.channel_id,
                    severity=p["severity"],
                    score=score,
                    attack_type=p["type"],
                    explanation=f"Regex match for {p['name']}",
                    matched_text=match.group(0)
                ))
        return detections
