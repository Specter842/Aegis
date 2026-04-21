import { useState, useCallback, useRef, useEffect } from 'react';
import { useAegisRealtime } from './useAegisRealtime';
import { fetchIncidents, fetchDocuments, fetchUrls, proxyChat as apiProxyChat } from './aegisApi';

// ============================================================
// Tool Permissions
// ============================================================
const TOOL_PERMISSIONS = [
  { id: 'file_read', name: 'File Read', icon: '📄', minTrust: 20 },
  { id: 'file_write', name: 'File Write', icon: '✏️', minTrust: 60 },
  { id: 'database', name: 'Database', icon: '🗄️', minTrust: 50 },
  { id: 'api_call', name: 'API Calls', icon: '🌐', minTrust: 40 },
  { id: 'email', name: 'Email Send', icon: '📧', minTrust: 70 },
  { id: 'code_exec', name: 'Code Exec', icon: '⚡', minTrust: 80 },
  { id: 'admin', name: 'Admin Panel', icon: '🔑', minTrust: 90 },
  { id: 'memory', name: 'Memory Write', icon: '🧠', minTrust: 55 },
];

// ============================================================
// Attack Graph Data
// ============================================================
const ATTACK_GRAPH_NODES = [
  { id: 'user', label: 'User Input', type: 'source', x: 0, y: 0, z: 0 },
  { id: 'prompt_gate', label: 'Ingress Filter', type: 'defense', x: 2, y: 1, z: 0 },
  { id: 'llm', label: 'LLM Core', type: 'target', x: 4, y: 0, z: 0 },
  { id: 'reasoning', label: 'Intent Analyzer', type: 'defense', x: 3, y: -1, z: 1 },
  { id: 'tool_sandbox', label: 'Exec Sandbox', type: 'defense', x: 5, y: 1.5, z: -1 },
  { id: 'memory', label: 'Memory Guardian', type: 'target', x: 6, y: -1, z: 0 },
  { id: 'output_gate', label: 'Egress Filter', type: 'defense', x: 7, y: 0, z: 1 },
  { id: 'file_system', label: 'File System', type: 'resource', x: 6, y: 2, z: -1 },
  { id: 'database', label: 'Database', type: 'resource', x: 7, y: 2, z: 1 },
  { id: 'api', label: 'External API', type: 'resource', x: 8, y: 1, z: 0 },
  { id: 'output', label: 'User Output', type: 'sink', x: 9, y: 0, z: 0 },
];

const ATTACK_GRAPH_EDGES = [
  { source: 'user', target: 'prompt_gate' },
  { source: 'prompt_gate', target: 'llm' },
  { source: 'llm', target: 'reasoning' },
  { source: 'reasoning', target: 'tool_sandbox' },
  { source: 'tool_sandbox', target: 'file_system' },
  { source: 'tool_sandbox', target: 'database' },
  { source: 'tool_sandbox', target: 'api' },
  { source: 'llm', target: 'memory' },
  { source: 'memory', target: 'llm' },
  { source: 'llm', target: 'output_gate' },
  { source: 'output_gate', target: 'output' },
];

// ============================================================
// Defense Mode Logic
// ============================================================
function computeDefenseMode(trustScore) {
  if (trustScore > 70) return 'normal';
  if (trustScore > 30) return 'elevated';
  return 'lockdown';
}

// ============================================================
// Severity helpers
// ============================================================
const SEVERITY_ORDER = { critical: 4, high: 3, medium: 2, low: 1, safe: 0 };
const SEVERITY_DECAY = { critical: 30, high: 20, medium: 12, low: 5 };

function mapAttackTypeToGraphPath(attackType) {
  if (['code_execution', 'destructive_action', 'tool_manipulation'].includes(attackType)) {
    return { path: ['user', 'prompt_gate', 'llm', 'reasoning', 'tool_sandbox'], point: 'tool_sandbox' };
  }
  if (attackType === 'memory_poisoning') {
    return { path: ['user', 'prompt_gate', 'llm', 'memory'], point: 'memory' };
  }
  if (attackType === 'data_exfiltration') {
    return { path: ['user', 'prompt_gate', 'llm', 'output_gate'], point: 'output_gate' };
  }
  return { path: ['user', 'prompt_gate'], point: 'prompt_gate' };
}

// ============================================================
// Main Hook
// ============================================================
export function useAegis() {
  const [trustScore, setTrustScore] = useState(100);
  const [defenseMode, setDefenseMode] = useState('normal'); // normal, elevated, lockdown
  const [events, setEvents] = useState([]);
  const [currentAttack, setCurrentAttack] = useState(null);
  const [attackHistory, setAttackHistory] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeNodes, setActiveNodes] = useState([]);
  const [activeEdges, setActiveEdges] = useState([]);
  const [shieldBurst, setShieldBurst] = useState(null);
  const [totalBlocked, setTotalBlocked] = useState(0);
  const [totalAnalyzed, setTotalAnalyzed] = useState(0);
  const [autonomousActions, setAutonomousActions] = useState([]);
  const [pipelineStatus, setPipelineStatus] = useState({
    ingress: 'nominal',
    intent: 'nominal',
    sandbox: 'nominal',
    memory: 'nominal',
    egress: 'nominal',
  });
  const [timelineEvents, setTimelineEvents] = useState([]);
  const [historyLoaded, setHistoryLoaded] = useState(false);
  
  const [documents, setDocuments] = useState([]);
  const [urls, setUrls] = useState([]);
  const [proxyMode, setProxyMode] = useState(false); // false = scan only, true = proxy
  const [lastProxyResult, setLastProxyResult] = useState(null);
  
  const eventIdRef = useRef(0);

  const actionIdRef = useRef(0);
  const sessionStart = useRef(Date.now());

  // ──────────────────────────────────────────
  // Phase 2: Real-Time WebSocket Integration
  // ──────────────────────────────────────────
  const realtime = useAegisRealtime();

  // ──────────────────────────────────────────
  // Add autonomous action
  // ──────────────────────────────────────────
  const addAction = useCallback((icon, message, type = 'info') => {
    const action = {
      id: ++actionIdRef.current,
      timestamp: new Date(),
      icon,
      message,
      type, // info, warning, critical, recovery
    };
    setAutonomousActions(prev => [action, ...prev].slice(0, 30));
    return action;
  }, []);

  // ──────────────────────────────────────────
  // Phase 2: Load incident history on mount
  // ──────────────────────────────────────────
  useEffect(() => {
    if (historyLoaded) return;

    async function loadHistory() {
      try {
        const { incidents, total } = await fetchIncidents({ limit: 50 });
        
        const docs = await fetchDocuments();
        setDocuments(docs);
        
        const u = await fetchUrls();
        setUrls(u);

        if (incidents.length > 0) {
          // Populate timeline from historical incidents
          const historyTimeline = incidents
            .filter(inc => inc.detection_count > 0)
            .map(inc => ({
              id: `hist-${inc.id}`,
              timestamp: new Date(inc.created_at).getTime(),
              severity: inc.detections?.[0]?.severity || 'medium',
              type: inc.detections?.[0]?.attack_type || 'unknown',
              label: inc.detections?.[0]?.explanation || 'Historical Detection',
            }))
            .reverse(); // oldest first for timeline

          setTimelineEvents(prev => [...historyTimeline, ...prev].slice(-50));

          // Update counters from history
          const blocked = incidents.filter(i => i.decision === 'block' || i.decision === 'challenge').length;
          setTotalAnalyzed(prev => Math.max(prev, total));
          setTotalBlocked(prev => Math.max(prev, blocked));

          addAction('📊', `Loaded ${incidents.length} historical incidents`, 'info');
        }
      } catch (e) {
        console.warn('[AEGIS] Failed to load incident history:', e);
      }
      setHistoryLoaded(true);
    }

    loadHistory();
  }, [historyLoaded, addAction]);

  // ──────────────────────────────────────────
  // Phase 2: Handle real-time WebSocket events
  // ──────────────────────────────────────────
  useEffect(() => {
    const unsubscribe = realtime.onEvent((event) => {
      if (event.type === 'SYSTEM_STATUS') {
        handleSystemStatus(event);
      } else if (event.type === 'SCAN_COMPLETED') {
        handleScanCompleted(event);
      } else if (event.type === 'ATTACK_DETECTED') {
        handleAttackDetected(event);
      }
    });

    return unsubscribe;
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [realtime.onEvent]);

  // ──────────────────────────────────────────
  // Phase 2: WS connection state actions
  // ──────────────────────────────────────────
  useEffect(() => {
    if (realtime.isConnected) {
      addAction('🔗', 'WebSocket connected — live event stream active', 'info');
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [realtime.isConnected]);

  // ──────────────────────────────────────────
  // Event Handlers
  // ──────────────────────────────────────────

  function handleSystemStatus(event) {
    // Map system status into pipeline status
    const components = event.components || {};
    const isAnyDegraded = Object.values(components).some(c => !c.is_ready);

    setPipelineStatus({
      ingress: isAnyDegraded ? 'alert' : 'nominal',
      intent: 'nominal',
      sandbox: 'nominal',
      memory: 'nominal',
      egress: 'nominal',
    });
  }

  function handleScanCompleted(event) {
    setTotalAnalyzed(prev => prev + 1);

    // Add clean scan to timeline
    if (event.detection_count === 0) {
      setTimelineEvents(prev => [...prev, {
        id: `ws-${event.trace_id}`,
        timestamp: Date.now(),
        severity: 'safe',
        type: 'clean',
        label: 'Clean',
      }].slice(-50));
    }

    // Recover trust slightly on clean scans
    if (event.decision === 'allow' && event.risk_score === 0) {
      setTrustScore(prev => {
        const newTrust = Math.min(100, prev + 3);
        const newMode = computeDefenseMode(newTrust);
        setDefenseMode(currentMode => {
          if (newMode !== currentMode && newMode === 'normal') {
            addAction('✅', 'DEFENSE RESTORED → NORMAL MODE', 'recovery');
          }
          return newMode;
        });
        return newTrust;
      });
    }
  }

  function handleAttackDetected(event) {
    setTotalBlocked(prev => prev + 1);

    // Compute severity from event
    const topSeverity = event.severity || 'high';
    const attackTypes = event.attack_types || [];
    const primaryAttackType = attackTypes[0] || 'unknown';

    // Compute trust decay
    const decay = SEVERITY_DECAY[topSeverity] || 15;
    setTrustScore(prev => {
      const newTrust = Math.max(0, prev - decay);
      const newMode = computeDefenseMode(newTrust);

      setDefenseMode(currentMode => {
        if (newMode !== currentMode) {
          if (newMode === 'elevated' && currentMode === 'normal') {
            addAction('🔶', 'DEFENSE ESCALATED → ELEVATED MODE', 'warning');
          } else if (newMode === 'lockdown') {
            addAction('🚨', 'DEFENSE ESCALATED → LOCKDOWN MODE', 'critical');
          }
        }
        return newMode;
      });

      return newTrust;
    });

    // Add to timeline
    setTimelineEvents(prev => [...prev, {
      id: `ws-${event.trace_id}`,
      timestamp: Date.now(),
      severity: topSeverity,
      type: primaryAttackType,
      label: event.operator_summary || `${topSeverity.toUpperCase()} attack detected`,
    }].slice(-50));

    // Build attack event for UI components
    const attackEvent = {
      id: event.trace_id,
      timestamp: new Date(event.timestamp),
      prompt: null, // Not sent over WS for safety
      isMalicious: true,
      riskScore: Math.round(event.risk_score * 100),
      severity: topSeverity,
      attacks: (event.top_detections || []).map(d => ({
        type: d.attack_type,
        name: d.explanation,
        severity: d.severity,
        confidence: d.score,
      })),
      reconstruction: null, // Reconstruction not sent over WS
      attackPath: mapAttackTypeToGraphPath(primaryAttackType).path,
      interceptionPoint: mapAttackTypeToGraphPath(primaryAttackType).point,
      layers: {
        prompt_gate: { status: 'intercepted', details: `Detected ${event.top_detections?.length || 0} threat(s)` },
        reasoning_monitor: { status: primaryAttackType === 'jailbreak' ? 'alert' : 'nominal', details: 'Chain-of-thought analysis' },
        tool_sandbox: { status: ['code_execution', 'destructive_action', 'tool_manipulation'].includes(primaryAttackType) ? 'blocked' : 'nominal', details: 'Tool access control' },
        memory_sentinel: { status: primaryAttackType === 'memory_poisoning' ? 'quarantined' : 'nominal', details: 'Memory integrity check' },
        output_gate: { status: primaryAttackType === 'data_exfiltration' ? 'filtered' : 'nominal', details: 'Output sanitization' },
      },
      trustScore: 0, // Will be updated by state
      defenseMode: 'normal', // Will be updated by state
      operatorSummary: event.operator_summary,
      sourceKind: event.source_kind || 'prompt',
      quarantined: event.quarantined,
    };

    // Trigger graph animation
    setActiveNodes(attackEvent.attackPath);
    setActiveEdges(attackEvent.attackPath.slice(0, -1).map((n, i) => `${n}-${attackEvent.attackPath[i + 1]}`));
    setShieldBurst(attackEvent.interceptionPoint);
    setTimeout(() => {
      setActiveNodes([]);
      setActiveEdges([]);
      setShieldBurst(null);
    }, 4000);

    // Update pipeline status
    setPipelineStatus({
      ingress: attackEvent.layers.prompt_gate.status,
      intent: attackEvent.layers.reasoning_monitor.status,
      sandbox: attackEvent.layers.tool_sandbox.status,
      memory: attackEvent.layers.memory_sentinel.status,
      egress: attackEvent.layers.output_gate.status,
    });

    // Add autonomous actions
    addAction('🔍', `Detected ${attackTypes.length} threat vector(s): ${attackTypes.join(', ')}`, 'warning');
    addAction('🛡️', `Decision: ${event.decision?.toUpperCase()} — ${event.recommended_action}`, 'critical');

    setCurrentAttack(attackEvent);
    setAttackHistory(prev => [attackEvent, ...prev].slice(0, 100));
  }

  // ──────────────────────────────────────────
  // REST-based prompt analysis (synchronous path)
  // ──────────────────────────────────────────
  const analyzePrompt = useCallback(async (prompt) => {
    setIsProcessing(true);
    setTotalAnalyzed(prev => prev + 1);

    try {
      // Call the real backend via legacy adapter
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, session_id: 'default' }),
      });

      if (!response.ok) throw new Error('Backend unavailable');

      const result = await response.json();

      // Map backend result to frontend event
      const event = {
        id: result.id,
        timestamp: new Date(result.timestamp),
        prompt: result.prompt,
        isMalicious: result.is_malicious,
        riskScore: result.risk_score,
        severity: result.severity,
        attacks: result.attacks,
        reconstruction: result.reconstruction,
        attackPath: result.attack_path,
        interceptionPoint: result.interception_point,
        layers: result.layers,
        trustScore: result.trust_score,
        defenseMode: computeDefenseMode(result.trust_score),
      };

      // Trust & defense mode updates from REST response
      setTrustScore(event.trustScore);
      setTotalBlocked(prev => result.is_malicious ? prev + 1 : prev);

      setDefenseMode(prevMode => {
        const newMode = event.defenseMode;
        if (newMode !== prevMode) {
          if (newMode === 'elevated' && prevMode === 'normal') addAction('🔶', 'DEFENSE ESCALATED → ELEVATED MODE', 'warning');
          else if (newMode === 'lockdown') addAction('🚨', 'DEFENSE ESCALATED → LOCKDOWN MODE', 'critical');
          else if (newMode === 'normal') addAction('✅', 'DEFENSE RESTORED → NORMAL MODE', 'recovery');
        }
        return newMode;
      });

      if (result.is_malicious) {
        addAction('🔍', `Detected ${result.attacks.length} threat(s)`, 'warning');
        addAction('🔄', 'Reconstructed prompt — neutralized vector(s)', 'info');
      }

      // Attack graph path animation
      if (result.is_malicious) {
        setActiveNodes(event.attackPath);
        setActiveEdges(event.attackPath.slice(0, -1).map((n, i) => `${n}-${event.attackPath[i + 1]}`));
        setShieldBurst(event.interceptionPoint);
        setTimeout(() => {
          setActiveNodes([]);
          setActiveEdges([]);
          setShieldBurst(null);
        }, 4000);
      }

      setPipelineStatus({
        ingress: result.layers.prompt_gate.status,
        intent: result.layers.reasoning_monitor.status,
        sandbox: result.layers.tool_sandbox.status,
        memory: result.layers.memory_sentinel.status,
        egress: result.layers.output_gate.status,
      });

      setTimelineEvents(prev => [...prev, {
        id: event.id,
        timestamp: Date.now(),
        severity: event.severity,
        type: event.isMalicious ? (event.attacks[0]?.type || 'unknown') : 'clean',
        label: event.isMalicious ? event.attacks[0]?.name : 'Clean',
      }].slice(-50));

      setCurrentAttack(event);
      setEvents(prev => [event, ...prev].slice(0, 50));
      if (event.isMalicious) setAttackHistory(prev => [event, ...prev].slice(0, 100));

    } catch (error) {
      console.warn('AEGIS Backend offline — prompt analysis unavailable:', error);
      addAction('⚠️', 'Backend unreachable — scan not performed', 'warning');
    }

    setIsProcessing(false);
  }, [addAction]);

  const proxyPrompt = useCallback(async (prompt) => {
    setIsProcessing(true);
    setTotalAnalyzed(prev => prev + 1);
    setLastProxyResult(null);

    try {
      const result = await apiProxyChat({ prompt });
      if (!result) throw new Error('Proxy unavailable');

      // Add to events for prompt display
      const event = {
        id: result.trace_id,
        timestamp: new Date(),
        prompt: prompt,
        isMalicious: result.decision === 'block',
        riskScore: result.llm_called ? result.output_scan?.risk_score || 0 : result.risk_score || 0,
        severity: result.decision === 'block' ? 'high' : 'safe',
        attacks: [], 
        trustScore: result.decision === 'block' ? Math.max(0, trustScore - 15) : trustScore,
      };
      
      setLastProxyResult(result);
      setEvents(prev => [event, ...prev].slice(0, 50));
      
      if (result.decision === 'block') {
         addAction('🚫', result.llm_called && result.output_scan?.blocked ? 'Output block applied' : 'Prompt blocked before execution', 'warning');
      } else {
         addAction('✅', 'Proxied safely', 'info');
      }
    } catch (e) {
      console.warn('Proxy error', e);
      addAction('⚠️', 'Proxy unavailable', 'warning');
    }
    setIsProcessing(false);
  }, [addAction, trustScore]);

  const resetTrust = useCallback(async () => {
    try {
      await fetch('/api/reset-trust?session_id=default', { method: 'POST' });
    } catch (e) {
      console.warn('Backend reset failed:', e);
    }
    setTrustScore(100);
    setDefenseMode('normal');
    setPipelineStatus({
      ingress: 'nominal', intent: 'nominal', sandbox: 'nominal', memory: 'nominal', egress: 'nominal',
    });
    addAction('🔄', 'Trust engine reset — all permissions restored, defense mode NORMAL', 'recovery');
  }, [addAction]);

  const getPermissions = useCallback(() => {
    return TOOL_PERMISSIONS.map(tool => ({
      ...tool,
      granted: trustScore >= tool.minTrust,
    }));
  }, [trustScore]);

  const getAttackStats = useCallback(() => {
    const typeCounts = {};
    attackHistory.forEach(e => {
      (e.attacks || []).forEach(a => {
        typeCounts[a.type] = (typeCounts[a.type] || 0) + 1;
      });
    });
    return typeCounts;
  }, [attackHistory]);

  const getSessionDuration = useCallback(() => {
    return Math.floor((Date.now() - sessionStart.current) / 1000);
  }, []);

  return {
    trustScore,
    defenseMode,
    events,
    currentAttack,
    attackHistory,
    isProcessing,
    activeNodes,
    activeEdges,
    shieldBurst,
    totalBlocked,
    totalAnalyzed,
    autonomousActions,
    pipelineStatus,
    timelineEvents,
    analyzePrompt,
    resetTrust,
    getPermissions,
    getAttackStats,
    getSessionDuration,
    documents,
    urls,
    loadSources: async () => {
        const docs = await fetchDocuments();
        setDocuments(docs);
        const u = await fetchUrls();
        setUrls(u);
    },
    proxyMode,
    setProxyMode,
    proxyPrompt,
    lastProxyResult,
    graphData: { nodes: ATTACK_GRAPH_NODES, edges: ATTACK_GRAPH_EDGES },

    // Phase 2: WebSocket state
    wsConnectionState: realtime.connectionState,
    isWsConnected: realtime.isConnected,
    systemStatus: realtime.systemStatus,
  };
}
