from typing import List
from app.db.repositories.requests_repo import RequestsRepo
from app.db.repositories.channels_repo import ChannelsRepo
from app.db.repositories.detections_repo import DetectionsRepo
from app.schemas.scan import ScanRequest, ScanResult
from app.schemas.common import ChannelText
from app.core.security import redact_text
from app.core.logging import get_logger

log = get_logger(__name__)

class PersistenceService:
    def __init__(self, requests_repo: RequestsRepo, channels_repo: ChannelsRepo, detections_repo: DetectionsRepo):
        self.requests_repo = requests_repo
        self.channels_repo = channels_repo
        self.detections_repo = detections_repo
        
    async def save_scan_result(self, request: ScanRequest, channels: List[ChannelText], result: ScanResult):
        try:
            # Save Request
            req_model = self.requests_repo.add({
                "request_id": request.request_id,
                "tenant_id": request.tenant_id,
                "app_id": request.app_id,
                "user_id": request.user_id,
                "raw_prompt": request.prompt, # in a real system we might truncate/redact this before DB
                "normalized_prompt": channels[0].text if channels else None,
                "decision": result.decision,
                "risk_score": result.risk_score,
                "trace_id": result.trace_id
            })
            
            # Commit request to get ID
            await self.requests_repo.session.commit()
            await self.requests_repo.session.refresh(req_model)
            
            channel_id_to_pk = {}
            
            # Save Channels
            for ch in channels:
                chan_model = self.channels_repo.add({
                    "request_fk": req_model.id,
                    "channel_id": ch.channel_id,
                    "source_type": ch.source_type,
                    "trust_level": ch.trust_level,
                    "text_content": ch.text, 
                    "sanitized_content": result.sanitized_channels.get(ch.channel_id),
                    "risk_score": result.channel_scores.get(ch.channel_id, 0.0)
                })
                # We need PK for detections... doing a flush
                await self.channels_repo.session.flush()
                channel_id_to_pk[ch.channel_id] = chan_model.id
                
            # Save Detections
            det_data = []
            for d in result.detections:
                fk = channel_id_to_pk.get(d.channel_id)
                if not fk:
                    continue
                    
                det_data.append({
                    "request_fk": req_model.id,
                    "channel_fk": fk,
                    "scanner_name": d.scanner,
                    "attack_type": d.attack_type,
                    "severity": d.severity,
                    "score": d.score,
                    "matched_text": redact_text(d.matched_text, max_len=512),
                    "explanation": d.explanation,
                    "metadata_json": d.metadata
                })
                
            if det_data:
                self.detections_repo.add_many(det_data)
                
            await self.requests_repo.session.commit()
            log.info("scan_persisted", request_id=request.request_id, internal_id=req_model.id)
            
        except Exception as e:
            await self.requests_repo.session.rollback()
            log.error("persistence_failed", error=str(e), request_id=request.request_id)
