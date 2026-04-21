import { useMemo } from 'react';

const ATTACK_CATEGORIES = [
  { key: 'prompt_injection', label: 'Injection', angle: 0 },
  { key: 'jailbreak', label: 'Jailbreak', angle: 60 },
  { key: 'privilege_escalation', label: 'Escalation', angle: 120 },
  { key: 'data_exfiltration', label: 'Exfiltration', angle: 180 },
  { key: 'code_execution', label: 'Execution', angle: 240 },
  { key: 'memory_poisoning', label: 'Poisoning', angle: 300 },
];

export default function ThreatRadar({ attackStats, defenseMode }) {
  const maxCount = useMemo(() => {
    const values = Object.values(attackStats);
    return values.length > 0 ? Math.max(...values, 1) : 1;
  }, [attackStats]);

  const center = 65;
  const maxRadius = 50;

  const modeColor = {
    normal: 'var(--threat-safe)',
    elevated: 'var(--threat-medium)',
    lockdown: 'var(--threat-critical)',
  }[defenseMode] || 'var(--threat-safe)';

  const getPoint = (angle, radius) => {
    const rad = (angle - 90) * (Math.PI / 180);
    return {
      x: center + radius * Math.cos(rad),
      y: center + radius * Math.sin(rad),
    };
  };

  const polygonPoints = ATTACK_CATEGORIES.map(cat => {
    const count = attackStats[cat.key] || 0;
    const allRelated = Object.entries(attackStats)
      .filter(([k]) => k.includes(cat.key.split('_')[0]) || cat.key.includes(k.split('_')[0]))
      .reduce((sum, [, v]) => sum + v, 0);
    const total = count + allRelated / 2;
    const normalizedRadius = Math.min((total / maxCount) * maxRadius, maxRadius);
    return getPoint(cat.angle, Math.max(normalizedRadius, 4));
  }).map(p => `${p.x},${p.y}`).join(' ');

  return (
    <div style={{
      position: 'absolute',
      top: 'var(--space-md)',
      left: 'var(--space-md)',
      width: '140px',
      height: '160px',
      zIndex: 10,
    }}>
      <div style={{
        fontSize: '8px',
        fontFamily: 'var(--font-mono)',
        color: 'var(--text-tertiary)',
        textTransform: 'uppercase',
        letterSpacing: '0.12em',
        marginBottom: '3px',
        display: 'flex',
        alignItems: 'center',
        gap: '4px',
      }}>
        <span style={{
          width: '5px', height: '5px', borderRadius: '50%',
          background: modeColor,
          boxShadow: `0 0 4px ${modeColor}`,
        }} />
        Radar // Threats
      </div>

      <svg width="130" height="130" viewBox="0 0 130 130">
        {[0.25, 0.5, 0.75, 1].map(r => (
          <circle key={r} cx={center} cy={center} r={maxRadius * r}
            fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="0.5" />
        ))}

        {ATTACK_CATEGORIES.map(cat => {
          const end = getPoint(cat.angle, maxRadius);
          return <line key={cat.key} x1={center} y1={center} x2={end.x} y2={end.y}
            stroke="rgba(255,255,255,0.05)" strokeWidth="0.5" />;
        })}

        {Object.keys(attackStats).length > 0 && (
          <polygon points={polygonPoints}
            fill="rgba(255, 45, 85, 0.12)" stroke="var(--threat-critical)" strokeWidth="1"
            style={{ filter: 'drop-shadow(0 0 3px rgba(255,45,85,0.25))' }} />
        )}

        <line x1={center} y1={center} x2={center} y2={center - maxRadius}
          stroke={modeColor} strokeWidth="1" opacity="0.35"
          style={{ transformOrigin: `${center}px ${center}px`, animation: 'radar-sweep 4s linear infinite' }} />

        <circle cx={center} cy={center} r="3" fill={modeColor} opacity="0.7">
          <animate attributeName="r" values="2;4;2" dur="2s" repeatCount="indefinite" />
          <animate attributeName="opacity" values="0.7;0.3;0.7" dur="2s" repeatCount="indefinite" />
        </circle>

        {ATTACK_CATEGORIES.map(cat => {
          const pos = getPoint(cat.angle, maxRadius + 12);
          return <text key={cat.key} x={pos.x} y={pos.y}
            textAnchor="middle" dominantBaseline="middle"
            fill="var(--text-tertiary)" fontSize="6" fontFamily="var(--font-mono)">
            {cat.label}
          </text>;
        })}

        {ATTACK_CATEGORIES.map(cat => {
          const count = attackStats[cat.key] || 0;
          if (count === 0) return null;
          const radius = Math.min((count / maxCount) * maxRadius, maxRadius);
          const pos = getPoint(cat.angle, radius);
          return <circle key={`b-${cat.key}`} cx={pos.x} cy={pos.y} r="3"
            fill="var(--threat-critical)" opacity="0.8">
            <animate attributeName="r" values="2;4;2" dur="1.5s" repeatCount="indefinite" />
          </circle>;
        })}
      </svg>

      <style>{`@keyframes radar-sweep { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
