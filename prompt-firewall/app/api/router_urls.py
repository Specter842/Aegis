from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Annotated, List
from app.schemas.ingest import UrlIngestRequest, UrlIngestResponse, UrlDetailResponse, ChunkDetail
from app.services.url_service import UrlService
from app.api.deps import get_url_service, get_db_session
from app.db.repositories.url_sources_repo import UrlSourcesRepo
from app.db.repositories.url_chunks_repo import UrlChunksRepo
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/v1/urls", tags=["URLs"])

@router.post("/ingest", response_model=UrlIngestResponse)
async def ingest_url(
    request: UrlIngestRequest,
    service: Annotated[UrlService, Depends(get_url_service)]
):
    try:
        return await service.process_url(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=List[UrlDetailResponse])
async def list_urls(
    tenant_id: str = Query(..., description="Filter by tenant ID"),
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_db_session)
):
    repo = UrlSourcesRepo(session)
    urls = await repo.list_url_sources(tenant_id=tenant_id, limit=limit, offset=offset)
    return [UrlDetailResponse(
        id=u.id, tenant_id=u.tenant_id, url_id=u.url_id, url=u.url, domain=u.domain,
        status=u.status, overall_risk=u.overall_risk, suspicious_chunks_count=u.suspicious_chunks_count, created_at=u.created_at
    ) for u in urls]

@router.get("/{url_id}", response_model=UrlDetailResponse)
async def get_url(
    url_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    repo = UrlSourcesRepo(session)
    url = await repo.get_url_source_by_id(url_id)
    if not url:
         raise HTTPException(status_code=404, detail="URL not found")
    return UrlDetailResponse(
        id=url.id, tenant_id=url.tenant_id, url_id=url.url_id, url=url.url, domain=url.domain,
        status=url.status, overall_risk=url.overall_risk, suspicious_chunks_count=url.suspicious_chunks_count, created_at=url.created_at
    )

@router.get("/{url_id}/chunks", response_model=List[ChunkDetail])
async def get_url_chunks(
    url_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    repo = UrlSourcesRepo(session)
    url = await repo.get_url_source_by_id(url_id)
    if not url:
         raise HTTPException(status_code=404, detail="URL not found")
    
    chunks_repo = UrlChunksRepo(session)
    chunks = await chunks_repo.get_chunks_for_url_source(url.id)
    return [ChunkDetail(
        chunk_id=c.chunk_id, chunk_index=c.chunk_index, chunk_text=c.chunk_text, risk_score=c.risk_score,
        attack_type=c.attack_type, quarantined=bool(c.quarantined), created_at=c.created_at
    ) for c in chunks]
