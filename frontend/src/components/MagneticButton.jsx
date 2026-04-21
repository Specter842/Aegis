import { useRef, useState } from 'react';
import { motion, useMotionValue, useSpring } from 'framer-motion';

export default function MagneticButton({
  children,
  className = '',
  style = {},
  onClick,
  strength = 0.35,
  radius = 120,
  disabled = false,
  ...props
}) {
  const ref = useRef(null);
  const [isHovered, setIsHovered] = useState(false);

  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const springX = useSpring(x, { stiffness: 250, damping: 20, mass: 0.5 });
  const springY = useSpring(y, { stiffness: 250, damping: 20, mass: 0.5 });

  const handleMouseMove = (e) => {
    if (!ref.current || disabled) return;
    const rect = ref.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    const deltaX = e.clientX - centerX;
    const deltaY = e.clientY - centerY;
    const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

    if (distance < radius) {
      x.set(deltaX * strength);
      y.set(deltaY * strength);
    }
  };

  const handleMouseLeave = () => {
    x.set(0);
    y.set(0);
    setIsHovered(false);
  };

  return (
    <motion.button
      ref={ref}
      className={className}
      style={{ ...style, x: springX, y: springY, position: 'relative' }}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
      disabled={disabled}
      whileTap={{ scale: 0.95 }}
      {...props}
    >
      {children}
      {isHovered && (
        <motion.span
          className="magnetic-btn-glow"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          style={{
            position: 'absolute',
            inset: '-2px',
            borderRadius: 'inherit',
            background: 'linear-gradient(135deg, rgba(0,240,255,0.15), rgba(123,97,255,0.15))',
            filter: 'blur(8px)',
            zIndex: -1,
            pointerEvents: 'none',
          }}
        />
      )}
    </motion.button>
  );
}
