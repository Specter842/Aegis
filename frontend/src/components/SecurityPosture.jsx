import { motion } from 'framer-motion';
import { useState, useEffect }from 'react';

export default function SecurityPosture({ trustScore, defenseMode, totalBlocked, totalAnalyzed, pipelineStatus, getSessionDuration }) {
  const [duration, setDuration] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setDuration(getSessionDuration());
    }, 1000);
    return () => clearInterval(interval);
  }, [getSessionDuration]);

  const formatDuration = (s) => {
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return `${m.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`;
  };

  const modeConfig = {
    normal: { label: 'NORMAL', color: 'var(--threat-safe)', bg: 'rgba(48,209,88,0.08)', border: 'rgba(48,209,88,0.2)', icon: '🟢' },
    elevated: { label: 'ELEVATED', color: 'var(--threat-medium)', bg: 'rgba(255,159,10,0.08)', border: 'rgba(255,159,10,0.2)', icon: '🟠' },
    lockdown: { label: 'LOCKDOWN', color: 'var(--threat-critical)', bg: 'rgba(255,45,85,0.1)', border: 'rgba(255,45,85,0.25)', icon: '🔴' },
  };

  const mode = modeConfig[defenseMode] || modeConfig.normal;
  const blockRate = totalAnalyzed > 0 ? Math.round((totalBlocked / totalAnalyzed) * 100) : 0;
  const trustTrend = trustScore > 70 ? '↑' : trustScore > 30 ? '→' : '↓';
  const trustTrendColor = trustScore > 70 ? 'var(--threat-safe)' : trustScore > 30 ? 'var(--threat-medium)' : 'var(--threat-critical)';
  const activePolicies = Object.values(pipelineStatus).filter(s => s !== 'nominal').length;

  const stats = [
    { label: 'BLOCKED', value: totalBlocked, color: totalBlocked > 0 ? 'var(--threat-critical)' : 'var(--text-tertiary)' },
    { label: 'BLOCK %', value: `${blockRate}%`, color: blockRate > 50 ? 'var(--threat-critical)' : blockRate > 0 ? 'var(--threat-medium)' : 'var(--text-tertiary)' },
    { label: 'SESSION', value: formatDuration(duration), color: 'var(--text-secondary)' },
  ];

  const containerVariants = {
    hidden: {},
    visible: { transition: { staggerChildren: 0.08, delayChildren: 0.1 } },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 12, scale: 0.95 },
    visible: { opacity: 1, y: 0, scale: 1, transition: { type: 'spring', stiffness: 180, damping: 18 } },
  };

  return (
    <motion.div
      className="glass-panel"
      style={{ padding: 'var(--space-md)' }}
      initial={{ opacity: 0, y: -15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: 'spring', stiffness: 120, damping: 20 }}
    >
      <div className="section-label" style={{ marginBottom: 'var(--space-sm)' }}>Security Posture</div>

      {/* Defense Mode Badge */}
      <motion.div
        layout
        transition={{ type: 'spring', stiffness: 200, damping: 25 }}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-sm)',
          padding: '8px 12px',
          borderRadius: 'var(--radius-md)',
          background: mode.bg,
          border: `1px solid ${mode.border}`,
          marginBottom: 'var(--space-md)',
        }}
      >
        <motion.span
          key={mode.icon}
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ type: 'spring', stiffness: 200, damping: 12 }}
          style={{ fontSize: '16px' }}
        >
          {mode.icon}
        </motion.span>
        <div style={{ flex: 1 }}>
          <motion.div
            key={mode.label}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
            style={{
              fontFamily: 'var(--font-display)',
              fontWeight: 700,
              fontSize: 'var(--text-sm)',
              color: mode.color,
              letterSpacing: '0.1em',
            }}
          >
            {mode.label} MODE
          </motion.div>
          <div style={{
            fontSize: '9px',
            fontFamily: 'var(--font-mono)',
            color: 'var(--text-tertiary)',
          }}>
            {defenseMode === 'normal' ? 'All systems nominal' :
             defenseMode === 'elevated' ? 'Enhanced monitoring active' :
             'Full quarantine — all tools locked'}
          </div>
        </div>
        <motion.div
          key={trustTrend}
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', stiffness: 300, damping: 15 }}
          style={{
            fontFamily: 'var(--font-mono)',
            fontSize: 'var(--text-sm)',
            fontWeight: 700,
            color: trustTrendColor,
          }}
        >
          {trustTrend}
        </motion.div>
      </motion.div>

      {/* Stats Grid */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr 1fr',
          gap: '6px',
        }}
      >
        {stats.map(stat => (
          <motion.div
            key={stat.label}
            variants={itemVariants}
            whileHover={{ scale: 1.04, borderColor: 'var(--border-active)' }}
            style={{
              textAlign: 'center',
              padding: '6px 4px',
              borderRadius: 'var(--radius-sm)',
              background: 'rgba(255,255,255,0.02)',
              border: '1px solid var(--border-subtle)',
              transition: 'border-color 0.2s',
            }}
          >
            <motion.div
              key={`${stat.label}-${stat.value}`}
              initial={{ scale: 1.2 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 300, damping: 15 }}
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: 'var(--text-sm)',
                fontWeight: 700,
                color: stat.color,
              }}
            >
              {stat.value}
            </motion.div>
            <div style={{
              fontSize: '8px',
              fontFamily: 'var(--font-mono)',
              color: 'var(--text-tertiary)',
              textTransform: 'uppercase',
              letterSpacing: '0.08em',
            }}>
              {stat.label}
            </div>
          </motion.div>
        ))}
      </motion.div>

      {/* Active Policies */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        style={{
          marginTop: 'var(--space-sm)',
          fontSize: '9px',
          fontFamily: 'var(--font-mono)',
          color: 'var(--text-tertiary)',
          display: 'flex',
          justifyContent: 'space-between',
          padding: '4px 0',
        }}
      >
        <span>Active policies: <span style={{ color: activePolicies > 0 ? 'var(--threat-medium)' : 'var(--text-secondary)' }}>{activePolicies > 0 ? activePolicies : 'baseline'}</span></span>
        <span>Analyzed: <span style={{ color: 'var(--text-secondary)' }}>{totalAnalyzed}</span></span>
      </motion.div>
    </motion.div>
  );
}
