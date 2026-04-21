import { useRef } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import AnimatedCounter from './AnimatedCounter';
import MagneticButton from './MagneticButton';

// Staggered letter animation for the title
function AnimatedTitle() {
  const letters = 'AEGIS'.split('');
  const containerVariants = {
    hidden: {},
    visible: {
      transition: { staggerChildren: 0.08, delayChildren: 0.3 },
    },
  };
  const letterVariants = {
    hidden: { opacity: 0, y: 50, rotateX: -90 },
    visible: {
      opacity: 1,
      y: 0,
      rotateX: 0,
      transition: { type: 'spring', stiffness: 100, damping: 12 },
    },
  };

  return (
    <motion.div
      className="hero__title"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      style={{ display: 'flex', gap: '2px', perspective: '800px' }}
    >
      {letters.map((letter, i) => (
        <motion.span
          key={i}
          variants={letterVariants}
          className="hero__letter"
        >
          {letter}
        </motion.span>
      ))}
    </motion.div>
  );
}

// Animated shield icon
function ShieldIcon() {
  return (
    <motion.div
      className="hero__shield"
      initial={{ scale: 0, rotate: -180 }}
      animate={{ scale: 1, rotate: 0 }}
      transition={{ type: 'spring', stiffness: 80, damping: 15, delay: 0.1 }}
    >
      <motion.div
        className="hero__shield-inner"
        animate={{
          boxShadow: [
            '0 0 30px rgba(0,240,255,0.2), 0 0 60px rgba(0,240,255,0.1)',
            '0 0 50px rgba(0,240,255,0.35), 0 0 100px rgba(0,240,255,0.15)',
            '0 0 30px rgba(0,240,255,0.2), 0 0 60px rgba(0,240,255,0.1)',
          ],
        }}
        transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
      >
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
          <motion.path
            d="M9 12l2 2 4-4"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ delay: 1.2, duration: 0.6, ease: 'easeOut' }}
          />
        </svg>
      </motion.div>
    </motion.div>
  );
}

export default function HeroSection({ totalAnalyzed, totalBlocked, trustScore, onLaunch }) {
  const heroRef = useRef(null);
  const { scrollYProgress } = useScroll({
    target: heroRef,
    offset: ['start start', 'end start'],
  });

  const heroOpacity = useTransform(scrollYProgress, [0, 0.8], [1, 0]);
  const heroScale = useTransform(scrollYProgress, [0, 0.8], [1, 0.92]);
  const heroY = useTransform(scrollYProgress, [0, 1], [0, -80]);

  const stats = [
    { label: 'Prompts Scanned', value: totalAnalyzed || 12847, suffix: '' },
    { label: 'Threats Blocked', value: totalBlocked || 423, suffix: '' },
    { label: 'Trust Score', value: trustScore || 100, suffix: '%' },
    { label: 'Uptime', value: 99.9, suffix: '%', decimals: 1 },
  ];

  return (
    <motion.section
      ref={heroRef}
      className="hero"
      style={{ opacity: heroOpacity, scale: heroScale, y: heroY }}
    >
      {/* Noise overlay */}
      <div className="hero__noise" />

      {/* Grid lines */}
      <div className="hero__grid" />

      {/* Radial gradient center */}
      <motion.div
        className="hero__radial"
        animate={{ scale: [1, 1.05, 1], opacity: [0.5, 0.7, 0.5] }}
        transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
      />

      <div className="hero__content">
        <ShieldIcon />
        <AnimatedTitle />

        <motion.p
          className="hero__subtitle"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.9, duration: 0.6 }}
        >
          Autonomous Execution Guard for Intelligent Systems
        </motion.p>

        <motion.p
          className="hero__description"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.1, duration: 0.6 }}
        >
          Real-time security kernel defending AI agent runtimes against
          prompt injection, jailbreaks, and adversarial exploitation.
        </motion.p>

        {/* Stats strip */}
        <motion.div
          className="hero__stats"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.3, duration: 0.6 }}
        >
          {stats.map((stat, i) => (
            <div key={stat.label} className="hero__stat">
              <AnimatedCounter
                value={stat.value}
                suffix={stat.suffix}
                decimals={stat.decimals || 0}
                delay={1.5 + i * 0.15}
                className="hero__stat-value"
              />
              <span className="hero__stat-label">{stat.label}</span>
            </div>
          ))}
        </motion.div>

        {/* CTA */}
        <motion.div
          className="hero__cta"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.8, duration: 0.6 }}
        >
          <MagneticButton
            className="btn btn--primary hero__btn"
            onClick={onLaunch}
            strength={0.3}
          >
            <span>Launch Dashboard</span>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="5" y1="12" x2="19" y2="12" />
              <polyline points="12 5 19 12 12 19" />
            </svg>
          </MagneticButton>
        </motion.div>

        {/* Scroll indicator */}
        <motion.div
          className="hero__scroll-indicator"
          animate={{ y: [0, 8, 0] }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 0.5 }}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="7 13 12 18 17 13" />
            <polyline points="7 6 12 11 17 6" />
          </svg>
        </motion.div>
      </div>

      {/* Decorative horizontal lines */}
      <motion.div
        className="hero__line hero__line--left"
        initial={{ scaleX: 0 }}
        animate={{ scaleX: 1 }}
        transition={{ delay: 0.5, duration: 1.2, ease: [0.25, 0.46, 0.45, 0.94] }}
      />
      <motion.div
        className="hero__line hero__line--right"
        initial={{ scaleX: 0 }}
        animate={{ scaleX: 1 }}
        transition={{ delay: 0.6, duration: 1.2, ease: [0.25, 0.46, 0.45, 0.94] }}
      />
    </motion.section>
  );
}
