import { motion, AnimatePresence } from 'framer-motion';

const sections = [
  { id: 'hero', label: 'Home', icon: '⬡' },
  { id: 'dashboard', label: 'Dashboard', icon: '◈' },
];

export default function FloatingNav({ activeSection, visible }) {
  return (
    <AnimatePresence>
      {visible && (
        <motion.nav
          className="floating-nav"
          initial={{ y: 80, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 80, opacity: 0 }}
          transition={{ type: 'spring', stiffness: 200, damping: 25 }}
        >
          <div className="floating-nav__inner">
            {sections.map((section) => (
              <motion.button
                key={section.id}
                className={`floating-nav__item ${activeSection === section.id ? 'floating-nav__item--active' : ''}`}
                onClick={() => {
                  document.getElementById(section.id)?.scrollIntoView({ behavior: 'smooth' });
                }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <span className="floating-nav__icon">{section.icon}</span>
                <span className="floating-nav__label">{section.label}</span>
                {activeSection === section.id && (
                  <motion.div
                    className="floating-nav__indicator"
                    layoutId="nav-indicator"
                    transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                  />
                )}
              </motion.button>
            ))}
          </div>
        </motion.nav>
      )}
    </AnimatePresence>
  );
}
