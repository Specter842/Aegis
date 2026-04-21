import asyncio
from app.schemas.scan import Detection
from app.schemas.common import ChannelText
from app.scanners.registry import ScannerRegistry
from app.core.constants import ScanStage
from app.core.logging import get_logger
from app.core.exceptions import CriticalScannerError

log = get_logger(__name__)

class ScanEngine:
    def __init__(self, registry: ScannerRegistry):
        self.registry = registry
        self.timeout_sec = 2.0  # 2 second max per scanner
        
    async def scan_channel(self, channel: ChannelText) -> list[Detection]:
        all_detections = []
        
        # Run in order: PRE_PROCESS -> STATIC -> ML -> POST_PROCESS
        for stage in [ScanStage.PRE_PROCESS, ScanStage.STATIC, ScanStage.ML, ScanStage.POST_PROCESS]:
            scanners = self.registry.get_scanners_for_stage(stage)
            
            # Filter by supported source types
            valid_scanners = [s for s in scanners if channel.source_type in s.supported_source_types]
            if not valid_scanners:
                continue
                
            # Execute concurrently within the stage
            tasks = [self._execute_scanner(scanner, channel) for scanner in valid_scanners]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for scanner, result in zip(valid_scanners, results):
                if isinstance(result, Exception):
                    log.error("scanner_failed", scanner_name=scanner.name, error=str(result))
                    if scanner.is_critical:
                        raise CriticalScannerError(f"Critical scanner {scanner.name} failed", scanner.name, result)
                    continue
                    
                all_detections.extend(result)
                
        return all_detections
        
    async def _execute_scanner(self, scanner, channel: ChannelText) -> list[Detection]:
        # Guard against unready scanners
        health = scanner.readiness()
        if not health.is_ready:
            log.debug("scanner_not_ready_skip", scanner=scanner.name)
            return []
            
        try:
            return await asyncio.wait_for(scanner.scan(channel), timeout=self.timeout_sec)
        except asyncio.TimeoutError as e:
            raise Exception(f"Timeout ({self.timeout_sec}s)") from e
