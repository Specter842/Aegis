import { motion, AnimatePresence } from 'framer-motion';
import { useEffect, useState } from 'react';

const SIMULATED_ACTIONS = [
  { icon: '🔍', message: 'Scanning ingress pipeline — no threats detected', type: 'info' },
  { icon: '📡', message: 'Threat signature database synchronized (1,247 patterns)', type: 'info' },
  { icon: '🧠', message: 'Intent analyzer calibration complete — semantic model loaded', type: 'info' },
  { icon: '💾', message: 'Memory guardian scan — vector store integrity verified', type: 'info' },
  { icon: '🔧', message: 'Execution sandbox health check — all tool isolations active', type: 'info' },
  { icon: '📊', message: 'Trust decay function recalibrated (λ=0.15)', type: 'info' },
];

const actionVariants = {
  initial: { opacity: 0, x: -20, height: 0, marginBottom: 0 },
  animate: {
    opacity: 1,
    x: 0,
    height: 'auto',
    marginBottom: 2,
    transition: { type: 'spring', stiffness: 200, damping: 20, mass: 0.8 },
  },
  exit: {
    opacity: 0,
    x: 15,
    height: 0,
    marginBottom: 0,
    transition: { duration: 0.2, ease: 'easeIn' },
  },
};

export default function AutonomousActions({ actions, isWsConnected }) {
  const [simulatedActions, setSimulatedActions] = useState([]);

  // Background simulation — ONLY when WebSocket is disconnected and no real actions exist
  useEffect(() => {
    if (isWsConnected) {
      setSimulatedActions([]);
      return;
    }
    const interval = setInterval(() => {
      if (Math.random() > 0.65 && actions.length === 0) {
        const sim = SIMULATED_ACTIONS[Math.floor(Math.random() * SIMULATED_ACTIONS.length)];
        setSimulatedActions(prev => [{
          id: `sim-${Date.now()}`,
          timestamp: new Date(),
          simulated: true,
          ...sim,
        }, ...prev].slice(0, 10));
      }
    }, 4000);
    return () => clearInterval(interval);
  }, [actions.length, isWsConnected]);

  const allActions = [
    ...actions.map(a => ({ ...a, simulated: false })),
    ...simulatedActions,
  ].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)).slice(0, 20);

  const typeStyles = {
    info: { borderColor: 'rgba(0, 240, 255, 0.12)', textColor: 'var(--text-secondary)', glowColor: 'rgba(0, 240, 255, 0.05)' },
    warning: { borderColor: 'rgba(255, 159, 10, 0.18)', textColor: 'var(--threat-medium)', glowColor: 'rgba(255, 159, 10, 0.04)' },
    critical: { borderColor: 'rgba(255, 45, 85, 0.2)', textColor: 'var(--threat-critical)', glowColor: 'rgba(255, 45, 85, 0.04)' },
    recovery: { borderColor: 'rgba(48, 209, 88, 0.18)', textColor: 'var(--threat-safe)', glowColor: 'rgba(48, 209, 88, 0.04)' },
  };

  return (
    <div className="glass-panel" style={{
      display: 'flex',
      flexDirection: 'column',
      padding: 0,
      overflow: 'hidden',
    }}>
      <div style={{
        padding: '7px var(--space-md)',
        borderBottom: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexShrink: 0,
      }}>
        <div className="section-label" style={{ margin: 0 }}>
          Autonomous Actions
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <div className="pulse-dot" style={{ width: '5px', height: '5px' }} />
          <span style={{
            fontSize: '8px',
            fontFamily: 'var(--font-mono)',
            color: isWsConnected ? 'var(--threat-safe)' : 'var(--text-tertiary)',
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
          }}>
            {isWsConnected ? 'AEGIS Live' : 'AEGIS Offline'}
          </span>
        </div>
      </div>

      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: 'var(--space-xs)',
        minHeight: 0,
      }}>
        <AnimatePresence initial={false}>
          {allActions.map((action, index) => {
            const style = typeStyles[action.type] || typeStyles.info;
            const isNew = !action.simulated && index === 0;
            return (
              <motion.div
                key={action.id}
                variants={actionVariants}
                initial="initial"
                animate="animate"
                exit="exit"
                layout
                style={{
                  display: 'flex',
                  gap: '6px',
                  padding: '5px var(--space-sm)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '10px',
                  fontFamily: 'var(--font-mono)',
                  borderLeft: `2px solid ${style.borderColor}`,
                  opacity: action.simulated ? 0.4 : 1,
                  lineHeight: 1.4,
                  background: isNew ? style.glowColor : 'transparent',
                  transition: 'background 1s ease',
                }}
              >
                <motion.span
                  style={{ flexShrink: 0, fontSize: '11px' }}
                  initial={!action.simulated ? { scale: 1.4 } : false}
                  animate={{ scale: 1 }}
                  transition={{ type: 'spring', stiffness: 300, damping: 12 }}
                >
                  {action.icon}
                </motion.span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <span style={{ color: style.textColor }}>
                    {action.message}
                  </span>
                  <div style={{
                    fontSize: '8px',
                    color: 'var(--text-tertiary)',
                    marginTop: '1px',
                  }}>
                    {new Date(action.timestamp).toLocaleTimeString('en-US', {
                      hour12: false,
                      hour: '2-digit',
                      minute: '2-digit',
                      second: '2-digit',
                    })}
                  </div>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>

        {allActions.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            style={{
              textAlign: 'center',
              color: 'var(--text-tertiary)',
              fontSize: 'var(--text-xs)',
              padding: 'var(--space-lg)',
            }}
          >
            <motion.span
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              Autonomous defense engine initializing...
            </motion.span>
          </motion.div>
        )}
      </div>
    </div>
  );
}
