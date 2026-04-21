import asyncio
from collections import defaultdict
from app.scanners.base import BaseScanner
from app.core.constants import ScanStage
from app.core.logging import get_logger

log = get_logger(__name__)

class ScannerRegistry:
    def __init__(self):
        self._scanners: dict[str, BaseScanner] = {}
        self._by_stage: dict[ScanStage, list[BaseScanner]] = defaultdict(list)
        self._initialized = False

    def register(self, scanner: BaseScanner):
        if scanner.name in self._scanners:
            log.warning("scanner_already_registered", scanner_name=scanner.name)
            return
            
        self._scanners[scanner.name] = scanner
        self._by_stage[scanner.stage].append(scanner)
        log.info("scanner_registered", scanner_name=scanner.name, stage=scanner.stage.value)
        
    def get_scanners_for_stage(self, stage: ScanStage) -> list[BaseScanner]:
        return self._by_stage.get(stage, [])
        
    def get_all(self) -> list[BaseScanner]:
        return list(self._scanners.values())
