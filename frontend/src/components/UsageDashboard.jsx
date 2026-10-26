import React, { useState } from 'react';

export default function UsageDashboard({
  usage,
  requestHistory,
  onSimulateQuota,
  onUpgradeTier
}) {
  const [testingStatus, setTestingStatus] = useState('');

  const today = usage?.today || {};
  const queryPercent = today.queries_percent || 0;
  const tokenPercent = today.tokens_percent || 0;

  const handleSimulate = async (action) => {
    try {
      setTestingStatus('Simulating quota state...');
      await onSimulateQuota(action);
      setTestingStatus(action === 'exhaust' ? 'Quota marked as EXHAUSTED (Queries at limit).' : 'Quota RESET to 0.');
      setTimeout(() => setTestingStatus(''), 4000);
    } catch (e) {
      setTestingStatus(`Error: ${e.message}`);
    }
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '1150px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Title */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#fff', letterSpacing: '-0.02em' }}>
            Usage Analytics & Quota Governance
          </h2>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            Per-user consumption metrics, sliding-window rate limit telemetry, and immutable audit logs.
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span className="badge badge-indigo">Daily Reset: 00:00 UTC</span>
        </div>
      </div>

      {/* Quota KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.25rem' }}>
        {/* Tier Card */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase' }}>
            Subscription Tier
          </span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', margin: '0.6rem 0' }}>
            <h3 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#fff' }}>
              {usage?.tier || 'FREE'}
            </h3>
            <span className={`badge ${usage?.tier === 'ENTERPRISE' ? 'badge-indigo' : usage?.tier === 'PRO' ? 'badge-emerald' : 'badge-amber'}`}>
              Active
            </span>
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Rate Limit: {usage?.quota?.rate_limit_per_minute || 20} req/min
          </p>
          <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
            <button
              onClick={() => onUpgradeTier('FREE')}
              style={{
                flex: 1,
                padding: '0.35rem 0.5rem',
                borderRadius: '6px',
                border: '1px solid var(--border-subtle)',
                background: usage?.tier === 'FREE' ? 'rgba(255, 255, 255, 0.12)' : 'transparent',
                color: '#fff',
                fontSize: '0.75rem',
                cursor: 'pointer'
              }}
            >
              Free
            </button>
            <button
              onClick={() => onUpgradeTier('PRO')}
              style={{
                flex: 1,
                padding: '0.35rem 0.5rem',
                borderRadius: '6px',
                border: '1px solid var(--border-subtle)',
                background: usage?.tier === 'PRO' ? 'rgba(16, 185, 129, 0.2)' : 'transparent',
                color: '#fff',
                fontSize: '0.75rem',
                cursor: 'pointer'
              }}
            >
              Pro
            </button>
            <button
              onClick={() => onUpgradeTier('ENTERPRISE')}
              style={{
                flex: 1,
                padding: '0.35rem 0.5rem',
                borderRadius: '6px',
                border: '1px solid var(--border-subtle)',
                background: usage?.tier === 'ENTERPRISE' ? 'rgba(99, 102, 241, 0.2)' : 'transparent',
                color: '#fff',
                fontSize: '0.75rem',
                cursor: 'pointer'
              }}
            >
              Enterprise
            </button>
          </div>
        </div>

        {/* Query Quota Card */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase' }}>
              Daily Query Budget
            </span>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: queryPercent >= 90 ? 'var(--accent-rose)' : 'var(--accent-cyan)' }}>
              {queryPercent}%
            </span>
          </div>
          <div style={{ margin: '0.6rem 0' }}>
            <h3 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#fff' }}>
              {today.queries_used || 0} <span style={{ fontSize: '1rem', color: 'var(--text-dim)', fontWeight: 500 }}>/ {today.queries_limit || 0}</span>
            </h3>
          </div>
          <div style={{ width: '100%', height: '6px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '3px', overflow: 'hidden' }}>
            <div style={{
              width: `${queryPercent}%`,
              height: '100%',
              background: queryPercent >= 90 ? 'var(--accent-rose)' : 'linear-gradient(90deg, #6366f1, #06b6d4)',
              transition: 'width 0.4s ease'
            }} />
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.75rem' }}>
            Remaining today: <strong style={{ color: '#fff' }}>{today.queries_remaining || 0} queries</strong>
          </p>
        </div>

        {/* Token Budget Card */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase' }}>
              Daily Token Window
            </span>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: tokenPercent >= 90 ? 'var(--accent-rose)' : 'var(--accent-emerald)' }}>
              {tokenPercent}%
            </span>
          </div>
          <div style={{ margin: '0.6rem 0' }}>
            <h3 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#fff' }}>
              {today.tokens_used?.toLocaleString() || 0} <span style={{ fontSize: '1rem', color: 'var(--text-dim)', fontWeight: 500 }}>/ {today.tokens_limit?.toLocaleString() || 0}</span>
            </h3>
          </div>
          <div style={{ width: '100%', height: '6px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '3px', overflow: 'hidden' }}>
            <div style={{
              width: `${tokenPercent}%`,
              height: '100%',
              background: tokenPercent >= 90 ? 'var(--accent-rose)' : 'linear-gradient(90deg, #10b981, #06b6d4)',
              transition: 'width 0.4s ease'
            }} />
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.75rem' }}>
            Remaining today: <strong style={{ color: '#fff' }}>{today.tokens_remaining?.toLocaleString() || 0} tokens</strong>
          </p>
        </div>
      </div>

      {/* Developer QA Testing Panel */}
      <div className="glass-panel" style={{ padding: '1.25rem 1.5rem', background: 'rgba(99, 102, 241, 0.04)', border: '1px solid rgba(99, 102, 241, 0.2)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span>🧪</span> Developer QA Simulation Controls (Section 2 Requirement)
            </h4>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
              Instantly toggle quota state to verify HTTP 429 Too Many Requests edge cases and recovery handling.
            </p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <button
              id="simulate-exhaust-btn"
              onClick={() => handleSimulate('exhaust')}
              style={{
                background: 'rgba(244, 63, 94, 0.15)',
                border: '1px solid rgba(244, 63, 94, 0.35)',
                color: '#f87171',
                padding: '0.45rem 0.9rem',
                borderRadius: '6px',
                fontSize: '0.8rem',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              Simulate Quota Limit (Trigger 429)
            </button>
            <button
              id="simulate-reset-btn"
              onClick={() => handleSimulate('reset')}
              style={{
                background: 'rgba(16, 185, 129, 0.15)',
                border: '1px solid rgba(16, 185, 129, 0.35)',
                color: '#34d399',
                padding: '0.45rem 0.9rem',
                borderRadius: '6px',
                fontSize: '0.8rem',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              Reset Quota to Zero
            </button>
          </div>
        </div>
        {testingStatus && (
          <p style={{ marginTop: '0.6rem', fontSize: '0.78rem', color: 'var(--accent-cyan)', fontWeight: 500 }}>
            {testingStatus}
          </p>
        )}
      </div>

      {/* 7-Day Trend Chart */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#fff', marginBottom: '1.25rem' }}>
          7-Day Activity & Token Consumption Velocity
        </h3>
        <div style={{ display: 'flex', alignItems: 'flex-end', gap: '1rem', height: '140px', paddingBottom: '0.5rem' }}>
          {(usage?.daily_trend || []).map((t, i) => {
            const barHeight = Math.max(12, Math.min(130, (t.queries / (today.queries_limit || 25)) * 130));
            return (
              <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.4rem' }}>
                <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>{t.queries}q</span>
                <div style={{
                  width: '100%',
                  height: `${barHeight}px`,
                  background: 'linear-gradient(180deg, #6366f1 0%, rgba(99, 102, 241, 0.2) 100%)',
                  borderRadius: '6px 6px 2px 2px',
                  transition: 'height 0.3s ease'
                }} />
                <span style={{ fontSize: '0.65rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
                  {t.date.substring(5)}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="glass-panel" style={{ overflow: 'hidden' }}>
        <div style={{ padding: '1rem 1.5rem', borderBottom: '1px solid var(--border-subtle)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#fff' }}>
            Live Security & API Request Audit Logs
          </h3>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
            Last 50 recorded calls
          </span>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.82rem' }}>
            <thead>
              <tr style={{ background: 'rgba(255, 255, 255, 0.02)', borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-dim)', fontSize: '0.72rem', textTransform: 'uppercase' }}>
                <th style={{ padding: '0.75rem 1.25rem' }}>Method & Route</th>
                <th style={{ padding: '0.75rem 1rem' }}>Status</th>
                <th style={{ padding: '0.75rem 1rem' }}>Latency</th>
                <th style={{ padding: '0.75rem 1rem' }}>Tokens</th>
                <th style={{ padding: '0.75rem 1rem' }}>IP Address</th>
                <th style={{ padding: '0.75rem 1.25rem', textAlign: 'right' }}>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {requestHistory.length === 0 ? (
                <tr>
                  <td colSpan="6" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                    No request logs recorded yet.
                  </td>
                </tr>
              ) : (
                requestHistory.slice(0, 15).map(log => (
                  <tr key={log.id} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                    <td style={{ padding: '0.75rem 1.25rem', fontFamily: 'var(--font-mono)', color: '#fff' }}>
                      <span style={{ color: log.method === 'POST' ? 'var(--accent-primary)' : 'var(--accent-cyan)', fontWeight: 700, marginRight: '0.5rem' }}>
                        {log.method}
                      </span>
                      <span>{log.endpoint}</span>
                    </td>
                    <td style={{ padding: '0.75rem 1rem' }}>
                      <span className={`badge ${log.status_code >= 400 ? 'badge-rose' : 'badge-emerald'}`} style={{ fontSize: '0.65rem' }}>
                        {log.status_code}
                      </span>
                    </td>
                    <td style={{ padding: '0.75rem 1rem', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                      {log.latency_ms} ms
                    </td>
                    <td style={{ padding: '0.75rem 1rem', fontFamily: 'var(--font-mono)', color: 'var(--text-dim)' }}>
                      {log.tokens_consumed || 0}
                    </td>
                    <td style={{ padding: '0.75rem 1rem', color: 'var(--text-dim)' }}>
                      {log.ip_address || '127.0.0.1'}
                    </td>
                    <td style={{ padding: '0.75rem 1.25rem', textAlign: 'right', color: 'var(--text-dim)', fontSize: '0.75rem' }}>
                      {new Date(log.created_at).toLocaleTimeString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
