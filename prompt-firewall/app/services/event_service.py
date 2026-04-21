"""
AEGIS Phase 2 — Event Service

Converts scan pipeline results into structured WebSocket events
and triggers broadcast through the ConnectionManager.

Responsibilities:
  - Build SCAN_COMPLETED event for every scan
  - Build ATTACK_DETECTED event for block/challenge decisions
  - Build SYSTEM_STATUS from readiness checks
  - Ensure matched text is redacted/truncated for safe broadcast
"""

from __future__ import annotations

from app.schemas.scan import ScanRequest, ScanResult, Detection
from app.schemas.events import (
    SystemStatusEvent,
    ScanCompletedEvent,
    AttackDetectedEvent,
    CompactDetection,
    SourceSummary,
)
from app.services.ws_broadcaster import ConnectionManager
from app.services.readiness_service import ReadinessService
from app.core.security import redact_text
from app.core.logging import get_logger

log = get_logger("event_service")

# Severity ranking for determining the top severity
_SEVERITY_RANK = {"critical": 4, "high": 3, "medium": 2, "low": 1}

# Decisions that trigger ATTACK_DETECTED
_ATTACK_DECISIONS = {"block", "challenge"}


class EventService:
    """
    Converts scan results into WebSocket events and broadcasts them.
    
    Usage:
        event_svc = EventService(ws_manager, readiness_service)
        await event_svc.emit_scan_events(request, result)
    """

    def __init__(
        self,
        ws_manager: ConnectionManager,
        readiness_service: ReadinessService,
    ):
        self._ws_manager = ws_manager
        self._readiness = readiness_service

    # ──────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────

    async def emit_scan_events(self, request: ScanRequest, result: ScanResult):
        """
        Called after a scan completes. Emits:
          - Always: SCAN_COMPLETED
          - Conditionally: ATTACK_DETECTED (if block/challenge or high-confidence attacks)
        """
        if self._ws_manager.active_count == 0:
            return  # No clients listening, skip event construction

        source_summary = self._build_source_summary(request, result)

        # Always emit SCAN_COMPLETED
        scan_event = ScanCompletedEvent(
            request_id=result.request_id,
            trace_id=result.trace_id,
            decision=result.decision,
            risk_score=result.risk_score,
            channel_scores=result.channel_scores,
            recommended_action=result.recommended_action,
            detection_count=len(result.detections),
            source_summary=source_summary,
        )
        await self._ws_manager.broadcast(scan_event.model_dump())

        # Conditionally emit ATTACK_DETECTED
        if self._should_emit_attack(result):
            attack_event = self._build_attack_event(request, result, source_summary)
            await self._ws_manager.broadcast(attack_event.model_dump())

        log.info(
            "events_emitted",
            request_id=result.request_id,
            decision=result.decision,
            attack_emitted=self._should_emit_attack(result),
            clients=self._ws_manager.active_count,
        )

    async def build_system_status(self) -> SystemStatusEvent:
        """Build a SYSTEM_STATUS event from current readiness state."""
        is_ready, details = await self._readiness.evaluate_readiness()

        return SystemStatusEvent(
            status="operational" if is_ready else "degraded",
            components=details.get("components", {}),
            summary=self._build_status_summary(is_ready, details),
        )

    # ──────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────

    def _should_emit_attack(self, result: ScanResult) -> bool:
        """Determine whether an ATTACK_DETECTED event should be emitted."""
        if result.decision in _ATTACK_DECISIONS:
            return True
        # Also emit for high-confidence attacks even if decision is sanitize/allow
        if any(d.score >= 0.8 and d.severity in ("critical", "high") for d in result.detections):
            return True
        return False

    def _build_source_summary(self, request: ScanRequest, result: ScanResult) -> SourceSummary:
        """Build a source summary from request channels."""
        # Determine source types and channel count from channel_scores
        channel_ids = list(result.channel_scores.keys()) if result.channel_scores else ["prompt"]
        
        source_types = set()
        source_types.add("user")  # Prompt is always user
        for msg in request.history:
            if msg.role == "user":
                source_types.add("user")
            elif msg.role == "tool":
                source_types.add("tool")
            else:
                source_types.add("system")

        # Primary channel is the one with the highest score
        primary_channel = "prompt"
        if result.channel_scores:
            primary_channel = max(result.channel_scores, key=result.channel_scores.get)

        return SourceSummary(
            channels_scanned=max(len(channel_ids), 1),
            primary_channel=primary_channel,
            source_types=sorted(source_types),
            has_untrusted=True,  # Prompt is always untrusted
        )

    def _build_attack_event(
        self,
        request: ScanRequest,
        result: ScanResult,
        source_summary: SourceSummary,
    ) -> AttackDetectedEvent:
        """Build an ATTACK_DETECTED event with safe/truncated detections."""
        
        # Determine top severity
        top_severity = "low"
        for d in result.detections:
            if _SEVERITY_RANK.get(d.severity, 0) > _SEVERITY_RANK.get(top_severity, 0):
                top_severity = d.severity

        # Unique attack types
        attack_types = list(dict.fromkeys(d.attack_type for d in result.detections))

        # Top detections (max 5, safe excerpts)
        sorted_detections = sorted(
            result.detections,
            key=lambda d: d.score,
            reverse=True,
        )[:5]

        top_detections = [
            CompactDetection(
                scanner=d.scanner,
                attack_type=d.attack_type,
                severity=d.severity,
                score=d.score,
                explanation=d.explanation,
                matched_excerpt=redact_text(d.matched_text, max_len=80),
            )
            for d in sorted_detections
        ]

        # Operator summary
        operator_summary = (
            f"{top_severity.upper()} {attack_types[0] if attack_types else 'unknown'} "
            f"attack detected. {len(result.detections)} attack vector(s) identified. "
            f"Decision: {result.decision.upper()}."
        )

        # Primary channel
        primary_channel = source_summary.primary_channel

        return AttackDetectedEvent(
            request_id=result.request_id,
            trace_id=result.trace_id,
            decision=result.decision,
            risk_score=result.risk_score,
            severity=top_severity,
            attack_types=attack_types,
            recommended_action=result.recommended_action,
            channel_scores=result.channel_scores,
            primary_channel=primary_channel,
            source_summary=source_summary,
            operator_summary=operator_summary,
            top_detections=top_detections,
        )

    def _build_status_summary(self, is_ready: bool, details: dict) -> str:
        """Build a human-readable status summary."""
        components = details.get("components", {})
        total = len(components)
        ready_count = sum(1 for c in components.values() if c.get("is_ready", False))

        if is_ready:
            return f"All {total} components operational."
        else:
            failed = total - ready_count
            return f"{ready_count}/{total} components operational. {failed} component(s) degraded."

    async def emit_ingest_events(self, source_kind: str, source_id: str, chunk_id: str, detections: list[Detection]):
        if self._ws_manager.active_count == 0:
            return
            
        top_severity = "low"
        attack_types = []
        for d in detections:
            if _SEVERITY_RANK.get(d.severity, 0) > _SEVERITY_RANK.get(top_severity, 0):
                top_severity = d.severity
            if d.attack_type not in attack_types:
                attack_types.append(d.attack_type)
                
        sorted_detections = sorted(detections, key=lambda d: d.score, reverse=True)[:5]
        top_detections = [
            CompactDetection(
                scanner=d.scanner,
                attack_type=d.attack_type,
                severity=d.severity,
                score=d.score,
                explanation=d.explanation,
                matched_excerpt=redact_text(d.matched_text, max_len=80),
            )
            for d in sorted_detections
        ]
        
        event = AttackDetectedEvent(
            request_id=f"ingest_{source_id}",
            trace_id=f"trace_{source_id}",
            decision="block",
            risk_score=max((d.score for d in detections), default=0.0),
            severity=top_severity,
            attack_types=attack_types,
            recommended_action="quarantine",
            channel_scores={chunk_id: max((d.score for d in detections), default=0.0)},
            primary_channel=chunk_id,
            source_summary=SourceSummary(
                channels_scanned=1,
                primary_channel=chunk_id,
                source_types=[source_kind],
                has_untrusted=True
            ),
            operator_summary=f"Malicious {source_kind} chunk quarantined.",
            top_detections=top_detections,
            source_kind=source_kind,
            source_id=source_id,
            chunk_id=chunk_id,
            quarantined=True
        )
        
        await self._ws_manager.broadcast(event.model_dump())

    async def emit_output_blocked(self, request_id: str, trace_id: str, detections: list[Detection], action: str, provider: str, model: str, safe_excerpt: str):
        if self._ws_manager.active_count == 0:
            return
            
        top_severity = "low"
        attack_types = []
        for d in detections:
            if _SEVERITY_RANK.get(d.severity, 0) > _SEVERITY_RANK.get(top_severity, 0):
                top_severity = d.severity
            if d.attack_type not in attack_types:
                attack_types.append(d.attack_type)
                
        sorted_detections = sorted(detections, key=lambda d: d.score, reverse=True)[:5]
        top_detections = [
            CompactDetection(
                scanner=d.scanner,
                attack_type=d.attack_type,
                severity=d.severity,
                score=d.score,
                explanation=d.explanation,
                matched_excerpt=redact_text(d.matched_text, max_len=80),
            )
            for d in sorted_detections
        ]
        
        event = AttackDetectedEvent(
            request_id=request_id,
            trace_id=trace_id,
            decision="block",
            risk_score=max((d.score for d in detections), default=0.0),
            severity=top_severity,
            attack_types=attack_types,
            recommended_action=action,
            channel_scores={"output": max((d.score for d in detections), default=0.0)},
            primary_channel="output",
            source_summary=SourceSummary(
                channels_scanned=1,
                primary_channel="output",
                source_types=["output_content"],
                has_untrusted=True
            ),
            operator_summary=f"Output from {provider}/{model} blocked/redacted ({action}).",
            top_detections=top_detections,
            source_kind="output"
        )
        await self._ws_manager.broadcast(event.model_dump())
