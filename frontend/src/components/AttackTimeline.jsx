import { useRef, useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function AttackTimeline({ timelineEvents }) {
  const containerRef = useRef(null);
  const [hoveredEvent, setHoveredEvent] = useState(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollLeft = containerRef.current.scrollWidth;
    }
  }, [timelineEvents]);

  const severityColors = {
    critical: '#ff2d55',
    high: '#ff6b35',
    medium: '#ff9f0a',
    low: '#ffd60a',
    safe: '#30d158',
    clean: '#30d158',
  };

  if (timelineEvents.length === 0) return null;

  const startTime = timelineEvents[0]?.timestamp || Date.now();
  const endTime = Date.now();
  const totalSpan = Math.max(endTime - startTime, 5000);

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: 'spring', stiffness: 150, damping: 20 }}
      style={{
        position: 'absolute',
        bottom: 'var(--space-md)',
        left: 'var(--space-md)',
        right: 'var(--space-md)',
        zIndex: 10,
        pointerEvents: 'auto',
      }}
    >
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '6px',
        marginBottom: '4px',
      }}>
        <span style={{
          fontSize: '8px',
          fontFamily: 'var(--font-mono)',
          color: 'var(--text-tertiary)',
          textTransform: 'uppercase',
          letterSpacing: '0.12em',
        }}>
          Attack Timeline
        </span>
        <div style={{
          flex: 1,
          height: '1px',
          background: 'linear-gradient(90deg, var(--border-subtle), transparent)',
        }} />
        <span style={{
          fontSize: '8px',
          fontFamily: 'var(--font-mono)',
          color: 'var(--text-tertiary)',
        }}>
          {timelineEvents.length} events
        </span>
      </div>

      <div
        ref={containerRef}
        style={{
          position: 'relative',
          height: '36px',
          background: 'rgba(5, 5, 8, 0.75)',
          backdropFilter: 'blur(12px)',
          borderRadius: 'var(--radius-sm)',
          border: '1px solid var(--border-subtle)',
          overflow: 'hidden',
          cursor: 'crosshair',
        }}
      >
        {/* Background track */}
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '8px',
          right: '8px',
          height: '2px',
          background: 'rgba(255,255,255,0.04)',
          transform: 'translateY(-50%)',
        }} />

        {/* Event dots */}
        <AnimatePresence>
          {timelineEvents.map((event) => {
            const position = ((event.timestamp - startTime) / totalSpan) * 100;
            const clampedPosition = Math.min(Math.max(position, 2), 98);
            const color = severityColors[event.severity] || severityColors.safe;
            const isMalicious = event.severity !== 'safe' && event.type !== 'clean';
            const dotSize = isMalicious ? 8 : 5;

            return (
              <motion.div
                key={event.id}
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ type: 'spring', stiffness: 400, damping: 15 }}
                onMouseEnter={() => setHoveredEvent(event)}
                onMouseLeave={() => setHoveredEvent(null)}
                style={{
                  position: 'absolute',
                  left: `${clampedPosition}%`,
                  top: '50%',
                  transform: 'translate(-50%, -50%)',
                  width: `${dotSize}px`,
                  height: `${dotSize}px`,
                  borderRadius: '50%',
                  background: color,
                  boxShadow: isMalicious ? `0 0 8px ${color}, 0 0 16px ${color}` : `0 0 4px ${color}`,
                  zIndex: isMalicious ? 3 : 1,
                  cursor: 'pointer',
                }}
              />
            );
          })}
        </AnimatePresence>

        {/* Hover tooltip */}
        <AnimatePresence>
          {hoveredEvent && (
            <motion.div
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 5 }}
              transition={{ duration: 0.15 }}
              style={{
                position: 'absolute',
                top: '-32px',
                left: `${Math.min(Math.max(((hoveredEvent.timestamp - startTime) / totalSpan) * 100, 10), 90)}%`,
                transform: 'translateX(-50%)',
                padding: '3px 8px',
                borderRadius: 'var(--radius-sm)',
                background: 'rgba(10,10,18,0.95)',
                border: `1px solid ${severityColors[hoveredEvent.severity] || 'var(--border-subtle)'}`,
                fontSize: '8px',
                fontFamily: 'var(--font-mono)',
                color: severityColors[hoveredEvent.severity] || 'var(--text-secondary)',
                whiteSpace: 'nowrap',
                pointerEvents: 'none',
                zIndex: 20,
                boxShadow: '0 4px 12px rgba(0,0,0,0.5)',
              }}
            >
              {hoveredEvent.label} ({hoveredEvent.severity})
            </motion.div>
          )}
        </AnimatePresence>

        {/* Current time cursor */}
        <motion.div
          animate={{ opacity: [0.6, 1, 0.6] }}
          transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
          style={{
            position: 'absolute',
            right: '4px',
            top: '4px',
            bottom: '4px',
            width: '2px',
            background: 'var(--mode-accent)',
            borderRadius: '1px',
            boxShadow: '0 0 8px var(--mode-accent)',
          }}
        />

        {/* Time labels */}
        <div style={{
          position: 'absolute',
          bottom: '2px',
          left: '8px',
          fontSize: '7px',
          fontFamily: 'var(--font-mono)',
          color: 'var(--text-tertiary)',
          opacity: 0.6,
        }}>
          {new Date(startTime).toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}
        </div>
        <div style={{
          position: 'absolute',
          bottom: '2px',
          right: '8px',
          fontSize: '7px',
          fontFamily: 'var(--font-mono)',
          color: 'var(--text-tertiary)',
          opacity: 0.6,
        }}>
          NOW
        </div>
      </div>
    </motion.div>
  );
}
