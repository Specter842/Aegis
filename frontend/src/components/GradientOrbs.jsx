import { motion } from 'framer-motion';

const orbs = [
  {
    size: 600,
    color: 'rgba(0, 240, 255, 0.045)',
    x: '15%',
    y: '20%',
    duration: 22,
    delay: 0,
  },
  {
    size: 500,
    color: 'rgba(123, 97, 255, 0.04)',
    x: '75%',
    y: '60%',
    duration: 28,
    delay: 2,
  },
  {
    size: 450,
    color: 'rgba(59, 130, 246, 0.035)',
    x: '50%',
    y: '30%',
    duration: 25,
    delay: 5,
  },
  {
    size: 350,
    color: 'rgba(0, 255, 136, 0.025)',
    x: '85%',
    y: '15%',
    duration: 30,
    delay: 8,
  },
];

export default function GradientOrbs({ defenseMode = 'normal' }) {
  const modeHue = {
    normal: 0,
    elevated: 30,
    lockdown: -60,
  };

  return (
    <div
      className="gradient-orbs"
      style={{
        position: 'fixed',
        inset: 0,
        overflow: 'hidden',
        pointerEvents: 'none',
        zIndex: 0,
      }}
    >
      {orbs.map((orb, i) => (
        <motion.div
          key={i}
          style={{
            position: 'absolute',
            width: orb.size,
            height: orb.size,
            borderRadius: '50%',
            background: `radial-gradient(circle, ${orb.color} 0%, transparent 70%)`,
            filter: `blur(80px) hue-rotate(${modeHue[defenseMode] || 0}deg)`,
            left: orb.x,
            top: orb.y,
            willChange: 'transform',
          }}
          animate={{
            x: [0, 40, -30, 20, 0],
            y: [0, -30, 20, -15, 0],
            scale: [1, 1.15, 0.9, 1.05, 1],
          }}
          transition={{
            duration: orb.duration,
            delay: orb.delay,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      ))}
    </div>
  );
}
