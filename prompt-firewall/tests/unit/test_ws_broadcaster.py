"""
Tests for AEGIS Phase 2 — ConnectionManager / WebSocket Broadcaster

Verifies:
  - connect/disconnect lifecycle
  - max connection cap enforcement
  - broadcast to multiple clients
  - dead client cleanup on send failure
  - disconnect_all on shutdown
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch
from app.services.ws_broadcaster import ConnectionManager


class FakeWebSocket:
    """Minimal WebSocket mock for testing."""
    
    def __init__(self, connected=True):
        self._connected = connected
        self.accepted = False
        self.closed = False
        self.close_code = None
        self.close_reason = None
        self.sent_messages = []

    @property
    def client_state(self):
        from starlette.websockets import WebSocketState
        return WebSocketState.CONNECTED if self._connected else WebSocketState.DISCONNECTED

    async def accept(self):
        self.accepted = True

    async def close(self, code=1000, reason=""):
        self.closed = True
        self.close_code = code
        self.close_reason = reason
        self._connected = False

    async def send_json(self, data):
        if not self._connected:
            raise RuntimeError("WebSocket is disconnected")
        self.sent_messages.append(data)

    async def receive_text(self):
        raise Exception("Not implemented in test")


class TestConnectionLifecycle:
    async def test_connect_accepts_websocket(self):
        """connect() should accept the websocket and register it."""
        manager = ConnectionManager(max_connections=10)
        ws = FakeWebSocket()

        result = await manager.connect(ws)

        assert result is True
        assert ws.accepted is True
        assert manager.active_count == 1

    async def test_disconnect_removes_websocket(self):
        """disconnect() should remove the websocket from active connections."""
        manager = ConnectionManager(max_connections=10)
        ws = FakeWebSocket()
        await manager.connect(ws)

        await manager.disconnect(ws)

        assert manager.active_count == 0

    async def test_disconnect_unknown_websocket_is_safe(self):
        """disconnect() should not raise for unregistered websockets."""
        manager = ConnectionManager(max_connections=10)
        ws = FakeWebSocket()

        await manager.disconnect(ws)  # Should not raise
        assert manager.active_count == 0


class TestMaxConnectionCap:
    async def test_rejects_when_at_capacity(self):
        """Should reject new connections when max capacity is reached."""
        manager = ConnectionManager(max_connections=2)

        ws1 = FakeWebSocket()
        ws2 = FakeWebSocket()
        ws3 = FakeWebSocket()

        assert await manager.connect(ws1) is True
        assert await manager.connect(ws2) is True
        assert await manager.connect(ws3) is False
        assert ws3.closed is True
        assert manager.active_count == 2

    async def test_can_connect_after_disconnect(self):
        """Should allow new connections after existing ones disconnect."""
        manager = ConnectionManager(max_connections=1)

        ws1 = FakeWebSocket()
        ws2 = FakeWebSocket()

        assert await manager.connect(ws1) is True
        await manager.disconnect(ws1)
        assert await manager.connect(ws2) is True
        assert manager.active_count == 1


class TestBroadcast:
    async def test_broadcast_to_multiple_clients(self):
        """broadcast() should send to all connected clients."""
        manager = ConnectionManager(max_connections=10)

        ws1 = FakeWebSocket()
        ws2 = FakeWebSocket()
        ws3 = FakeWebSocket()

        await manager.connect(ws1)
        await manager.connect(ws2)
        await manager.connect(ws3)

        await manager.broadcast({"type": "TEST", "data": "hello"})

        assert len(ws1.sent_messages) == 1
        assert len(ws2.sent_messages) == 1
        assert len(ws3.sent_messages) == 1
        assert ws1.sent_messages[0] == {"type": "TEST", "data": "hello"}

    async def test_broadcast_removes_dead_clients(self):
        """broadcast() should remove clients that fail to receive."""
        manager = ConnectionManager(max_connections=10)

        ws1 = FakeWebSocket(connected=True)
        ws2 = FakeWebSocket(connected=False)  # Dead client

        await manager.connect(ws1)
        # Manually add the dead client (simulating a connection that died)
        manager._connections.append(ws2)

        await manager.broadcast({"type": "TEST"})

        assert len(ws1.sent_messages) == 1
        assert manager.active_count == 1  # Dead client removed

    async def test_broadcast_to_empty_list(self):
        """broadcast() with no clients should not raise."""
        manager = ConnectionManager(max_connections=10)

        await manager.broadcast({"type": "TEST"})  # Should not raise


class TestPersonalMessage:
    async def test_send_personal(self):
        """send_personal() should send to a specific client."""
        manager = ConnectionManager(max_connections=10)

        ws = FakeWebSocket()
        await manager.connect(ws)

        await manager.send_personal(ws, {"type": "HELLO"})

        assert len(ws.sent_messages) == 1
        assert ws.sent_messages[0] == {"type": "HELLO"}

    async def test_send_personal_to_dead_client(self):
        """send_personal() should not raise for dead clients."""
        manager = ConnectionManager(max_connections=10)

        ws = FakeWebSocket(connected=False)

        await manager.send_personal(ws, {"type": "HELLO"})  # Should not raise


class TestDisconnectAll:
    async def test_disconnect_all(self):
        """disconnect_all() should close and remove all connections."""
        manager = ConnectionManager(max_connections=10)

        ws1 = FakeWebSocket()
        ws2 = FakeWebSocket()

        await manager.connect(ws1)
        await manager.connect(ws2)

        await manager.disconnect_all()

        assert manager.active_count == 0
        assert ws1.closed is True
        assert ws2.closed is True
