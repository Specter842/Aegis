from pydantic import BaseModel
from typing import Dict, Any, Callable, Awaitable
import asyncio
from app.scanners.registry import ScannerRegistry
from app.db.session import AsyncSessionLocal
from sqlalchemy import text
from app.core.logging import get_logger

log = get_logger(__name__)

class ComponentStatus(BaseModel):
    is_ready: bool
    diagnostic: str = "ok"
    is_critical: bool = True

class ReadinessService:
    def __init__(self, scanner_registry: ScannerRegistry):
        self.registry = scanner_registry
        
    async def check_database(self) -> ComponentStatus:
        try:
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))
            return ComponentStatus(is_ready=True)
        except Exception as e:
            return ComponentStatus(is_ready=False, diagnostic=str(e), is_critical=True)
            
    def check_scanners(self) -> Dict[str, ComponentStatus]:
        status_map = {}
        for scanner in self.registry.get_all():
            h = scanner.readiness()
            status_map[scanner.name] = ComponentStatus(
                is_ready=h.is_ready,
                diagnostic=h.diagnostic or "ready",
                is_critical=scanner.is_critical
            )
        return status_map
        
    async def evaluate_readiness(self) -> tuple[bool, Dict[str, Any]]:
        components = {}
        
        # Check DB
        db_status = await self.check_database()
        components["database"] = db_status.model_dump()
        
        # Check scanners
        scanner_statuses = self.check_scanners()
        for k, v in scanner_statuses.items():
            components[k] = v.model_dump()
            
        # A component is ready if all CRITICAL components are ready
        is_ready = True
        for name, status in components.items():
            if status["is_critical"] and not status["is_ready"]:
                log.error("readiness_critical_failure", component=name, diagnostic=status["diagnostic"])
                is_ready = False
                
        return is_ready, {"components": components, "status": "ready" if is_ready else "not_ready"}
