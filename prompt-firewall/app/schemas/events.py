"""
AEGIS Phase 2 — WebSocket Event Schemas

Stable, typed event payloads for real-time broadcasting.
All events are JSON-serializable and safe for frontend consumption.

Event types:
  - SYSTEM_STATUS: backend health snapshot on connect / heartbeat
  - SCAN_COMPLETED: emitted after every completed scan
  - ATTACK_DETECTED: emitted when decision is block/challenge or high-confidence attack
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from pydantic import BaseModel, Field


# ──────────────────────────────────────────────
# Source Summary (future-proof for Phase 3)
# ──────────────────────────────────────────────

class SourceSummary(BaseModel):
    """
    Describes which input channels were involved in a scan.
    Designed to support Phase 3 multi-channel ingestion
    (document_chunk, url_content, tool_output, etc.)
    without schema rewrites.
    """
    channels_scanned: int = Field(description="Total channels analyzed")
    primary_channel: str = Field(description="The channel that triggered the highest signal")
    source_types: list[str] = Field(default_factory=list, description="e.g. ['user', 'system']")
    has_untrusted: bool = Field(default=True, description="Whether any untrusted channel was present")


# ──────────────────────────────────────────────
# Base Event
# ──────────────────────────────────────────────

class BaseEvent(BaseModel):
    """Base for all WebSocket events."""
    type: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ──────────────────────────────────────────────
# SYSTEM_STATUS
# ──────────────────────────────────────────────

class SystemStatusEvent(BaseEvent):
    """
    Backend health snapshot. Sent on WebSocket connect and optionally
    on periodic heartbeat.
    """
    type: str = "SYSTEM_STATUS"
    service: str = "aegis-prompt-firewall"
    version: str = "0.2.0"
    status: str = Field(description="'operational', 'degraded', or 'unavailable'")
    components: dict[str, Any] = Field(default_factory=dict)
    summary: str = ""


# ──────────────────────────────────────────────
# SCAN_COMPLETED
# ──────────────────────────────────────────────

class ScanCompletedEvent(BaseEvent):
    """
    Generic scan completion notification.
    Emitted for EVERY completed scan regardless of decision.
    """
    type: str = "SCAN_COMPLETED"
    request_id: str
    trace_id: str
    decision: str
    risk_score: float
    channel_scores: dict[str, float] = Field(default_factory=dict)
    recommended_action: str
    detection_count: int = 0
    source_summary: SourceSummary


# ──────────────────────────────────────────────
# Compact Detection (safe for WS broadcast)
# ──────────────────────────────────────────────

class CompactDetection(BaseModel):
    """
    A truncated, safe-for-broadcast detection summary.
    No raw matched text longer than 80 chars.
    """
    scanner: str
    attack_type: str
    severity: str
    score: float
    explanation: str
    matched_excerpt: str = Field(default="", description="Truncated/redacted matched text")


# ──────────────────────────────────────────────
# ATTACK_DETECTED
# ──────────────────────────────────────────────

class AttackDetectedEvent(BaseEvent):
    """
    High-signal attack detection event.
    Only emitted when decision is block/challenge
    or high-confidence attacks are detected.
    """
    type: str = "ATTACK_DETECTED"
    request_id: str
    trace_id: str
    decision: str
    risk_score: float
    severity: str
    attack_types: list[str] = Field(default_factory=list)
    recommended_action: str
    channel_scores: dict[str, float] = Field(default_factory=dict)
    primary_channel: str = "prompt"
    source_summary: SourceSummary
    operator_summary: str = ""
    top_detections: list[CompactDetection] = Field(default_factory=list)
    source_kind: Optional[str] = None
    source_id: Optional[str] = None
    chunk_id: Optional[str] = None
    quarantined: Optional[bool] = None
