import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { fetchDocChunks, fetchUrlChunks } from '../hooks/aegisApi';

export default function SourcesPanel({ documents, urls, loadSources }) {
  const [expandedDoc, setExpandedDoc] = useState(null);
  const [expandedUrl, setExpandedUrl] = useState(null);
  const [docChunks, setDocChunks] = useState({});
  const [urlChunks, setUrlChunks] = useState({});

  useEffect(() => {
    loadSources();
  }, [loadSources]);

  const toggleDoc = async (docId) => {
    if (expandedDoc === docId) {
      setExpandedDoc(null);
    } else {
      setExpandedDoc(docId);
      if (!docChunks[docId]) {
        const chunks = await fetchDocChunks(docId);
        setDocChunks(prev => ({ ...prev, [docId]: chunks }));
      }
    }
  };

  const toggleUrl = async (urlId) => {
    if (expandedUrl === urlId) {
      setExpandedUrl(null);
    } else {
      setExpandedUrl(urlId);
      if (!urlChunks[urlId]) {
        const chunks = await fetchUrlChunks(urlId);
        setUrlChunks(prev => ({ ...prev, [urlId]: chunks }));
      }
    }
  };

  return (
    <div className="sources-panel">
      <div className="section-header">
        <h4>Ingested Documents</h4>
        <span className="badge">{documents?.length || 0}</span>
      </div>
      <div className="sources-list documents-list">
        {documents?.slice(0, 10).map(doc => (
          <div key={doc.document_id} className={`source-item ${doc.overall_risk >= 0.8 ? 'danger' : ''}`}>
            <div className="source-header" onClick={() => toggleDoc(doc.document_id)} style={{ cursor: 'pointer', display: 'flex', justifyContent: 'space-between', padding: '0.5rem', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', marginBottom: '0.5rem' }}>
              <div>
                <span className="source-icon" style={{marginRight: '0.5rem'}}>📄</span>
                <span className="source-name">{doc.name || doc.document_id}</span>
              </div>
              {doc.suspicious_chunks_count > 0 && <span className="warning-badge" style={{color: '#ff4444', fontSize: '0.8rem'}}>{doc.suspicious_chunks_count} quarantined</span>}
            </div>
            <AnimatePresence>
              {expandedDoc === doc.document_id && (
                <motion.div initial={{height:0}} animate={{height:'auto'}} exit={{height:0}} className="source-chunks" style={{overflow:'hidden', paddingLeft: '1rem'}}>
                  {(docChunks[doc.document_id] || []).filter(c => c.quarantined).map(chunk => (
                    <div key={chunk.chunk_id} className="chunk quarant" style={{background: 'rgba(255,0,0,0.1)', borderLeft: '2px solid red', padding: '0.5rem', marginBottom:'0.5rem'}}>
                      <div className="chunk-meta" style={{fontSize:'0.75rem', color: '#ffaaaa', marginBottom:'0.25rem'}}>Quarantined • High Risk • {chunk.attack_type}</div>
                      <div className="chunk-text" style={{fontSize: '0.85rem'}}>{chunk.chunk_text}</div>
                    </div>
                  ))}
                  {(docChunks[doc.document_id] || []).filter(c => !c.quarantined).map(chunk => (
                    <div key={chunk.chunk_id} className="chunk safe" style={{background: 'rgba(255,255,255,0.02)', padding: '0.5rem', marginBottom:'0.5rem'}}>
                      <div className="chunk-meta" style={{fontSize:'0.75rem', opacity: 0.5}}>Safe</div>
                      <div className="chunk-text" style={{fontSize: '0.85rem', opacity: 0.8}}>{chunk.chunk_text.substring(0, 80)}...</div>
                    </div>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        ))}
        {documents?.length === 0 && <div className="empty-state" style={{opacity: 0.5, fontSize: '0.9rem', margin: '0.5rem 0'}}>No documents ingested</div>}
      </div>

      <div className="section-header" style={{ marginTop: '1.5rem' }}>
        <h4>Ingested URLs</h4>
        <span className="badge">{urls?.length || 0}</span>
      </div>
      <div className="sources-list urls-list">
        {urls?.slice(0, 10).map(url => (
          <div key={url.url_id} className={`source-item ${url.overall_risk >= 0.8 ? 'danger' : ''}`}>
            <div className="source-header" onClick={() => toggleUrl(url.url_id)} style={{ cursor: 'pointer', display: 'flex', justifyContent: 'space-between', padding: '0.5rem', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', marginBottom: '0.5rem' }}>
              <div>
                <span className="source-icon" style={{marginRight: '0.5rem'}}>🌐</span>
                <span className="source-name">{url.domain || url.url_id}</span>
              </div>
              {url.suspicious_chunks_count > 0 && <span className="warning-badge" style={{color: '#ff4444', fontSize: '0.8rem'}}>{url.suspicious_chunks_count} quarantined</span>}
            </div>
            <AnimatePresence>
              {expandedUrl === url.url_id && (
                <motion.div initial={{height:0}} animate={{height:'auto'}} exit={{height:0}} className="source-chunks" style={{overflow:'hidden', paddingLeft: '1rem'}}>
                   {(urlChunks[url.url_id] || []).filter(c => c.quarantined).map(chunk => (
                    <div key={chunk.chunk_id} className="chunk quarant" style={{background: 'rgba(255,0,0,0.1)', borderLeft: '2px solid red', padding: '0.5rem', marginBottom:'0.5rem'}}>
                      <div className="chunk-meta" style={{fontSize:'0.75rem', color: '#ffaaaa', marginBottom:'0.25rem'}}>Quarantined • High Risk • {chunk.attack_type}</div>
                      <div className="chunk-text" style={{fontSize: '0.85rem'}}>{chunk.chunk_text}</div>
                    </div>
                  ))}
                   {(urlChunks[url.url_id] || []).filter(c => !c.quarantined).map(chunk => (
                    <div key={chunk.chunk_id} className="chunk safe" style={{background: 'rgba(255,255,255,0.02)', padding: '0.5rem', marginBottom:'0.5rem'}}>
                      <div className="chunk-meta" style={{fontSize:'0.75rem', opacity: 0.5}}>Safe</div>
                      <div className="chunk-text" style={{fontSize: '0.85rem', opacity: 0.8}}>{chunk.chunk_text.substring(0, 80)}...</div>
                    </div>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        ))}
        {urls?.length === 0 && <div className="empty-state" style={{opacity: 0.5, fontSize: '0.9rem', margin: '0.5rem 0'}}>No URLs ingested</div>}
      </div>
    </div>
  );
}
