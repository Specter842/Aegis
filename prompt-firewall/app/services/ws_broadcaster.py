"""
AEGIS Phase 2 — WebSocket Connection Manager / Broadcaster

Manages concurrent WebSocket connections and provides safe broadcast
to all connected clients. Designed as a singleton stored on app.state.

Features:
  - connection cap (configurable, default 50)
  - safe disconnect cleanup
  - broadcast with dead-client removal
  - personal message for initial handshake
  - asyncio lock for concurrent safety
"""

from __future__ import annotations

import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
from app.core.logging import get_logger

log = get_logger("ws_broadcaster")


class ConnectionManager:
    """
    Manages WebSocket connections for AEGIS real-time event broadcasting.
    
    Usage:
        manager = ConnectionManager(max_connections=50)
        app.state.ws_manager = manager
    """

    def __init__(self, max_connections: int = 50):
        self._connections: list[WebSocket] = []
        self._max_connections = max_connections
        self._lock = asyncio.Lock()

    @property
    def active_count(self) -> int:
        return len(self._connections)

    async def connect(self, websocket: WebSocket) -> bool:
        """
        Accept and register a WebSocket connection.
        Returns False if connection cap is reached.
        """
        async with self._lock:
            if len(self._connections) >= self._max_connections:
                log.warning(
                    "ws_connection_rejected",
                    reason="max_connections_reached",
                    current=len(self._connections),
                    max=self._max_connections,
                )
                await websocket.close(code=1013, reason="Maximum connections reached")
                return False

            await websocket.accept()
            self._connections.append(websocket)
            log.info(
                "ws_client_connected",
                total_connections=len(self._connections),
            )
            return True

    async def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection safely."""
        async with self._lock:
            if websocket in self._connections:
                self._connections.remove(websocket)
                log.info(
                    "ws_client_disconnected",
                    total_connections=len(self._connections),
                )

    async def broadcast(self, data: dict):
        """
        Send a JSON payload to all connected clients.
        Dead clients are removed automatically.
        """
        dead_connections: list[WebSocket] = []

        # Snapshot under lock, send outside lock to avoid holding it during I/O
        async with self._lock:
            connections_snapshot = list(self._connections)

        for ws in connections_snapshot:
            try:
                if ws.client_state == WebSocketState.CONNECTED:
                    await ws.send_json(data)
                else:
                    dead_connections.append(ws)
            except Exception as e:
                log.warning("ws_send_failed", error=str(e))
                dead_connections.append(ws)

        # Clean up dead connections
        if dead_connections:
            async with self._lock:
                for ws in dead_connections:
                    if ws in self._connections:
                        self._connections.remove(ws)
                log.info(
                    "ws_dead_clients_removed",
                    removed=len(dead_connections),
                    remaining=len(self._connections),
                )

    async def send_personal(self, websocket: WebSocket, data: dict):
        """Send a JSON payload to a specific client (e.g., handshake)."""
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_json(data)
        except Exception as e:
            log.warning("ws_personal_send_failed", error=str(e))

    async def disconnect_all(self):
        """Disconnect all clients. Called on shutdown."""
        async with self._lock:
            for ws in self._connections:
                try:
                    await ws.close(code=1001, reason="Server shutting down")
                except Exception:
                    pass
            self._connections.clear()
            log.info("ws_all_clients_disconnected")
