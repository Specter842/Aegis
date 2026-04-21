from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Annotated, List
from app.schemas.ingest import DocumentIngestRequest, DocumentIngestResponse, DocumentDetailResponse, ChunkDetail
from app.services.document_service import DocumentService
from app.api.deps import get_document_service, get_db_session
from app.db.repositories.documents_repo import DocumentsRepo
from app.db.repositories.document_chunks_repo import DocumentChunksRepo
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/v1/documents", tags=["Documents"])

@router.post("/ingest", response_model=DocumentIngestResponse)
async def ingest_document(
    request: DocumentIngestRequest,
    service: Annotated[DocumentService, Depends(get_document_service)]
):
    return await service.process_document(request)

@router.get("", response_model=List[DocumentDetailResponse])
async def list_documents(
    tenant_id: str = Query(..., description="Filter by tenant ID"),
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_db_session)
):
    repo = DocumentsRepo(session)
    docs = await repo.list_documents(tenant_id=tenant_id, limit=limit, offset=offset)
    return [DocumentDetailResponse(
        id=d.id, tenant_id=d.tenant_id, document_id=d.document_id, name=d.name, source_type=d.source_type,
        status=d.status, overall_risk=d.overall_risk, suspicious_chunks_count=d.suspicious_chunks_count, created_at=d.created_at
    ) for d in docs]

@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    repo = DocumentsRepo(session)
    doc = await repo.get_document_by_id(document_id)
    if not doc:
         raise HTTPException(status_code=404, detail="Document not found")
    return DocumentDetailResponse(
        id=doc.id, tenant_id=doc.tenant_id, document_id=doc.document_id, name=doc.name, source_type=doc.source_type,
        status=doc.status, overall_risk=doc.overall_risk, suspicious_chunks_count=doc.suspicious_chunks_count, created_at=doc.created_at
    )

@router.get("/{document_id}/chunks", response_model=List[ChunkDetail])
async def get_document_chunks(
    document_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    repo = DocumentsRepo(session)
    doc = await repo.get_document_by_id(document_id)
    if not doc:
         raise HTTPException(status_code=404, detail="Document not found")
    
    chunks_repo = DocumentChunksRepo(session)
    chunks = await chunks_repo.get_chunks_for_document(doc.id)
    return [ChunkDetail(
        chunk_id=c.chunk_id, chunk_index=c.chunk_index, chunk_text=c.chunk_text, risk_score=c.risk_score,
        attack_type=c.attack_type, quarantined=bool(c.quarantined), created_at=c.created_at
    ) for c in chunks]
