import { motion, AnimatePresence } from 'framer-motion';

const containerVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.05, delayChildren: 0.1 } },
};

const itemVariants = {
  hidden: { opacity: 0, scale: 0.9, y: 8 },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: { type: 'spring', stiffness: 200, damping: 18 },
  },
};

export default function PermissionMatrix({ permissions, trustScore, defenseMode }) {
  return (
    <motion.div
      className="glass-panel"
      style={{ padding: 'var(--space-md)' }}
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ type: 'spring', stiffness: 120, damping: 20, delay: 0.1 }}
    >
      <div className="section-label">Permission Gates</div>
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '5px',
        }}
      >
        {permissions.map((tool) => (
          <motion.div
            key={tool.id}
            variants={itemVariants}
            whileHover={{
              scale: 1.03,
              borderColor: tool.granted ? 'rgba(48, 209, 88, 0.25)' : 'rgba(255, 45, 85, 0.3)',
              transition: { duration: 0.2 },
            }}
            whileTap={{ scale: 0.97 }}
            animate={{
              opacity: tool.granted ? 1 : 0.35,
            }}
            transition={{ duration: 0.4 }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 8px',
              borderRadius: 'var(--radius-sm)',
              background: tool.granted
                ? 'rgba(48, 209, 88, 0.04)'
                : defenseMode === 'lockdown'
                  ? 'rgba(255, 45, 85, 0.06)'
                  : 'rgba(255, 45, 85, 0.03)',
              border: `1px solid ${tool.granted
                ? 'rgba(48, 209, 88, 0.1)'
                : defenseMode === 'lockdown'
                  ? 'rgba(255, 45, 85, 0.15)'
                  : 'rgba(255, 45, 85, 0.08)'}`,
              position: 'relative',
              overflow: 'hidden',
              cursor: 'default',
            }}
          >
            {!tool.granted && (
              <div style={{
                position: 'absolute',
                top: 0, left: 0, right: 0, bottom: 0,
                background: 'repeating-linear-gradient(45deg, transparent, transparent 3px, rgba(255,45,85,0.02) 3px, rgba(255,45,85,0.02) 6px)',
                pointerEvents: 'none',
              }} />
            )}

            <span style={{ fontSize: '13px' }}>{tool.icon}</span>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{
                fontSize: '10px',
                fontWeight: 600,
                fontFamily: 'var(--font-display)',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                color: tool.granted ? 'var(--text-primary)' : 'var(--text-tertiary)',
              }}>
                {tool.name}
              </div>
              <div style={{
                fontSize: '8px',
                fontFamily: 'var(--font-mono)',
                color: 'var(--text-tertiary)',
              }}>
                ≥{tool.minTrust}%
              </div>
            </div>
            <AnimatePresence mode="wait">
              <motion.span
                key={tool.granted ? 'open' : 'locked'}
                initial={{ rotateY: 90, opacity: 0 }}
                animate={{ rotateY: 0, opacity: tool.granted ? 0.4 : 0.8 }}
                exit={{ rotateY: -90, opacity: 0 }}
                transition={{ duration: 0.3 }}
                style={{ fontSize: '10px', display: 'inline-block' }}
              >
                {tool.granted ? '🔓' : '🔒'}
              </motion.span>
            </AnimatePresence>
          </motion.div>
        ))}
      </motion.div>

      <div style={{
        marginTop: 'var(--space-sm)',
        display: 'flex',
        justifyContent: 'space-between',
        fontSize: '8px',
        fontFamily: 'var(--font-mono)',
        color: 'var(--text-tertiary)',
        marginBottom: '3px',
      }}>
        <span>Quarantine</span>
        <span>Full Access</span>
      </div>
      <div style={{
        width: '100%', height: '4px', borderRadius: '2px',
        background: 'var(--bg-primary)', position: 'relative', overflow: 'hidden',
      }}>
        <motion.div
          animate={{ width: `${trustScore}%` }}
          transition={{ type: 'spring', stiffness: 80, damping: 20 }}
          style={{
            height: '100%', borderRadius: '2px',
            background: trustScore > 70
              ? 'linear-gradient(90deg, var(--threat-safe), var(--accent-green))'
              : trustScore > 40
                ? 'linear-gradient(90deg, var(--threat-medium), var(--threat-low))'
                : 'linear-gradient(90deg, var(--threat-critical), var(--threat-high))',
            boxShadow: `0 0 8px ${trustScore > 70 ? 'var(--threat-safe)' : trustScore > 40 ? 'var(--threat-medium)' : 'var(--threat-critical)'}`,
          }}
        />
      </div>
    </motion.div>
  );
}
