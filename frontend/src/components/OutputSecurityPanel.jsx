import { motion } from 'framer-motion';
import { useState } from 'react';
import { submitFeedback } from '../hooks/aegisApi';

export default function OutputSecurityPanel({ proxyResult }) {
  if (!proxyResult || !proxyResult.llm_called) return null;

  const { output_scan, model_response, target } = proxyResult;
  const isBlocked = output_scan?.blocked;
  const isLeaked = output_scan?.canary_leaked;
  const isPii = output_scan?.pii_detected;
  const action = output_scan?.action || 'allow'; // allow, redact, truncate, block

  const [feedbackLabel, setFeedbackLabel] = useState('true_positive');
  const [feedbackSent, setFeedbackSent] = useState(false);

  const handleFeedback = async () => {
    await submitFeedback({ trace_id: proxyResult.trace_id, label: feedbackLabel });
    setFeedbackSent(true);
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`glass-panel ${isBlocked ? 'glass-panel--danger' : ''}`}
      style={{ padding: 'var(--space-md)', marginBottom: 'var(--space-md)' }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <div style={{ fontSize: '10px', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Output Security Profile
        </div>
        <div className="badge badge--info" style={{ fontSize: '9px' }}>
          {target?.provider} / {target?.model}
        </div>
      </div>

      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '12px' }}>
        <div className={`badge ${isBlocked ? 'badge--critical' : (action !== 'allow' ? 'badge--warning' : 'badge--safe')}`}>
          Action: {action.toUpperCase()}
        </div>
        
        <div className="badge badge--default">
           Risk: {output_scan?.risk_score || 0}%
        </div>

        {isLeaked && (
           <div className="badge badge--critical">🚨 Protected Context Leaked</div>
        )}
        
        {isPii && (
           <div className="badge badge--warning">👁️ PII Detected</div>
        )}

        {output_scan?.block_reason && (
           <div className="badge badge--default" style={{ borderColor: 'var(--threat-critical)' }}>
             Reason: {output_scan.block_reason}
           </div>
        )}
      </div>

      <div style={{ background: 'var(--bg-secondary)', padding: '10px', borderRadius: '4px', border: '1px solid var(--border-subtle)', fontSize: '11px', fontFamily: 'var(--font-mono)' }}>
        <div style={{ color: 'var(--text-tertiary)', marginBottom: '4px', fontSize: '9px' }}>Final Response Delivered:</div>
        <div style={{ color: isBlocked ? 'var(--threat-critical)' : 'var(--text-primary)', wordBreak: 'break-word', whiteSpace: 'pre-wrap' }}>
          {isBlocked ? "<Response completely blocked>" : (model_response?.content || "(No response)")}
        </div>
      </div>

      <div style={{ marginTop: '14px', paddingTop: '10px', borderTop: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ fontSize: '9px', color: 'var(--text-secondary)' }}>Review Assessment:</div>
        {!feedbackSent ? (
          <div style={{ display: 'flex', gap: '6px' }}>
            <select 
              value={feedbackLabel} 
              onChange={e => setFeedbackLabel(e.target.value)}
              style={{ fontSize: '9px', padding: '2px 4px', background: 'var(--bg-panel)', color: 'var(--text-primary)', border: '1px solid var(--border-subtle)' }}
            >
              <option value="true_positive">True Positive</option>
              <option value="false_positive">False Positive</option>
              <option value="false_negative">False Negative</option>
              <option value="needs_review">Needs Review</option>
            </select>
            <button onClick={handleFeedback} className="btn btn--primary" style={{ fontSize: '9px', padding: '2px 8px' }}>
              Submit
            </button>
          </div>
        ) : (
          <div style={{ fontSize: '9px', color: 'var(--threat-safe)' }}>✓ Feedback Recorded</div>
        )}
      </div>
    </motion.div>
  );
}
