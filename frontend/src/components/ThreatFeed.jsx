import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect } from 'react';

const SIMULATED_THREATS = [
  { type: 'prompt_injection', source: '192.168.1.42', severity: 'critical', msg: 'Token injection pattern detected in API request' },
  { type: 'jailbreak', source: '10.0.0.15', severity: 'high', msg: 'DAN persona manipulation attempt blocked' },
  { type: 'memory_poisoning', source: '172.16.0.88', severity: 'critical', msg: 'RAG document contained embedded injection payload' },
  { type: 'privilege_escalation', source: '192.168.2.7', severity: 'high', msg: 'Admin role assumption detected in tool call chain' },
  { type: 'data_exfiltration', source: '10.0.1.33', severity: 'medium', msg: 'Output contained potential credential leak pattern' },
  { type: 'obfuscation', source: '192.168.0.99', severity: 'medium', msg: 'Base64-encoded payload detected in user prompt' },
];

export default function ThreatFeed({ events }) {
  const [simulatedEvents, setSimulatedEvents] = useState([]);

  // Add simulated background events
  useEffect(() => {
    const interval = setInterval(() => {
      if (Math.random() > 0.6) {
        const threat = SIMULATED_THREATS[Math.floor(Math.random() * SIMULATED_THREATS.length)];
        setSimulatedEvents(prev => [{
          id: `sim-${Date.now()}`,
          timestamp: new Date(),
          simulated: true,
          ...threat,
        }, ...prev].slice(0, 20));
      }
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const allEvents = [
    ...events.map(e => ({
      id: `real-${e.id}`,
      timestamp: e.timestamp,
      simulated: false,
      type: e.attacks?.[0]?.type || 'scan',
      severity: e.severity,
      source: 'console',
      msg: e.isMalicious
        ? `Blocked: ${e.attacks[0]?.name} (Risk: ${e.riskScore}%)`
        : `Clean prompt analyzed (Risk: ${e.riskScore}%)`,
    })),
    ...simulatedEvents,
  ].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)).slice(0, 15);

  const severityColors = {
    critical: 'var(--threat-critical)',
    high: 'var(--threat-high)',
    medium: 'var(--threat-medium)',
    low: 'var(--threat-low)',
    safe: 'var(--threat-safe)',
  };

  return (
    <div className="glass-panel" style={{
      display: 'flex',
      flexDirection: 'column',
      padding: 0,
      overflow: 'hidden',
    }}>
      <div style={{
        padding: 'var(--space-sm) var(--space-md)',
        borderBottom: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexShrink: 0,
      }}>
        <div className="section-label" style={{ margin: 0 }}>
          Threat Intelligence Feed
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <div className="pulse-dot pulse-dot--danger" style={{ width: '6px', height: '6px' }} />
          <span style={{
            fontSize: '9px',
            fontFamily: 'var(--font-mono)',
            color: 'var(--text-tertiary)',
            textTransform: 'uppercase',
          }}>
            Live
          </span>
        </div>
      </div>

      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: 'var(--space-xs)',
        minHeight: 0,
      }}>
        <AnimatePresence>
          {allEvents.map(event => (
            <motion.div
              key={event.id}
              initial={{ opacity: 0, x: -10, height: 0 }}
              animate={{ opacity: 1, x: 0, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.2 }}
              style={{
                display: 'flex',
                gap: 'var(--space-xs)',
                padding: '4px var(--space-sm)',
                borderRadius: 'var(--radius-sm)',
                marginBottom: '2px',
                fontSize: '10px',
                fontFamily: 'var(--font-mono)',
                borderLeft: `2px solid ${severityColors[event.severity] || 'var(--text-tertiary)'}`,
                background: event.simulated ? 'transparent' : 'rgba(255,255,255,0.02)',
                opacity: event.simulated ? 0.6 : 1,
              }}
            >
              <span style={{ color: 'var(--text-tertiary)', whiteSpace: 'nowrap', flexShrink: 0 }}>
                {new Date(event.timestamp).toLocaleTimeString('en-US', {
                  hour12: false,
                  hour: '2-digit',
                  minute: '2-digit',
                  second: '2-digit',
                })}
              </span>
              <span style={{
                color: severityColors[event.severity] || 'var(--text-secondary)',
                flexShrink: 0,
                width: '50px',
                textTransform: 'uppercase',
                fontWeight: 600,
                fontSize: '9px',
              }}>
                {event.severity}
              </span>
              <span style={{
                color: 'var(--text-secondary)',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}>
                {event.msg}
              </span>
            </motion.div>
          ))}
        </AnimatePresence>

        {allEvents.length === 0 && (
          <div style={{
            textAlign: 'center',
            color: 'var(--text-tertiary)',
            fontSize: 'var(--text-xs)',
            padding: 'var(--space-lg)',
          }}>
            Monitoring for threats...
          </div>
        )}
      </div>
    </div>
  );
}
