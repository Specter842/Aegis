import { useEffect, useRef } from 'react';
import { motion, useMotionValue, useSpring } from 'framer-motion';

export default function CursorGlow({ defenseMode = 'normal' }) {
  const cursorX = useMotionValue(-200);
  const cursorY = useMotionValue(-200);

  const springConfig = { stiffness: 120, damping: 30, mass: 0.8 };
  const x = useSpring(cursorX, springConfig);
  const y = useSpring(cursorY, springConfig);

  const modeColors = {
    normal: 'rgba(0, 240, 255, 0.07)',
    elevated: 'rgba(255, 159, 10, 0.07)',
    lockdown: 'rgba(255, 45, 85, 0.08)',
  };

  useEffect(() => {
    const handleMouseMove = (e) => {
      cursorX.set(e.clientX);
      cursorY.set(e.clientY);
    };

    window.addEventListener('mousemove', handleMouseMove, { passive: true });
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, [cursorX, cursorY]);

  return (
    <motion.div
      className="cursor-glow"
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '500px',
        height: '500px',
        borderRadius: '50%',
        background: `radial-gradient(circle, ${modeColors[defenseMode] || modeColors.normal} 0%, transparent 70%)`,
        pointerEvents: 'none',
        zIndex: 0,
        x,
        y,
        translateX: '-50%',
        translateY: '-50%',
        willChange: 'transform',
      }}
    />
  );
}
