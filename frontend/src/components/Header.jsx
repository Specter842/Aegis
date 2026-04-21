import { motion } from 'framer-motion';

const PIPELINE_LAYERS = [
  { key: 'ingress', label: 'Ingress' },
  { key: 'intent', label: 'Intent' },
  { key: 'sandbox', label: 'Sandbox' },
  { key: 'memory', label: 'Memory' },
  { key: 'egress', label: 'Egress' },
];

const containerVariants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.06, delayChildren: 0.2 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: -8 },
  visible: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 200, damping: 20 } },
};

export default function Header({ trustScore, defenseMode, totalBlocked, totalAnalyzed, pipelineStatus, onReset, wsConnectionState }) {
  const wsConfig = {
    connected: { label: 'LIVE', color: 'var(--threat-safe)', dotClass: '' },
    connecting: { label: 'CONNECTING', color: 'var(--threat-medium)', dotClass: 'pulse-dot--warning' },
    disconnected: { label: 'OFFLINE', color: 'var(--threat-critical)', dotClass: 'pulse-dot--danger' },
    error: { label: 'ERROR', color: 'var(--threat-critical)', dotClass: 'pulse-dot--danger' },
  };
  const ws = wsConfig[wsConnectionState] || wsConfig.disconnected;
  const modeConfig = {
    normal: { label: 'NORMAL', dotClass: '' },
    elevated: { label: 'ELEVATED', dotClass: 'pulse-dot--warning' },
    lockdown: { label: 'LOCKDOWN', dotClass: 'pulse-dot--danger' },
  };

  const mode = modeConfig[defenseMode] || modeConfig.normal;

  return (
    <motion.header
      className="dashboard__header glass-panel glass-panel--no-hover"
      initial={{ opacity: 0, y: -30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: 'spring', stiffness: 120, damping: 20 }}
    >
      <div className="logo">
        <motion.div
          className="logo__icon"
          whileHover={{ scale: 1.1, rotate: 5 }}
          whileTap={{ scale: 0.95 }}
          transition={{ type: 'spring', stiffness: 400, damping: 15 }}
        >
          🛡️
        </motion.div>
        <div>
          <div className="logo__text">AEGIS</div>
          <div className="logo__tagline">Autonomous Security Kernel</div>
        </div>
      </div>

      <motion.div
        className="status-bar"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Pipeline Status Dots */}
        <motion.div className="pipeline-dots" title="Security Pipeline Status" variants={itemVariants}>
          {PIPELINE_LAYERS.map((layer, i) => {
            const status = pipelineStatus[layer.key] || 'nominal';
            return (
              <motion.div
                key={layer.key}
                className={`pipeline-dot pipeline-dot--${status}`}
                title={`${layer.label}: ${status.toUpperCase()}`}
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 300, damping: 15, delay: 0.3 + i * 0.08 }}
              />
            );
          })}
        </motion.div>

        {/* WebSocket Connection Status */}
        <motion.div
          className={`defense-badge defense-badge--${wsConnectionState === 'connected' ? 'normal' : 'lockdown'}`}
          variants={itemVariants}
          title={`WebSocket: ${ws.label}`}
          style={{ gap: '4px', padding: '3px 8px' }}
        >
          <div className={`pulse-dot ${ws.dotClass}`} style={{ width: '5px', height: '5px' }} />
          <span style={{ fontSize: '8px', fontFamily: 'var(--font-mono)', color: ws.color, letterSpacing: '0.08em' }}>
            {ws.label}
          </span>
        </motion.div>

        <motion.div className="status-item" variants={itemVariants}>
          <span>Scanned</span>
          <motion.span
            className="status-item__value mono"
            key={totalAnalyzed}
            initial={{ scale: 1.3, color: 'var(--accent-cyan)' }}
            animate={{ scale: 1, color: 'var(--text-primary)' }}
            transition={{ duration: 0.4 }}
          >
            {totalAnalyzed}
          </motion.span>
        </motion.div>

        <motion.div className="status-item" variants={itemVariants}>
          <span>Blocked</span>
          <motion.span
            className="status-item__value mono"
            key={totalBlocked}
            initial={{ scale: 1.4 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 300, damping: 10 }}
            style={{ color: totalBlocked > 0 ? 'var(--threat-critical)' : 'var(--text-tertiary)' }}
          >
            {totalBlocked}
          </motion.span>
        </motion.div>

        <motion.div className="status-item" variants={itemVariants}>
          <span>Trust</span>
          <motion.span
            className="status-item__value mono"
            key={trustScore}
            animate={{
              color: trustScore > 70 ? 'var(--threat-safe)' : trustScore > 30 ? 'var(--threat-medium)' : 'var(--threat-critical)',
            }}
            transition={{ duration: 0.6 }}
          >
            {trustScore}%
          </motion.span>
        </motion.div>

        {/* Defense Mode Badge */}
        <motion.div
          className={`defense-badge defense-badge--${defenseMode}`}
          variants={itemVariants}
          layout
          transition={{ type: 'spring', stiffness: 200, damping: 25 }}
        >
          <div className={`pulse-dot ${mode.dotClass}`} style={{ width: '6px', height: '6px' }} />
          <motion.span
            key={mode.label}
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            {mode.label}
          </motion.span>
        </motion.div>

        <motion.button
          className="btn btn--ghost"
          onClick={onReset}
          style={{ padding: '5px 12px', fontSize: '9px' }}
          whileHover={{ scale: 1.05, borderColor: 'var(--mode-accent)' }}
          whileTap={{ scale: 0.92 }}
          variants={itemVariants}
        >
          Reset
        </motion.button>
      </motion.div>
    </motion.header>
  );
}
