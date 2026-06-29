from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.api.router_health import router as health_router
from app.api.router_scan import router as scan_router
from app.api.router_legacy import router as legacy_router
from app.api.router_incidents import router as incidents_router
from app.api.router_ws import router as ws_router
from app.api.router_documents import router as documents_router
from app.api.router_urls import router as urls_router
from app.api.router_proxy import router as proxy_router
from app.api.router_feedback import router as feedback_router

from app.scanners.registry import ScannerRegistry
from app.scanners.engine import ScanEngine
from app.services.normalizer import NormalizerService
from app.services.policy_engine import PolicyEngine
from app.services.readiness_service import ReadinessService
from app.services.ws_broadcaster import ConnectionManager
from app.services.event_service import EventService

# Scanners
from app.scanners.static.regex_scanner import RegexScanner
from app.scanners.static.yara_scanner import YaraScanner
from app.scanners.static.unicode_scanner import UnicodeScanner
from app.scanners.static.encoded_text_scanner import EncodedTextScanner

from app.scanners.llm_guard.prompt_injection import LLMGuardPromptInjection
from app.scanners.llm_guard.secrets import LLMGuardSecrets
from app.scanners.llm_guard.invisible_text import LLMGuardInvisibleText
from app.scanners.llm_guard.token_limit import LLMGuardTokenLimit

log = get_logger("aegis")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup Logging
    setup_logging(settings.LOG_LEVEL)
    log.info("aegis_startup_started", version="0.3.0", env=settings.ENVIRONMENT)
    
    # Init Scanners & Services
    registry = ScannerRegistry()
    registry.register(RegexScanner())
    registry.register(YaraScanner())
    registry.register(UnicodeScanner())
    registry.register(EncodedTextScanner())
    
    registry.register(LLMGuardPromptInjection())
    registry.register(LLMGuardSecrets())
    registry.register(LLMGuardInvisibleText())
    registry.register(LLMGuardTokenLimit())
    
    # Phase 1 services
    readiness_service = ReadinessService(registry)
    
    # Phase 2 services — WebSocket + Events
    ws_manager = ConnectionManager(max_connections=settings.WS_MAX_CONNECTIONS)
    event_service = EventService(ws_manager, readiness_service)
    
    # Store services on app state
    app.state.scanner_registry = registry
    app.state.scan_engine = ScanEngine(registry)
    app.state.normalizer = NormalizerService()
    app.state.policy_engine = PolicyEngine()
    app.state.readiness_service = readiness_service
    app.state.ws_manager = ws_manager
    app.state.event_service = event_service
    
    log.info("aegis_startup_completed", phase="3", ws_max=settings.WS_MAX_CONNECTIONS)
    yield
    
    # Shutdown: disconnect all WS clients
    await ws_manager.disconnect_all()
    log.info("aegis_shutdown")

app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(scan_router)
app.include_router(legacy_router)
app.include_router(incidents_router)
app.include_router(ws_router)
app.include_router(documents_router)
app.include_router(urls_router)
app.include_router(proxy_router)
app.include_router(feedback_router, prefix="/v1/feedback", tags=["Feedback"])
