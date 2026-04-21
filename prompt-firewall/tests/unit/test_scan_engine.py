import pytest
import asyncio
from app.scanners.engine import ScanEngine
from app.scanners.registry import ScannerRegistry
from app.scanners.base import BaseScanner, ScannerHealth
from app.schemas.common import ChannelText
from app.core.constants import ScanStage, SourceType
from app.core.exceptions import CriticalScannerError

class SlowScanner(BaseScanner):
    @property
    def name(self) -> str: return "slow"
    @property
    def stage(self) -> ScanStage: return ScanStage.STATIC
    @property
    def supported_source_types(self) -> set[str]: return {SourceType.USER}
    @property
    def is_critical(self) -> bool: return False
    
    def readiness(self) -> ScannerHealth:
        return ScannerHealth(name="slow", is_ready=True)

    async def scan(self, channel: ChannelText):
        await asyncio.sleep(60) # Simulate hang
        return []

class FailingCriticalScanner(SlowScanner):
    @property
    def name(self) -> str: return "failing_crit"
    @property
    def is_critical(self) -> bool: return True
    
    async def scan(self, channel):
        raise ValueError("I crash always")

@pytest.mark.asyncio
async def test_scan_engine_timeouts_non_critical():
    registry = ScannerRegistry()
    registry.register(SlowScanner())
    engine = ScanEngine(registry)
    engine.timeout_sec = 0.1 # short timeout for test
    
    chan = ChannelText(channel_id="p", source_type="user", text="test")
    # Should not raise, just logs error and returns empty list
    results = await engine.scan_channel(chan)
    assert len(results) == 0

@pytest.mark.asyncio
async def test_scan_engine_fails_on_critical_error():
    registry = ScannerRegistry()
    registry.register(FailingCriticalScanner())
    engine = ScanEngine(registry)
    
    chan = ChannelText(channel_id="p", source_type="user", text="test")
    with pytest.raises(CriticalScannerError):
        await engine.scan_channel(chan)
