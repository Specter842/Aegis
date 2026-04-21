import { motion, AnimatePresence } from 'framer-motion';
import { useEffect, useState, useRef } from 'react';

export default function TrustGauge({ score, defenseMode }) {
  const [displayScore, setDisplayScore] = useState(score);
  const [particles, setParticles] = useState([]);
  const prevScore = useRef(score);

  useEffect(() => {
    const start = displayScore;
    const diff = score - start;
    const duration = 700;
    const startTime = Date.now();

    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplayScore(Math.round(start + diff * eased));
      if (progress < 1) requestAnimationFrame(animate);
    };
    requestAnimationFrame(animate);

    // Trigger particles on score change
    if (Math.abs(score - prevScore.current) > 5) {
      const newParticles = Array.from({ length: 8 }, (_, i) => ({
        id: Date.now() + i,
        angle: (i / 8) * 360,
        distance: 30 + Math.random() * 25,
      }));
      setParticles(newParticles);
      setTimeout(() => setParticles([]), 800);
    }
    prevScore.current = score;
  }, [score]);

  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  const progress = (displayScore / 100) * circumference;
  const dashOffset = circumference - progress;

  const getColor = () => {
    if (displayScore > 70) return 'var(--threat-safe)';
    if (displayScore > 40) return 'var(--threat-medium)';
    if (displayScore > 15) return 'var(--threat-high)';
    return 'var(--threat-critical)';
  };

  const getGradientId = () => {
    if (displayScore > 70) return 'grad-safe';
    if (displayScore > 40) return 'grad-warn';
    return 'grad-danger';
  };

  const getStatus = () => {
    if (displayScore > 70) return 'SECURE';
    if (displayScore > 40) return 'CAUTION';
    if (displayScore > 15) return 'DANGER';
    return 'CRITICAL';
  };

  return (
    <motion.div
      className="glass-panel"
      style={{
        padding: 'var(--space-md)',
        textAlign: 'center',
      }}
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ type: 'spring', stiffness: 120, damping: 18, delay: 0.1 }}
    >
      <div className="section-label">Trust Engine</div>

      <div style={{ position: 'relative', width: '140px', height: '140px', margin: '0 auto' }}>
        <svg width="140" height="140" viewBox="0 0 140 140" style={{ transform: 'rotate(-90deg)' }}>
          <defs>
            <linearGradient id="grad-safe" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#30d158" />
              <stop offset="100%" stopColor="#00ff88" />
            </linearGradient>
            <linearGradient id="grad-warn" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#ff9f0a" />
              <stop offset="100%" stopColor="#ffd60a" />
            </linearGradient>
            <linearGradient id="grad-danger" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#ff2d55" />
              <stop offset="100%" stopColor="#ff6b35" />
            </linearGradient>
          </defs>

          {/* Track */}
          <circle cx="70" cy="70" r={radius} fill="none" stroke="var(--border-subtle)" strokeWidth="5" />

          {/* Outer pulse ring on score change */}
          <motion.circle
            cx="70" cy="70" r={radius + 8}
            fill="none"
            stroke={getColor()}
            strokeWidth="1"
            initial={{ opacity: 0 }}
            animate={{
              opacity: [0, 0.3, 0],
              r: [radius + 4, radius + 14, radius + 20],
            }}
            transition={{ duration: 1.2, ease: 'easeOut' }}
            key={score}
          />

          {/* Progress arc */}
          <circle
            cx="70" cy="70" r={radius}
            fill="none"
            stroke={`url(#${getGradientId()})`}
            strokeWidth="5"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={dashOffset}
            style={{
              transition: 'stroke-dashoffset 0.7s cubic-bezier(0.4, 0, 0.2, 1)',
              filter: `drop-shadow(0 0 8px ${getColor()})`,
            }}
          />

          {/* Tick marks */}
          {Array.from({ length: 20 }).map((_, i) => {
            const angle = (i / 20) * Math.PI * 2;
            const x1 = 70 + (radius + 6) * Math.cos(angle);
            const y1 = 70 + (radius + 6) * Math.sin(angle);
            const x2 = 70 + (radius + 10) * Math.cos(angle);
            const y2 = 70 + (radius + 10) * Math.sin(angle);
            return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke="var(--border-subtle)" strokeWidth="1" />;
          })}
        </svg>

        {/* Score particles burst */}
        <AnimatePresence>
          {particles.map(p => {
            const rad = (p.angle * Math.PI) / 180;
            return (
              <motion.div
                key={p.id}
                initial={{
                  opacity: 1,
                  x: 70,
                  y: 70,
                  scale: 1,
                }}
                animate={{
                  opacity: 0,
                  x: 70 + Math.cos(rad) * p.distance,
                  y: 70 + Math.sin(rad) * p.distance,
                  scale: 0,
                }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.7, ease: 'easeOut' }}
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: 4,
                  height: 4,
                  borderRadius: '50%',
                  background: getColor(),
                  boxShadow: `0 0 6px ${getColor()}`,
                  pointerEvents: 'none',
                }}
              />
            );
          })}
        </AnimatePresence>

        {/* Center text */}
        <div style={{
          position: 'absolute', top: '50%', left: '50%',
          transform: 'translate(-50%, -50%)',
          textAlign: 'center',
        }}>
          <motion.div
            key={displayScore}
            initial={{ scale: 1.15 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 300, damping: 15 }}
            style={{
              fontSize: '2rem',
              fontFamily: 'var(--font-display)',
              fontWeight: 700,
              color: getColor(),
              lineHeight: 1,
              textShadow: `0 0 24px ${getColor()}`,
            }}
          >
            {displayScore}
          </motion.div>
          <motion.div
            key={getStatus()}
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            style={{
              fontSize: '8px',
              fontFamily: 'var(--font-mono)',
              color: 'var(--text-tertiary)',
              textTransform: 'uppercase',
              letterSpacing: '0.12em',
              marginTop: '3px',
            }}
          >
            {getStatus()}
          </motion.div>
        </div>
      </div>

      {/* Trust bars */}
      <div style={{ marginTop: 'var(--space-sm)', display: 'flex', gap: '2px', justifyContent: 'center' }}>
        {Array.from({ length: 20 }).map((_, i) => {
          const threshold = (i + 1) * 5;
          const filled = displayScore >= threshold;
          return (
            <motion.div
              key={i}
              initial={{ scaleY: 0 }}
              animate={{ scaleY: 1 }}
              transition={{ delay: 0.5 + i * 0.03, duration: 0.3, ease: 'easeOut' }}
              style={{
                width: '5px', height: '14px',
                borderRadius: '2px',
                background: filled ? getColor() : 'var(--border-subtle)',
                opacity: filled ? 1 : 0.3,
                transition: 'background 0.3s, opacity 0.3s',
                boxShadow: filled ? `0 0 4px ${getColor()}` : 'none',
                transformOrigin: 'bottom',
              }}
            />
          );
        })}
      </div>
    </motion.div>
  );
}
