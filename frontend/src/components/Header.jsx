import React from 'react';

export default function Header({
  user,
  workspaces,
  currentWorkspace,
  onSelectWorkspace,
  usage,
  onUpgradeTier,
  onLogout
}) {
  const queryPercent = usage?.today?.queries_percent || 0;
  const queriesLeft = usage?.today?.queries_remaining ?? '--';
  const queryLimit = usage?.today?.queries_limit ?? '--';

  return (
    <header className="h-16 border-b border-[var(--border-subtle)] bg-[var(--bg-secondary)]/90 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-40">
      {/* Brand */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.875rem' }}>
        <div style={{
          width: '2.5rem',
          height: '2.5rem',
          borderRadius: '10px',
          background: 'linear-gradient(135deg, #6366f1 0%, #06b6d4 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 0 16px rgba(99, 102, 241, 0.4)'
        }}>
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
          </svg>
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <h1 style={{ fontSize: '1.1rem', fontWeight: 700, letterSpacing: '-0.02em', color: '#fff' }}>FalconXoft AI</h1>
            <span className="badge badge-indigo">SaaS Workspace</span>
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Document-Grounded RAG & Tenant Isolation</p>
        </div>
      </div>

      {/* Center: Workspace Selector */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Workspace:</span>
        <select
          id="workspace-selector"
          value={currentWorkspace?.id || ''}
          onChange={(e) => {
            const list = Array.isArray(workspaces) ? workspaces : [];
            const ws = list.find(w => w.id === e.target.value);
            if (ws) onSelectWorkspace(ws);
          }}
          style={{
            background: 'rgba(15, 20, 34, 0.9)',
            border: '1px solid var(--border-subtle)',
            color: 'var(--text-main)',
            padding: '0.45rem 1rem',
            borderRadius: '8px',
            fontSize: '0.85rem',
            fontWeight: 500,
            cursor: 'pointer',
            outline: 'none'
          }}
        >
          {(Array.isArray(workspaces) ? workspaces : []).map(ws => (
            <option key={ws.id} value={ws.id}>
              {ws.name} ({ws.role || 'Member'})
            </option>
          ))}
        </select>
      </div>

      {/* Right: Quota Meter & User Profile */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
        {/* Real-time Quota Capsule */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.04)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '9999px',
          padding: '0.35rem 0.85rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem'
        }}>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.5rem' }}>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Daily Queries</span>
              <span style={{ fontSize: '0.72rem', fontWeight: 600, color: queryPercent >= 90 ? 'var(--accent-rose)' : 'var(--accent-cyan)' }}>
                {queriesLeft} left / {queryLimit}
              </span>
            </div>
            <div style={{ width: '110px', height: '4px', background: 'rgba(255, 255, 255, 0.1)', borderRadius: '2px', overflow: 'hidden', marginTop: '3px' }}>
              <div style={{
                width: `${queryPercent}%`,
                height: '100%',
                background: queryPercent >= 90 ? 'var(--accent-rose)' : 'linear-gradient(90deg, #6366f1, #06b6d4)',
                transition: 'width 0.4s ease'
              }} />
            </div>
          </div>
          <span className={`badge ${user?.tier === 'ENTERPRISE' ? 'badge-indigo' : user?.tier === 'PRO' ? 'badge-emerald' : 'badge-amber'}`}>
            {user?.tier || 'FREE'}
          </span>
        </div>

        {/* Tier Upgrade Quick Action */}
        {user?.tier === 'FREE' && (
          <button
            id="upgrade-tier-btn"
            onClick={() => onUpgradeTier('PRO')}
            style={{
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              color: 'white',
              fontSize: '0.78rem',
              fontWeight: 600,
              padding: '0.4rem 0.85rem',
              borderRadius: '6px',
              border: 'none',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem'
            }}
          >
            ⚡ Upgrade to Pro
          </button>
        )}

        {/* Swagger Docs Link */}
        <a
          href="/api/docs/"
          target="_blank"
          rel="noreferrer"
          style={{
            fontSize: '0.8rem',
            color: 'var(--text-muted)',
            textDecoration: 'none',
            display: 'flex',
            alignItems: 'center',
            gap: '0.3rem',
            padding: '0.4rem 0.6rem',
            borderRadius: '6px',
            border: '1px solid var(--border-subtle)',
            background: 'rgba(255, 255, 255, 0.02)'
          }}
        >
          API Docs ↗
        </a>

        {/* User Card */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <div style={{
            width: '2rem',
            height: '2rem',
            borderRadius: '50%',
            background: '#6366f1',
            color: 'white',
            fontWeight: 700,
            fontSize: '0.85rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            {(user?.username || 'U')[0].toUpperCase()}
          </div>
          <button
            id="logout-btn"
            onClick={onLogout}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-dim)',
              fontSize: '0.78rem',
              cursor: 'pointer',
              padding: '0.2rem'
            }}
            title="Log Out"
          >
            Sign Out
          </button>
        </div>
      </div>
    </header>
  );
}
