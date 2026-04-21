"""
AEGIS Phase 2 — WebSocket Endpoint

Provides the /ws/aegis WebSocket route for real-time event broadcasting.

Behavior:
  - On connect: sends SYSTEM_STATUS event immediately
  - Read-only from client perspective: client messages are ignored
  - Keep-alive via read loop (detects disconnect)
  - Clean disconnect handling
"""

from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.services.ws_broadcaster import ConnectionManager
from app.services.event_service import EventService
from app.core.logging import get_logger

log = get_logger("router_ws")

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/aegis")
async def aegis_websocket(websocket: WebSocket):
    """
    Real-time AEGIS event stream.
    
    On connect:
      - Client is registered with the ConnectionManager
      - Receives an immediate SYSTEM_STATUS event
    
    During session:
      - Receives broadcast events (SCAN_COMPLETED, ATTACK_DETECTED)
      - Client messages are read but not processed (keeps connection alive)
    
    On disconnect:
      - Client is safely removed from the manager
    """
    # Access services from app state
    ws_manager: ConnectionManager = websocket.app.state.ws_manager
    event_service: EventService = websocket.app.state.event_service

    # Attempt connection
    accepted = await ws_manager.connect(websocket)
    if not accepted:
        return  # Connection rejected (cap reached)

    try:
        # Send initial SYSTEM_STATUS on connect
        try:
            status_event = await event_service.build_system_status()
            await ws_manager.send_personal(websocket, status_event.model_dump())
        except Exception as e:
            log.warning("ws_initial_status_failed", error=str(e))

        # Read loop — keeps connection alive
        # Client messages are read but not acted upon (read-only broadcast model)
        while True:
            try:
                _ = await websocket.receive_text()
                # Intentionally ignore client messages
            except WebSocketDisconnect:
                break

    except Exception as e:
        log.warning("ws_connection_error", error=str(e))
    finally:
        await ws_manager.disconnect(websocket)
