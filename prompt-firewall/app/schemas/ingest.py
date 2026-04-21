from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class DocumentIngestRequest(BaseModel):
    tenant_id: str
    document_id: str
    name: str = "Unknown Document"
    source_type: str = "upload"
    text: str = Field(..., description="The full text contents to be chunked and scanned")

class DocumentIngestResponse(BaseModel):
    document_id: str
    chunks_total: int
    suspicious_chunks: int
    max_chunk_risk: float
    overall_risk: float
    status: str

class UrlIngestRequest(BaseModel):
    tenant_id: str
    url_id: str
    url: str
    domain: Optional[str] = None
    source_type: str = "web"

class UrlIngestResponse(BaseModel):
    url_id: str
    chunks_total: int
    suspicious_chunks: int
    max_chunk_risk: float
    overall_risk: float
    status: str

class ChunkDetail(BaseModel):
    chunk_id: str
    chunk_index: int
    chunk_text: str
    risk_score: float
    attack_type: Optional[str] = None
    quarantined: bool
    created_at: datetime

class DocumentDetailResponse(BaseModel):
    id: int # Database ID
    tenant_id: str
    document_id: str
    name: Optional[str] = None
    source_type: str
    status: str
    overall_risk: float
    suspicious_chunks_count: int
    created_at: datetime

class UrlDetailResponse(BaseModel):
    id: int # Database ID
    tenant_id: str
    url_id: str
    url: str
    domain: Optional[str] = None
    status: str
    overall_risk: float
    suspicious_chunks_count: int
    created_at: datetime
