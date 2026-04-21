import { motion, AnimatePresence } from 'framer-motion';

const LAYER_ICONS = {
  ingress_filter: '🚪',
  intent_analyzer: '🧠',
  execution_sandbox: '🔧',
  memory_guardian: '💾',
  egress_filter: '📤',
};

const LAYER_NAMES = {
  ingress_filter: 'Ingress Filter',
  intent_analyzer: 'Intent Analyzer',
  execution_sandbox: 'Execution Sandbox',
  memory_guardian: 'Memory Guardian',
  egress_filter: 'Egress Filter',
};

const STATUS_STYLES = {
  intercepted: { bg: 'rgba(255,45,85,0.1)', color: 'var(--threat-critical)', label: 'INTERCEPTED' },
  blocked: { bg: 'rgba(255,45,85,0.1)', color: 'var(--threat-critical)', label: 'BLOCKED' },
  quarantined: { bg: 'rgba(255,159,10,0.1)', color: 'var(--threat-medium)', label: 'QUARANTINED' },
  filtered: { bg: 'rgba(255,107,53,0.1)', color: 'var(--threat-high)', label: 'FILTERED' },
  alert: { bg: 'rgba(255,159,10,0.1)', color: 'var(--threat-medium)', label: 'ALERT' },
  passed: { bg: 'rgba(48,209,88,0.05)', color: 'var(--threat-safe)', label: 'PASSED' },
  nominal: { bg: 'rgba(48,209,88,0.02)', color: 'var(--text-tertiary)', label: 'NOMINAL' },
};

const layerVariants = {
  hidden: { opacity: 0, x: -15 },
  visible: (i) => ({
    opacity: 1,
    x: 0,
    transition: { delay: i * 0.1, type: 'spring', stiffness: 200, damping: 20 },
  }),
};

export default function AttackReport({ attack }) {
  if (!attack) {
    return (
      <div style={{
        padding: 'var(--space-xl)',
        textAlign: 'center',
        color: 'var(--text-tertiary)',
        fontSize: 'var(--text-sm)',
      }}>
        <motion.div
          animate={{ y: [0, -4, 0] }}
          transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
          style={{ fontSize: '28px', marginBottom: 'var(--space-sm)', opacity: 0.5 }}
        >
          📋
        </motion.div>
        <div>Awaiting analysis data</div>
        <div style={{ fontSize: 'var(--text-xs)', marginTop: 'var(--space-xs)' }}>
          Submit a prompt to see forensic report
        </div>
      </div>
    );
  }

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={attack.id}
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -12 }}
        transition={{ type: 'spring', stiffness: 150, damping: 20 }}
        style={{ padding: 'var(--space-sm) var(--space-md)', display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}
      >
        {/* Verdict */}
        <motion.div
          initial={{ scale: 0.95 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', stiffness: 200, damping: 15 }}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-sm)',
            padding: '7px var(--space-md)',
            borderRadius: 'var(--radius-md)',
            background: attack.isMalicious ? 'rgba(255,45,85,0.06)' : 'rgba(48,209,88,0.06)',
            border: `1px solid ${attack.isMalicious ? 'rgba(255,45,85,0.15)' : 'rgba(48,209,88,0.15)'}`,
          }}
        >
          <motion.span
            initial={{ scale: 0, rotate: -90 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ type: 'spring', stiffness: 250, damping: 12 }}
            style={{ fontSize: '16px' }}
          >
            {attack.isMalicious ? '🚨' : '✅'}
          </motion.span>
          <div style={{ flex: 1 }}>
            <div style={{
              fontFamily: 'var(--font-display)',
              fontWeight: 700,
              fontSize: 'var(--text-sm)',
              color: attack.isMalicious ? 'var(--threat-critical)' : 'var(--threat-safe)',
            }}>
              {attack.isMalicious ? 'THREAT INTERCEPTED' : 'PROMPT VERIFIED'}
            </div>
            <div style={{ fontSize: '9px', color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)' }}>
              Risk: {attack.riskScore}% │ Mode: {attack.defenseMode?.toUpperCase()}
            </div>
          </div>
        </motion.div>

        {/* Intent Analysis */}
        {attack.isMalicious && attack.intentAnalysis && (
          <div>
            <div className="section-label" style={{ marginBottom: '6px' }}>Intent Analysis</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              {[
                { border: 'var(--threat-critical)', bg: 'rgba(255,45,85,0.04)', label: 'Adversarial Intent', text: attack.intentAnalysis.adversarial, color: 'var(--threat-critical)' },
                { border: 'var(--threat-safe)', bg: 'rgba(48,209,88,0.03)', label: 'Legitimate Intent', text: attack.intentAnalysis.legitimate, color: 'var(--threat-safe)' },
                { border: 'var(--accent-cyan)', bg: 'rgba(0,240,255,0.03)', label: 'AEGIS Action', text: attack.intentAnalysis.action, color: 'var(--accent-cyan)' },
              ].map((item, i) => (
                <motion.div
                  key={item.label}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 + i * 0.08, type: 'spring', stiffness: 200, damping: 20 }}
                  style={{
                    padding: '5px 8px',
                    borderRadius: 'var(--radius-sm)',
                    borderLeft: `3px solid ${item.border}`,
                    background: item.bg,
                    fontSize: '10px',
                  }}
                >
                  <span style={{ color: 'var(--text-tertiary)', fontSize: '8px', textTransform: 'uppercase', letterSpacing: '0.08em' }}>{item.label}</span>
                  <div style={{ color: item.color, marginTop: '2px' }}>{item.text}</div>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Detected Threats */}
        {attack.isMalicious && attack.attacks.length > 0 && (
          <div>
            <div className="section-label" style={{ marginBottom: '6px' }}>Threat Vectors</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
              {attack.attacks.map((a, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -12 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.08, type: 'spring', stiffness: 200, damping: 20 }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '4px 8px',
                    borderRadius: 'var(--radius-sm)',
                    background: 'rgba(255,255,255,0.02)',
                    border: '1px solid var(--border-subtle)',
                  }}
                >
                  <div>
                    <div style={{ fontSize: '11px', fontWeight: 500 }}>{a.name}</div>
                    <div style={{ fontSize: '9px', color: 'var(--text-tertiary)', fontFamily: 'var(--font-mono)' }}>{a.type}</div>
                  </div>
                  <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
                    <motion.span
                      className={`badge badge--${a.severity === 'critical' ? 'critical' : a.severity === 'high' ? 'warning' : 'info'}`}
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ type: 'spring', stiffness: 400, damping: 15, delay: 0.2 + i * 0.08 }}
                    >
                      {a.severity}
                    </motion.span>
                    <span style={{ fontSize: '9px', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
                      {Math.round(a.confidence * 100)}%
                    </span>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Security Pipeline Status — sequential light-up */}
        <div>
          <div className="section-label" style={{ marginBottom: '6px' }}>Security Pipeline</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
            {Object.entries(attack.layers).map(([key, layer], i) => {
              const status = STATUS_STYLES[layer.status] || STATUS_STYLES.nominal;
              return (
                <motion.div
                  key={key}
                  custom={i}
                  variants={layerVariants}
                  initial="hidden"
                  animate="visible"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    padding: '4px 8px',
                    borderRadius: 'var(--radius-sm)',
                    background: status.bg,
                    borderLeft: `3px solid ${status.color}`,
                  }}
                >
                  <span style={{ fontSize: '12px' }}>{LAYER_ICONS[key]}</span>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: '10px', fontWeight: 600, fontFamily: 'var(--font-display)' }}>
                      {LAYER_NAMES[key]}
                    </div>
                  </div>
                  <motion.span
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.3 + i * 0.1 }}
                    style={{
                      fontSize: '8px',
                      fontFamily: 'var(--font-mono)',
                      fontWeight: 700,
                      color: status.color,
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                    }}
                  >
                    {status.label}
                  </motion.span>
                </motion.div>
              );
            })}
          </div>
        </div>

        {/* Interception Path */}
        {attack.interceptionPoint && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            style={{
              padding: '6px 10px',
              borderRadius: 'var(--radius-md)',
              background: 'rgba(0,240,255,0.03)',
              border: '1px solid rgba(0,240,255,0.1)',
              fontSize: '9px',
              fontFamily: 'var(--font-mono)',
            }}
          >
            <span style={{ color: 'var(--text-tertiary)' }}>Intercepted → </span>
            <span style={{ color: 'var(--mode-accent)', fontWeight: 600 }}>
              {attack.interceptionPoint.replace(/_/g, ' ').toUpperCase()}
            </span>
            <span style={{ color: 'var(--text-tertiary)' }}> │ </span>
            <span style={{ color: 'var(--text-secondary)' }}>
              {attack.attackPath.join(' → ')}
            </span>
          </motion.div>
        )}
      </motion.div>
    </AnimatePresence>
  );
}
