/**
 * AEGIS Phase 2 — REST API Client
 * 
 * Provides functions for fetching data from the backend REST API.
 * Used for historical incident retrieval and other non-realtime data needs.
 */

const API_BASE = '/v1';

/**
 * Fetch incidents from the backend.
 * 
 * @param {Object} params
 * @param {number} [params.limit=50] - Max incidents to return
 * @param {string} [params.decision] - Filter by decision (allow, sanitize, challenge, block)
 * @param {string} [params.attackType] - Filter by attack type
 * @param {number} [params.minRisk] - Minimum risk score (0.0 - 1.0)
 * @returns {Promise<{incidents: Array, total: number}>}
 */
export async function fetchIncidents({ limit = 50, decision, attackType, minRisk } = {}) {
  try {
    const params = new URLSearchParams();
    params.set('limit', String(limit));
    if (decision) params.set('decision', decision);
    if (attackType) params.set('attack_type', attackType);
    if (minRisk !== undefined && minRisk !== null) params.set('min_risk', String(minRisk));

    const response = await fetch(`${API_BASE}/incidents?${params.toString()}`);

    if (!response.ok) {
      console.warn(`[AEGIS API] Incidents fetch failed: ${response.status}`);
      return { incidents: [], total: 0 };
    }

    const data = await response.json();
    return {
      incidents: data.incidents || [],
      total: data.total || 0,
    };
  } catch (error) {
    console.warn('[AEGIS API] Incidents fetch error:', error);
    return { incidents: [], total: 0 };
  }
}

/**
 * Fetch backend health status.
 * 
 * @returns {Promise<{status: string, version: string} | null>}
 */
export async function fetchHealth() {
  try {
    const response = await fetch('/health');
    if (!response.ok) return null;
    return await response.json();
  } catch (error) {
    console.warn('[AEGIS API] Health fetch error:', error);
    return null;
  }
}

/**
 * Fetch backend readiness status.
 * 
 * @returns {Promise<Object | null>}
 */
export async function fetchReadiness() {
  try {
    const response = await fetch('/ready');
    if (!response.ok) return null;
    return await response.json();
  } catch (error) {
    console.warn('[AEGIS API] Readiness fetch error:', error);
    return null;
  }
}

export async function fetchDocuments({ tenantId = 'demo', limit = 50, offset = 0 } = {}) {
  try {
    const params = new URLSearchParams({ tenant_id: tenantId, limit, offset });
    const response = await fetch(`${API_BASE}/documents?${params.toString()}`);
    if (!response.ok) return [];
    return await response.json();
  } catch (error) {
    console.warn('[AEGIS API] Fetch documents error:', error);
    return [];
  }
}

export async function fetchUrls({ tenantId = 'demo', limit = 50, offset = 0 } = {}) {
  try {
    const params = new URLSearchParams({ tenant_id: tenantId, limit, offset });
    const response = await fetch(`${API_BASE}/urls?${params.toString()}`);
    if (!response.ok) return [];
    return await response.json();
  } catch (error) {
    console.warn('[AEGIS API] Fetch URLs error:', error);
    return [];
  }
}

export async function fetchDocChunks(documentId) {
  try {
    const response = await fetch(`${API_BASE}/documents/${documentId}/chunks`);
    if (!response.ok) return [];
    return await response.json();
  } catch (error) {
    console.warn('[AEGIS API] Fetch doc chunks error:', error);
    return [];
  }
}

export async function fetchUrlChunks(urlId) {
  try {
    const response = await fetch(`${API_BASE}/urls/${urlId}/chunks`);
    if (!response.ok) return [];
    return await response.json();
  } catch (error) {
    console.warn('[AEGIS API] Fetch URL chunks error:', error);
    return [];
  }
}

export async function proxyChat({ prompt, app_id = 'demo', provider = 'openai', model = 'gpt-4' }) {
  try {
    const response = await fetch(`${API_BASE}/proxy/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        request_id: `req_${Date.now()}`,
        tenant_id: 'demo',
        app_id,
        prompt,
        target: { provider, model }
      }),
    });
    return await response.json();
  } catch (error) {
    console.warn('[AEGIS API] Proxy chat error:', error);
    return null;
  }
}

export async function submitFeedback({ trace_id, label, reviewer_notes }) {
  try {
    const response = await fetch(`${API_BASE}/feedback/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ trace_id, label, reviewer_notes, reviewer: 'operator-1' })
    });
    return await response.json();
  } catch (error) {
    console.warn('[AEGIS API] Feedback post error:', error);
    return null;
  }
}

export async function fetchFeedbackMetrics() {
  try {
    const response = await fetch(`${API_BASE}/feedback/metrics`);
    if (!response.ok) return null;
    return await response.json();
  } catch (error) {
    console.warn('[AEGIS API] Feedback metrics error:', error);
    return null;
  }
}
