from typing import List, Dict, Any
from app.db.repositories.documents_repo import DocumentsRepo
from app.db.repositories.document_chunks_repo import DocumentChunksRepo
from app.services.chunking_service import ChunkingService
from app.scanners.engine import ScanEngine
from app.services.event_service import EventService
from app.schemas.ingest import DocumentIngestRequest, DocumentIngestResponse
from app.db.models import DocumentModel, DocumentChunkModel
from app.schemas.common import ChannelText
import uuid

class DocumentService:
    def __init__(self,
                 documents_repo: DocumentsRepo,
                 document_chunks_repo: DocumentChunksRepo,
                 chunker: ChunkingService,
                 scan_engine: ScanEngine,
                 event_service: EventService):
        self.documents_repo = documents_repo
        self.document_chunks_repo = document_chunks_repo
        self.chunker = chunker
        self.scan_engine = scan_engine
        self.event_service = event_service

    async def process_document(self, request: DocumentIngestRequest) -> DocumentIngestResponse:
        chunks_text = self.chunker.chunk_text(request.text)
        
        # Save Document
        doc = DocumentModel(
            tenant_id=request.tenant_id,
            document_id=request.document_id,
            name=request.name,
            source_type=request.source_type,
            status="processing"
        )
        doc = await self.documents_repo.create_document(doc)
        
        max_chunk_risk = 0.0
        suspicious_chunks = 0
        overall_risk = 0.0
        
        chunk_models = []
        # Process Chunks
        for idx, chunk_text in enumerate(chunks_text):
            chunk_id = f"{request.document_id}_chunk_{idx}"
            channel = ChannelText(
                channel_id=chunk_id,
                text=chunk_text,
                source_type="document_chunk"
            )
            
            detections = await self.scan_engine.scan_channel(channel)
            
            chunk_risk = max([d.score for d in detections]) if detections else 0.0
            attack_type = detections[0].attack_type if detections else None
            quarantined = chunk_risk >= 0.8
            
            if quarantined:
                suspicious_chunks += 1
            max_chunk_risk = max(max_chunk_risk, chunk_risk)
            
            chunk_model = DocumentChunkModel(
                document_fk=doc.id,
                chunk_id=chunk_id,
                chunk_index=idx,
                chunk_text=chunk_text,
                risk_score=chunk_risk,
                attack_type=attack_type,
                quarantined=quarantined
            )
            chunk_models.append(chunk_model)
            
            if quarantined:
                 # Emit event for attack detected
                 await self.event_service.emit_ingest_events(source_kind="document", source_id=request.document_id, chunk_id=chunk_id, detections=detections)
        
        overall_risk = max_chunk_risk
        
        await self.document_chunks_repo.create_chunks(chunk_models)
        
        doc.status = "processed"
        doc.overall_risk = overall_risk
        doc.suspicious_chunks_count = suspicious_chunks
        await self.documents_repo.session.commit()
        
        return DocumentIngestResponse(
            document_id=request.document_id,
            chunks_total=len(chunks_text),
            suspicious_chunks=suspicious_chunks,
            max_chunk_risk=max_chunk_risk,
            overall_risk=overall_risk,
            status="processed"
        )
