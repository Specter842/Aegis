from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Optional
from app.schemas.common import ChannelText
from app.schemas.scan import Detection
from app.core.constants import ScanStage

class ScannerHealth(BaseModel):
    name: str
    is_ready: bool
    diagnostic: Optional[str] = None

class BaseScanner(ABC):
    """
    Base contract for all scanners.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this scanner"""
        pass
        
    @property
    @abstractmethod
    def stage(self) -> ScanStage:
        """Pipeline stage to run in"""
        pass
        
    @property
    @abstractmethod
    def supported_source_types(self) -> set[str]:
        """Source types this scanner cares about (e.g. {'user', 'system'})"""
        pass
        
    @property
    @abstractmethod
    def is_critical(self) -> bool:
        """If True, scanner failure aborts the pipeline. If False, failure is isolated."""
        pass
        
    @abstractmethod
    def readiness(self) -> ScannerHealth:
        """Returns the readiness state of this scanner."""
        pass
        
    @abstractmethod
    async def scan(self, channel: ChannelText) -> list[Detection]:
        """Runs the scanner over the channel text. Returns empty list if no detections."""
        pass
