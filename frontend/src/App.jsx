import { useState, useRef } from 'react';
import { motion, useScroll, useMotionValueEvent } from 'framer-motion';
import { useAegis } from './hooks/useAegis';
import HeroSection from './components/HeroSection';
import FloatingNav from './components/FloatingNav';
import CursorGlow from './components/CursorGlow';
import GradientOrbs from './components/GradientOrbs';
import Header from './components/Header';
import AttackGraph3D from './components/AttackGraph3D';
import TrustGauge from './components/TrustGauge';
import PromptChat from './components/PromptChat';
import AttackReport from './components/AttackReport';
import PermissionMatrix from './components/PermissionMatrix';
import ThreatRadar from './components/ThreatRadar';
import PromptDiff from './components/PromptDiff';
import SecurityPosture from './components/SecurityPosture';
import AttackTimeline from './components/AttackTimeline';
import AutonomousActions from './components/AutonomousActions';
import SourcesPanel from './components/SourcesPanel';
import OutputSecurityPanel from './components/OutputSecurityPanel';
import ResponseDiffView from './components/ResponseDiffView';

export default function App() {
  const aegis = useAegis();
  const [sidebarTab, setSidebarTab] = useState('report');
  const [activeSection, setActiveSection] = useState('hero');
  const [showNav, setShowNav] = useState(false);
  const dashboardRef = useRef(null);

  // Track scroll to toggle floating nav and active section
  const { scrollY } = useScroll();

  useMotionValueEvent(scrollY, 'change', (latest) => {
    setShowNav(latest > window.innerHeight * 0.5);
    if (latest < window.innerHeight * 0.6) {
      setActiveSection('hero');
    } else {
      setActiveSection('dashboard');
    }
  });

  const scrollToDashboard = () => {
    dashboardRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Defense mode CSS class
  const defenseModeClass = aegis.defenseMode === 'elevated' ? 'defense-elevated'
    : aegis.defenseMode === 'lockdown' ? 'defense-lockdown'
    : '';

  return (
    <div className={defenseModeClass}>
      {/* Ambient effects */}
      <CursorGlow defenseMode={aegis.defenseMode} />
      <GradientOrbs defenseMode={aegis.defenseMode} />
      <div className="noise-overlay" />

      {/* Floating navigation */}
      <FloatingNav activeSection={activeSection} visible={showNav} />

      {/* Hero Section */}
      <div id="hero">
        <HeroSection
          totalAnalyzed={aegis.totalAnalyzed}
          totalBlocked={aegis.totalBlocked}
          trustScore={aegis.trustScore}
          onLaunch={scrollToDashboard}
        />
      </div>

      {/* Dashboard Section */}
      <div id="dashboard" ref={dashboardRef} className="dashboard-section">
        <div className={`dashboard ${defenseModeClass}`}>
          <Header
            trustScore={aegis.trustScore}
            defenseMode={aegis.defenseMode}
            totalBlocked={aegis.totalBlocked}
            totalAnalyzed={aegis.totalAnalyzed}
            pipelineStatus={aegis.pipelineStatus}
            onReset={aegis.resetTrust}
            wsConnectionState={aegis.wsConnectionState}
          />

          <div className="dashboard__main">
            <div className="graph-container glass-panel scanline-overlay" style={{ position: 'relative', overflow: 'hidden', minHeight: 0 }}>
              <AttackGraph3D
                graphData={aegis.graphData}
                activeNodes={aegis.activeNodes}
                activeEdges={aegis.activeEdges}
                shieldBurst={aegis.shieldBurst}
                defenseMode={aegis.defenseMode}
              />
              <div className="graph-overlay">
                <ThreatRadar attackStats={aegis.getAttackStats()} defenseMode={aegis.defenseMode} />
              </div>
              <AttackTimeline timelineEvents={aegis.timelineEvents} />
            </div>

            <div className="bottom-panels">
              <PromptChat
                onSubmit={aegis.analyzePrompt}
                proxyPrompt={aegis.proxyPrompt}
                proxyMode={aegis.proxyMode}
                setProxyMode={aegis.setProxyMode}
                isProcessing={aegis.isProcessing}
                events={aegis.events}
                defenseMode={aegis.defenseMode}
              />
              <AutonomousActions actions={aegis.autonomousActions} isWsConnected={aegis.isWsConnected} />
            </div>
          </div>

          <div className="dashboard__sidebar">
            <SecurityPosture
              trustScore={aegis.trustScore}
              defenseMode={aegis.defenseMode}
              totalBlocked={aegis.totalBlocked}
              totalAnalyzed={aegis.totalAnalyzed}
              pipelineStatus={aegis.pipelineStatus}
              getSessionDuration={aegis.getSessionDuration}
            />

            <TrustGauge score={aegis.trustScore} defenseMode={aegis.defenseMode} />

            <PermissionMatrix permissions={aegis.getPermissions()} trustScore={aegis.trustScore} defenseMode={aegis.defenseMode} />

            <div className="sidebar-tabs glass-panel">
              <div className="sidebar-tabs__header">
                <motion.button
                  className={`sidebar-tab ${sidebarTab === 'report' ? 'sidebar-tab--active' : ''}`}
                  onClick={() => setSidebarTab('report')}
                  whileHover={{ backgroundColor: 'rgba(255,255,255,0.03)' }}
                  whileTap={{ scale: 0.97 }}
                >
                  Forensics
                </motion.button>
                <motion.button
                  className={`sidebar-tab ${sidebarTab === 'diff' ? 'sidebar-tab--active' : ''}`}
                  onClick={() => setSidebarTab('diff')}
                  whileHover={{ backgroundColor: 'rgba(255,255,255,0.03)' }}
                  whileTap={{ scale: 0.97 }}
                >
                  Repair
                </motion.button>
                <motion.button
                  className={`sidebar-tab ${sidebarTab === 'sources' ? 'sidebar-tab--active' : ''}`}
                  onClick={() => setSidebarTab('sources')}
                  whileHover={{ backgroundColor: 'rgba(255,255,255,0.03)' }}
                  whileTap={{ scale: 0.97 }}
                >
                  Sources
                </motion.button>
                <motion.button
                  className={`sidebar-tab ${sidebarTab === 'proxy' ? 'sidebar-tab--active' : ''}`}
                  onClick={() => setSidebarTab('proxy')}
                  whileHover={{ backgroundColor: 'rgba(255,255,255,0.03)' }}
                  whileTap={{ scale: 0.97 }}
                >
                  Proxy Monitor
                </motion.button>
              </div>
              <div className="sidebar-tabs__content" style={{ overflowY: 'auto' }}>
                {sidebarTab === 'report' && <AttackReport attack={aegis.currentAttack} />}
                {sidebarTab === 'diff' && <PromptDiff attack={aegis.currentAttack} />}
                {sidebarTab === 'sources' && <SourcesPanel documents={aegis.documents} urls={aegis.urls} loadSources={aegis.loadSources} />}
                {sidebarTab === 'proxy' && (
                  <div style={{ padding: 'var(--space-md)' }}>
                    {aegis.lastProxyResult ? (
                      <>
                        <OutputSecurityPanel proxyResult={aegis.lastProxyResult} />
                        <ResponseDiffView proxyResult={aegis.lastProxyResult} />
                      </>
                    ) : (
                      <div style={{ color: 'var(--text-tertiary)', fontSize: '10px', textAlign: 'center', marginTop: '20px' }}>
                        No proxy events captured yet. Enable Proxy Mode and send a prompt.
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
