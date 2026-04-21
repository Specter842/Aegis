import { useRef } from 'react';
import { motion, useInView } from 'framer-motion';

const directions = {
  up: { hidden: { opacity: 0, y: 60 }, visible: { opacity: 1, y: 0 } },
  down: { hidden: { opacity: 0, y: -60 }, visible: { opacity: 1, y: 0 } },
  left: { hidden: { opacity: 0, x: -60 }, visible: { opacity: 1, x: 0 } },
  right: { hidden: { opacity: 0, x: 60 }, visible: { opacity: 1, x: 0 } },
  scale: { hidden: { opacity: 0, scale: 0.85 }, visible: { opacity: 1, scale: 1 } },
  fade: { hidden: { opacity: 0 }, visible: { opacity: 1 } },
};

export default function AnimatedSection({
  children,
  direction = 'up',
  delay = 0,
  duration = 0.7,
  stagger = 0,
  threshold = 0.15,
  once = true,
  className = '',
  style = {},
  as = 'div',
}) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once, amount: threshold });

  const variants = {
    hidden: directions[direction]?.hidden || directions.up.hidden,
    visible: {
      ...directions[direction]?.visible || directions.up.visible,
      transition: {
        duration,
        delay,
        ease: [0.25, 0.46, 0.45, 0.94],
        staggerChildren: stagger,
      },
    },
  };

  const MotionComponent = motion[as] || motion.div;

  return (
    <MotionComponent
      ref={ref}
      variants={variants}
      initial="hidden"
      animate={isInView ? 'visible' : 'hidden'}
      className={className}
      style={style}
    >
      {children}
    </MotionComponent>
  );
}

// Child item for staggered containers
export function AnimatedItem({ children, className = '', style = {}, direction = 'up' }) {
  const variants = {
    hidden: directions[direction]?.hidden || directions.up.hidden,
    visible: {
      ...directions[direction]?.visible || directions.up.visible,
      transition: { duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] },
    },
  };

  return (
    <motion.div variants={variants} className={className} style={style}>
      {children}
    </motion.div>
  );
}
