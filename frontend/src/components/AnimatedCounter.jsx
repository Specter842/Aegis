import { useEffect, useRef } from 'react';
import { useMotionValue, useSpring, useInView, motion } from 'framer-motion';

export default function AnimatedCounter({
  value,
  duration = 1.5,
  delay = 0,
  prefix = '',
  suffix = '',
  decimals = 0,
  className = '',
  style = {},
  once = true,
}) {
  const ref = useRef(null);
  const motionValue = useMotionValue(0);
  const springValue = useSpring(motionValue, {
    stiffness: 60,
    damping: 25,
    restDelta: decimals > 0 ? 0.01 : 0.5,
  });
  const isInView = useInView(ref, { once });
  const displayRef = useRef(null);

  useEffect(() => {
    if (isInView) {
      const timer = setTimeout(() => {
        motionValue.set(value);
      }, delay * 1000);
      return () => clearTimeout(timer);
    }
  }, [isInView, value, delay, motionValue]);

  useEffect(() => {
    const unsubscribe = springValue.on('change', (latest) => {
      if (displayRef.current) {
        const formatted = decimals > 0
          ? latest.toFixed(decimals)
          : Math.round(latest).toLocaleString();
        displayRef.current.textContent = `${prefix}${formatted}${suffix}`;
      }
    });
    return unsubscribe;
  }, [springValue, prefix, suffix, decimals]);

  return (
    <motion.span
      ref={ref}
      className={className}
      style={style}
    >
      <span ref={displayRef}>{prefix}0{suffix}</span>
    </motion.span>
  );
}
