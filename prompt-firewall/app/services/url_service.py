from bs4 import BeautifulSoup
import httpx
from app.core.config import settings
from app.db.repositories.url_sources_repo import UrlSourcesRepo
from app.db.repositories.url_chunks_repo import UrlChunksRepo
from app.services.chunking_service import ChunkingService
from app.scanners.engine import ScanEngine
from app.services.event_service import EventService
from app.schemas.ingest import UrlIngestRequest, UrlIngestResponse
from app.db.models import UrlSourceModel, UrlChunkModel
from app.schemas.common import ChannelText

class UrlService:
    def __init__(self,
                 url_sources_repo: UrlSourcesRepo,
                 url_chunks_repo: UrlChunksRepo,
                 chunker: ChunkingService,
                 scan_engine: ScanEngine,
                 event_service: EventService):
        self.url_sources_repo = url_sources_repo
        self.url_chunks_repo = url_chunks_repo
        self.chunker = chunker
        self.scan_engine = scan_engine
        self.event_service = event_service

    async def process_url(self, request: UrlIngestRequest) -> UrlIngestResponse:
        # Fetch and parse
        async with httpx.AsyncClient() as client:
            resp = await client.get(request.url, timeout=settings.URL_FETCH_TIMEOUT)
            resp.raise_for_status()
            html = resp.text
            
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        
        chunks_text = self.chunker.chunk_text(text)
        
        src = UrlSourceModel(
            tenant_id=request.tenant_id,
            url_id=request.url_id,
            url=request.url,
            domain=request.domain,
            status="processing"
        )
        src = await self.url_sources_repo.create_url_source(src)
        
        max_chunk_risk = 0.0
        suspicious_chunks = 0
        
        chunk_models = []
        for idx, chunk_text in enumerate(chunks_text):
            chunk_id = f"{request.url_id}_chunk_{idx}"
            channel = ChannelText(
                channel_id=chunk_id,
                text=chunk_text,
                source_type="url_content"
            )
            
            detections = await self.scan_engine.scan_channel(channel)
            chunk_risk = max([d.score for d in detections]) if detections else 0.0
            attack_type = detections[0].attack_type if detections else None
            quarantined = chunk_risk >= 0.8
            
            if quarantined:
                suspicious_chunks += 1
            max_chunk_risk = max(max_chunk_risk, chunk_risk)
            
            chunk_models.append(UrlChunkModel(
                url_source_fk=src.id,
                chunk_id=chunk_id,
                chunk_index=idx,
                chunk_text=chunk_text,
                risk_score=chunk_risk,
                attack_type=attack_type,
                quarantined=quarantined
            ))
            
            if quarantined:
                 await self.event_service.emit_ingest_events(source_kind="url", source_id=request.url_id, chunk_id=chunk_id, detections=detections)
                 
        await self.url_chunks_repo.create_chunks(chunk_models)
        
        src.status = "processed"
        src.overall_risk = max_chunk_risk
        src.suspicious_chunks_count = suspicious_chunks
        await self.url_sources_repo.session.commit()
        
        return UrlIngestResponse(
            url_id=request.url_id,
            chunks_total=len(chunks_text),
            suspicious_chunks=suspicious_chunks,
            max_chunk_risk=max_chunk_risk,
            overall_risk=max_chunk_risk,
            status="processed"
        )
