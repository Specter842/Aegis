import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect } from 'react';

export default function PromptDiff({ attack }) {
  if (!attack || !attack.reconstruction) {
    return (
      <div style={{
        padding: 'var(--space-xl)',
        textAlign: 'center',
        color: 'var(--text-tertiary)',
        fontSize: 'var(--text-sm)',
      }}>
        <motion.div
          animate={{ rotate: [0, 360] }}
          transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
          style={{ fontSize: '28px', marginBottom: 'var(--space-sm)', opacity: 0.5, display: 'inline-block' }}
        >
          🔄
        </motion.div>
        <div>No reconstruction data</div>
        <div style={{ fontSize: 'var(--text-xs)', marginTop: 'var(--space-xs)' }}>
          Send a malicious prompt to see autonomous repair
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
        <div style={{
          fontSize: '9px',
          fontFamily: 'var(--font-mono)',
          color: 'var(--mode-accent)',
          textTransform: 'uppercase',
          letterSpacing: '0.1em',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
        }}>
          🔄 Repair // Prompt Reconstruction
        </div>

        {/* Original */}
        <motion.div
          initial={{ opacity: 0, x: -15 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1, type: 'spring', stiffness: 180, damping: 18 }}
        >
          <div style={{
            fontSize: '8px', fontFamily: 'var(--font-mono)', color: 'var(--threat-critical)',
            textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '3px',
            display: 'flex', alignItems: 'center', gap: '4px',
          }}>
            ✕ Original (Malicious)
          </div>
          <div style={{
            padding: '6px 10px', borderRadius: 'var(--radius-sm)',
            background: 'rgba(255,45,85,0.04)',
            border: '1px solid rgba(255,45,85,0.1)',
            borderLeft: '3px solid var(--threat-critical)',
            fontSize: '10px', fontFamily: 'var(--font-mono)',
            color: 'var(--text-secondary)', lineHeight: 1.5, wordBreak: 'break-word',
          }}>
            {attack.prompt}
          </div>
        </motion.div>

        {/* Arrow */}
        <motion.div
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3, type: 'spring', stiffness: 300, damping: 15 }}
          style={{ textAlign: 'center', color: 'var(--mode-accent)', fontSize: '14px', lineHeight: 1 }}
        >
          ↓
        </motion.div>

        {/* Reconstructed */}
        <motion.div
          initial={{ opacity: 0, x: 15 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4, type: 'spring', stiffness: 180, damping: 18 }}
        >
          <div style={{
            fontSize: '8px', fontFamily: 'var(--font-mono)', color: 'var(--threat-safe)',
            textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '3px',
            display: 'flex', alignItems: 'center', gap: '4px',
          }}>
            ✓ Reconstructed (Safe)
          </div>
          <TypewriterText
            text={attack.reconstruction.safe}
            delay={0.5}
          />
        </motion.div>

        {/* Changes */}
        <div>
          <div style={{
            fontSize: '8px', fontFamily: 'var(--font-mono)', color: 'var(--accent-purple)',
            textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '4px',
          }}>
            Surgical Changes
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
            {attack.reconstruction.changes.map((change, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -12, scale: 0.97 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                transition={{ delay: 0.6 + i * 0.12, type: 'spring', stiffness: 180, damping: 18 }}
                style={{
                  padding: '5px 8px', borderRadius: 'var(--radius-sm)',
                  background: 'rgba(123,97,255,0.03)',
                  border: '1px solid rgba(123,97,255,0.08)',
                }}
              >
                <div style={{ display: 'flex', gap: '6px', fontSize: '9px', fontFamily: 'var(--font-mono)', marginBottom: '2px' }}>
                  <span style={{ color: 'var(--threat-critical)', textDecoration: 'line-through', opacity: 0.6, maxWidth: '45%', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {change.original}
                  </span>
                  <motion.span
                    animate={{ x: [0, 3, 0] }}
                    transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
                    style={{ color: 'var(--text-tertiary)' }}
                  >
                    →
                  </motion.span>
                  <span style={{ color: 'var(--threat-safe)' }}>{change.replacement}</span>
                </div>
                <div style={{ fontSize: '9px', color: 'var(--text-tertiary)', fontStyle: 'italic' }}>
                  {change.reason}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}

// Typewriter component for the reconstructed text
function TypewriterText({ text, delay = 0 }) {
  const [displayText, setDisplayText] = useState('');
  const [done, setDone] = useState(false);

  useEffect(() => {
    setDisplayText('');
    setDone(false);
    const startTimeout = setTimeout(() => {
      let i = 0;
      const interval = setInterval(() => {
        if (i < text.length) {
          setDisplayText(text.slice(0, i + 1));
          i++;
        } else {
          clearInterval(interval);
          setDone(true);
        }
      }, 18);
      return () => clearInterval(interval);
    }, delay * 1000);
    return () => clearTimeout(startTimeout);
  }, [text, delay]);

  return (
    <div style={{
      padding: '6px 10px', borderRadius: 'var(--radius-sm)',
      background: 'rgba(48,209,88,0.03)',
      border: '1px solid rgba(48,209,88,0.1)',
      borderLeft: '3px solid var(--threat-safe)',
      fontSize: '10px', fontFamily: 'var(--font-mono)',
      color: 'var(--text-primary)', lineHeight: 1.5, wordBreak: 'break-word',
      minHeight: '2em',
    }}>
      {displayText}
      {!done && (
        <motion.span
          animate={{ opacity: [0, 1, 0] }}
          transition={{ duration: 0.8, repeat: Infinity }}
          style={{ color: 'var(--threat-safe)' }}
        >
          ▊
        </motion.span>
      )}
    </div>
  );
}
