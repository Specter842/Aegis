import { motion } from 'framer-motion';

export default function ResponseDiffView({ proxyResult }) {
  if (!proxyResult || !proxyResult.output_scan) return null;

  const { output_scan, model_response } = proxyResult;
  const action = output_scan.action || 'allow';
  const isBlocked = output_scan.blocked;

  return (
    <div style={{ padding: '10px', background: 'var(--bg-panel)', borderRadius: 'var(--radius-md)' }}>
      <h4 style={{ margin: '0 0 10px 0', fontSize: '12px', color: 'var(--text-secondary)' }}>Response Integrity Diff</h4>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
        <div style={{ border: '1px solid rgba(255,159,10,0.3)', borderRadius: '4px', padding: '8px', background: 'rgba(255,159,10,0.05)' }}>
          <div style={{ fontSize: '9px', color: 'var(--threat-warning)', marginBottom: '4px' }}>Safe Excerpt (Backend Preview)</div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', opacity: 0.8, wordBreak: 'break-word', whiteSpace: 'pre-wrap' }}>
            {output_scan.safe_excerpt || "<No valid safe excerpt provided>"}
          </div>
        </div>

        <div style={{ border: `1px solid ${isBlocked ? 'rgba(255,45,85,0.3)' : 'rgba(48,209,88,0.3)'}`, borderRadius: '4px', padding: '8px', background: isBlocked ? 'rgba(255,45,85,0.05)' : 'rgba(48,209,88,0.05)' }}>
          <div style={{ fontSize: '9px', color: isBlocked ? 'var(--threat-critical)' : 'var(--threat-safe)', marginBottom: '4px' }}>Final Delivered Content</div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', wordBreak: 'break-word', whiteSpace: 'pre-wrap' }}>
            {isBlocked ? "<Blocked securely at egress>" : (model_response?.content)}
          </div>
        </div>
      </div>
      
      {action !== 'allow' && (
        <div style={{ marginTop: '10px', fontSize: '9px', color: 'var(--text-tertiary)' }}>
          Changes Applied: 
          <span style={{ color: 'var(--mode-accent)', marginLeft: '4px', fontWeight: 'bold' }}>{action.toUpperCase()}</span>
        </div>
      )}
    </div>
  );
}
