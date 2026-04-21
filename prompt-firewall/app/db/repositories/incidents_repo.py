"""
AEGIS Phase 2 — Incidents Repository

Database queries for retrieving stored scan incidents.
Supports filtering, pagination, and safe data retrieval.
"""

from __future__ import annotations

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from sqlalchemy.orm import selectinload
from app.db.models import ScanRequestModel, ScanDetectionModel, ScanChannelModel
from app.core.logging import get_logger

log = get_logger("incidents_repo")


class IncidentsRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_incidents(
        self,
        limit: int = 50,
        decision: Optional[str] = None,
        attack_type: Optional[str] = None,
        min_risk: Optional[float] = None,
    ) -> list[dict]:
        """
        Retrieve stored incidents (scan requests with detections).
        
        Args:
            limit: Maximum number of results (capped at 200)
            decision: Filter by decision (allow, sanitize, challenge, block)
            attack_type: Filter by attack type in detections
            min_risk: Minimum risk score threshold
            
        Returns:
            List of incident dicts, newest first
        """
        limit = min(limit, 200)

        # Start with base query
        stmt = (
            select(ScanRequestModel)
            .order_by(desc(ScanRequestModel.created_at))
        )

        # Apply filters
        if decision:
            stmt = stmt.where(ScanRequestModel.decision == decision)

        if min_risk is not None:
            stmt = stmt.where(ScanRequestModel.risk_score >= min_risk)

        if attack_type:
            # Join with detections to filter by attack type
            stmt = stmt.join(
                ScanDetectionModel,
                ScanDetectionModel.request_fk == ScanRequestModel.id,
            ).where(ScanDetectionModel.attack_type == attack_type).distinct()

        stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        requests = result.scalars().all()

        # Fetch detections for each request
        incidents = []
        for req in requests:
            # Eagerly load detections
            det_stmt = (
                select(ScanDetectionModel)
                .where(ScanDetectionModel.request_fk == req.id)
                .order_by(desc(ScanDetectionModel.score))
            )
            det_result = await self.session.execute(det_stmt)
            detections = det_result.scalars().all()

            incidents.append(self._format_incident(req, detections))

        return incidents

    async def get_incident_count(
        self,
        decision: Optional[str] = None,
    ) -> int:
        """Get total count of incidents, optionally filtered."""
        stmt = select(func.count(ScanRequestModel.id))
        if decision:
            stmt = stmt.where(ScanRequestModel.decision == decision)
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    def _format_incident(
        self,
        req: ScanRequestModel,
        detections: list[ScanDetectionModel],
    ) -> dict:
        """Format a request + detections into a safe incident dict."""
        return {
            "id": req.id,
            "request_id": req.request_id,
            "trace_id": req.trace_id,
            "tenant_id": req.tenant_id,
            "app_id": req.app_id,
            "decision": req.decision,
            "risk_score": req.risk_score,
            "created_at": req.created_at.isoformat() if req.created_at else None,
            "detection_count": len(detections),
            "detections": [
                {
                    "scanner": d.scanner_name,
                    "attack_type": d.attack_type,
                    "severity": d.severity,
                    "score": d.score,
                    "explanation": d.explanation,
                    # Truncate matched text for safety
                    "matched_excerpt": (
                        d.matched_text[:80] + "..."
                        if d.matched_text and len(d.matched_text) > 80
                        else d.matched_text or ""
                    ),
                }
                for d in detections
            ],
        }
