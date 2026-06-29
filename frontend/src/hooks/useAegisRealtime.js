/**
 * AEGIS Phase 2 — Real-Time WebSocket Hook
 * 
 * Connects to the backend WebSocket at /ws/aegis and provides:
 *  - Auto-reconnect with exponential backoff
 *  - Connection state tracking
 *  - Event parsing and buffering
 *  - System status from initial handshake
 *  - Graceful cleanup on unmount
 * 
 * Usage:
 *   const { isConnected, connectionState, lastEvent, recentEvents, systemStatus } = useAegisRealtime();
 */

import { useState, useEffect, useRef, useCallback } from 'react';

// ──────────────────────────────────────────
// Connection States
// ──────────────────────────────────────────
const CONNECTION_STATES = {
  CONNECTING: 'connecting',
  CONNECTED: 'connected',
  DISCONNECTED: 'disconnected',
  ERROR: 'error',
};

// ──────────────────────────────────────────
// Known Event Types
// ──────────────────────────────────────────
const EVENT_TYPES = {
  SYSTEM_STATUS: 'SYSTEM_STATUS',
  SCAN_COMPLETED: 'SCAN_COMPLETED',
  ATTACK_DETECTED: 'ATTACK_DETECTED',
};

// ──────────────────────────────────────────
// Backoff Config
// ──────────────────────────────────────────
const INITIAL_BACKOFF_MS = 1000;
const MAX_BACKOFF_MS = 30000;
const BACKOFF_MULTIPLIER = 2;
const MAX_RECENT_EVENTS = 100;

/**
 * Determine the WebSocket URL based on the current page location.
 * In development with Vite proxy, we connect to the same host.
 * In production, the backend URL can be overridden via env var.
 */
function getWsUrl() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.host;
  return `${protocol}//${host}/ws/aegis`;
}

export function useAegisRealtime(wsUrl = null) {
  const [connectionState, setConnectionState] = useState(CONNECTION_STATES.DISCONNECTED);
  const [lastEvent, setLastEvent] = useState(null);
  const [recentEvents, setRecentEvents] = useState([]);
  const [systemStatus, setSystemStatus] = useState(null);

  const wsRef = useRef(null);
  const backoffRef = useRef(INITIAL_BACKOFF_MS);
  const reconnectTimerRef = useRef(null);
  const mountedRef = useRef(true);
  const eventCallbacksRef = useRef([]);

  const isConnected = connectionState === CONNECTION_STATES.CONNECTED;

  // ──────────────────────────────────────────
  // Event listener registration
  // ──────────────────────────────────────────
  const onEvent = useCallback((callback) => {
    eventCallbacksRef.current.push(callback);
    return () => {
      eventCallbacksRef.current = eventCallbacksRef.current.filter(cb => cb !== callback);
    };
  }, []);

  // ──────────────────────────────────────────
  // Handle incoming message
  // ──────────────────────────────────────────
  const handleMessage = useCallback((rawData) => {
    try {
      const event = JSON.parse(rawData);

      if (!event.type) {
        console.warn('[AEGIS WS] Received event without type:', event);
        return;
      }

      switch (event.type) {
        case EVENT_TYPES.SYSTEM_STATUS:
          setSystemStatus(event);
          break;

        case EVENT_TYPES.SCAN_COMPLETED:
        case EVENT_TYPES.ATTACK_DETECTED:
          setLastEvent(event);
          setRecentEvents(prev => [event, ...prev].slice(0, MAX_RECENT_EVENTS));
          break;

        default:
          console.warn(`[AEGIS WS] Unknown event type: ${event.type}`, event);
          // Still store it — forward compatibility
          setLastEvent(event);
          setRecentEvents(prev => [event, ...prev].slice(0, MAX_RECENT_EVENTS));
          break;
      }

      // Notify all registered callbacks
      eventCallbacksRef.current.forEach(cb => {
        try { cb(event); } catch (e) { console.error('[AEGIS WS] Callback error:', e); }
      });

    } catch (e) {
      console.error('[AEGIS WS] Failed to parse message:', e, rawData);
    }
  }, []);

  // ──────────────────────────────────────────
  // Connect
  // ──────────────────────────────────────────
  const connect = useCallback(() => {
    if (!mountedRef.current) return;

    // Clean up any existing connection
    if (wsRef.current) {
      try { wsRef.current.close(); } catch (e) { /* ignore */ }
    }

    const url = wsUrl || getWsUrl();
    setConnectionState(CONNECTION_STATES.CONNECTING);

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        if (!mountedRef.current) { ws.close(); return; }
        setConnectionState(CONNECTION_STATES.CONNECTED);
        backoffRef.current = INITIAL_BACKOFF_MS; // Reset backoff on success
        console.log('[AEGIS WS] Connected to', url);
      };

      ws.onmessage = (event) => {
        if (!mountedRef.current) return;
        handleMessage(event.data);
      };

      ws.onclose = (event) => {
        if (!mountedRef.current) return;
        setConnectionState(CONNECTION_STATES.DISCONNECTED);
        console.log(`[AEGIS WS] Disconnected (code: ${event.code})`);
        scheduleReconnect();
      };

      ws.onerror = (error) => {
        if (!mountedRef.current) return;
        setConnectionState(CONNECTION_STATES.ERROR);
        console.warn('[AEGIS WS] Connection error');
        // onclose will fire after onerror, which handles reconnect
      };

    } catch (e) {
      console.error('[AEGIS WS] Failed to create WebSocket:', e);
      setConnectionState(CONNECTION_STATES.ERROR);
      scheduleReconnect();
    }
  }, [wsUrl, handleMessage]);

  // ──────────────────────────────────────────
  // Reconnect with exponential backoff
  // ──────────────────────────────────────────
  const scheduleReconnect = useCallback(() => {
    if (!mountedRef.current) return;

    const delay = backoffRef.current;
    console.log(`[AEGIS WS] Reconnecting in ${delay}ms...`);

    reconnectTimerRef.current = setTimeout(() => {
      if (!mountedRef.current) return;
      backoffRef.current = Math.min(backoffRef.current * BACKOFF_MULTIPLIER, MAX_BACKOFF_MS);
      connect();
    }, delay);
  }, [connect]);

  // ──────────────────────────────────────────
  // Lifecycle
  // ──────────────────────────────────────────
  useEffect(() => {
    mountedRef.current = true;
    connect();

    return () => {
      mountedRef.current = false;

      // Clear reconnect timer
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }

      // Close WebSocket
      if (wsRef.current) {
        try {
          wsRef.current.close(1000, 'Component unmounted');
        } catch (e) { /* ignore */ }
        wsRef.current = null;
      }
    };
  }, [connect]);

  return {
    connectionState,
    isConnected,
    lastEvent,
    recentEvents,
    systemStatus,
    onEvent,
  };
}
