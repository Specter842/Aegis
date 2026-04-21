from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # App params
    APP_NAME: str = "AEGIS Prompt Firewall"
    ENVIRONMENT: str = "dev"
    LOG_LEVEL: str = "INFO"
    
    # DB params
    DATABASE_URL: str = "postgresql+asyncpg://aegis:aegis@localhost:5432/aegis_db"
    
    # Scanner params
    ENABLE_LLM_GUARD: bool = True
    # "strict" means readiness fails if ML models don't load. "degraded" means it warns.
    LLM_GUARD_READINESS_MODE: str = "strict" 
    
    # WebSocket params
    WS_MAX_CONNECTIONS: int = 50
    WS_HEARTBEAT_INTERVAL: int = 30  # seconds, 0 to disable
    
    # Security limits
    MAX_PROMPT_CHARS: int = 10000
    MAX_HISTORY_ITEMS: int = 50
    MAX_MESSAGE_CHARS: int = 4000
    MAX_PAYLOAD_BYTES: int = 1024 * 1024 # 1 MB
    
    # Ingestion params
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    URL_FETCH_TIMEOUT: int = 10
    MAX_URL_PAYLOAD_BYTES: int = 5 * 1024 * 1024 # 5 MB
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
