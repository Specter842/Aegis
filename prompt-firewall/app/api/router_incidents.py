"""
AEGIS Phase 2 — Incidents REST API

GET /v1/incidents — Retrieve stored scan incidents with optional filtering.
Used by the dashboard to bootstrap history on page load.
"""

from __future__ import annotations

from typing import Optional, Annotated
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db_session
from app.db.repositories.incidents_repo import IncidentsRepo
from app.core.logging import get_logger

log = get_logger("router_incidents")

router = APIRouter(prefix="/v1", tags=["Incidents"])


def get_incidents_repo(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> IncidentsRepo:
    return IncidentsRepo(session)


@router.get("/incidents", status_code=status.HTTP_200_OK)
async def list_incidents(
    repo: Annotated[IncidentsRepo, Depends(get_incidents_repo)],
    limit: int = Query(default=50, ge=1, le=200, description="Max incidents to return"),
    decision: Optional[str] = Query(default=None, description="Filter by decision: allow, sanitize, challenge, block"),
    attack_type: Optional[str] = Query(default=None, description="Filter by attack type"),
    min_risk: Optional[float] = Query(default=None, ge=0.0, le=1.0, description="Minimum risk score"),
):
    """
    Retrieve stored scan incidents, newest first.
    
    Used by the AEGIS dashboard to:
      - Bootstrap incident history on page load
      - Populate the attack timeline with historical data
      - Show incident details in forensics panels
    """
    try:
        incidents = await repo.get_incidents(
            limit=limit,
            decision=decision,
            attack_type=attack_type,
            min_risk=min_risk,
        )
        total = await repo.get_incident_count(decision=decision)

        return {
            "incidents": incidents,
            "total": total,
            "limit": limit,
            "filters": {
                "decision": decision,
                "attack_type": attack_type,
                "min_risk": min_risk,
            },
        }
    except Exception as e:
        log.error("incidents_fetch_failed", error=str(e), exc_info=True)
        return {
            "incidents": [],
            "total": 0,
            "limit": limit,
            "filters": {},
            "error": "Failed to fetch incidents",
        }
