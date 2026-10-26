import React from 'react';

export default function ArchitectureView() {
  return (
    <div style={{ padding: '2rem', maxWidth: '1150px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Header */}
      <div>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#fff', letterSpacing: '-0.02em' }}>
          System Architecture & Technical Specifications
        </h2>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
          Interactive architecture breakdown, security trust boundaries, RAG pipeline flow, and scaling benchmarks.
        </p>
      </div>

      {/* Grid of Key Subsystems */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1.25rem' }}>
        {/* Component 1 */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
            <span style={{ fontSize: '1.2rem' }}>🛡️</span>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#fff' }}>
              Multi-Tenant Data Isolation
            </h3>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
            Every document, chunk, vector embedding, and chat session is strictly partitioned by foreign key relation to <code style={{ color: 'var(--accent-cyan)' }}>workspace_id</code>. Cross-tenant leakage is eliminated through database foreign key constraints, ORM filtering, and Django permission guards.
          </p>
        </div>

        {/* Component 2 */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
            <span style={{ fontSize: '1.2rem' }}>🔍</span>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#fff' }}>
              Deterministic Grounded RAG & Fallbacks
            </h3>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
            Queries pass through a cosine semantic retriever with keyword boosting. If top chunk similarity falls below threshold (<code style={{ color: 'var(--accent-amber)' }}>&lt; 0.20</code>), the system cleanly triggers an <strong>Unsupported Query Refusal</strong> with zero hallucinations. Includes prompt injection guardrails.
          </p>
        </div>

        {/* Component 3 */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
            <span style={{ fontSize: '1.2rem' }}>⚡</span>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#fff' }}>
              Sliding-Window Rate Limiting & Quotas
            </h3>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
            Enforces per-tier query budgets (Free: 30/day, Pro: 500/day, Enterprise: 10,000/day). Middleware tracks 60-second sliding-window request rates and responds with <code style={{ color: 'var(--accent-rose)' }}>HTTP 429 Too Many Requests</code> with <code style={{ color: 'var(--accent-rose)' }}>Retry-After</code> headers.
          </p>
        </div>

        {/* Component 4 */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
            <span style={{ fontSize: '1.2rem' }}>💾</span>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#fff' }}>
              Storage Deduplication & SHA-256
            </h3>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
            Every file upload computes a 256-bit cryptographic digest. Duplicate files uploaded within the same tenant workspace are identified instantly, preventing redundant chunk storage, saving vector compute costs, and ensuring byte-level integrity.
          </p>
        </div>
      </div>

      {/* RAG Sequence Visualizer */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff', marginBottom: '1rem' }}>
          End-to-End RAG Execution Flow
        </h3>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(5, 1fr)',
          gap: '0.75rem',
          textAlign: 'center'
        }}>
          {[
            { step: '1. Ingest & Chunk', desc: 'File parsed, chunked into 400-tok segments with 50-tok overlap.' },
            { step: '2. Vector Embed', desc: 'Embeddings indexed in PostgreSQL with SHA-256 deduplication.' },
            { step: '3. Query Sanitize', desc: 'Adversarial prompt injection scan + sliding rate-limit check.' },
            { step: '4. Semantic Search', desc: 'Cosine similarity match within workspace boundaries.' },
            { step: '5. Grounded Cite', desc: 'Extracts exact citations, page numbers, and returns response.' }
          ].map((s, idx) => (
            <div key={idx} style={{
              background: 'rgba(255, 255, 255, 0.03)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '8px',
              padding: '1rem 0.75rem'
            }}>
              <span className="badge badge-indigo" style={{ fontSize: '0.7rem', marginBottom: '0.5rem' }}>
                {s.step}
              </span>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                {s.desc}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Scaling Capacity Overview */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff', marginBottom: '1rem' }}>
          Horizontal Scaling & Capacity Roadmap
        </h3>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem', textAlign: 'left' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-dim)', fontSize: '0.75rem' }}>
                <th style={{ padding: '0.75rem' }}>Scale Level</th>
                <th style={{ padding: '0.75rem' }}>Compute Strategy</th>
                <th style={{ padding: '0.75rem' }}>Database Capacity</th>
                <th style={{ padding: '0.75rem' }}>Caching & Queues</th>
                <th style={{ padding: '0.75rem' }}>Estimated Cost</th>
              </tr>
            </thead>
            <tbody>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                <td style={{ padding: '0.75rem', fontWeight: 600, color: '#fff' }}>100 Users</td>
                <td style={{ padding: '0.75rem', color: 'var(--text-muted)' }}>Single VPS (2 vCPU / 4GB RAM)</td>
                <td style={{ padding: '0.75rem', color: 'var(--text-muted)' }}>Local PostgreSQL 18 (20GB SSD)</td>
                <td style={{ padding: '0.75rem', color: 'var(--text-muted)' }}>In-memory cache + Celery</td>
                <td style={{ padding: '0.75rem', color: 'var(--accent-emerald)', fontWeight: 600 }}>$12 / mo</td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                <td style={{ padding: '0.75rem', fontWeight: 600, color: '#fff' }}>1,000 Users</td>
                <td style={{ padding: '0.75rem', color: 'var(--text-muted)' }}>Dual VPS + Nginx load balancer</td>
                <td style={{ padding: '0.75rem', color: 'var(--text-muted)' }}>Managed Postgres (4 vCPU / 16GB)</td>
                <td style={{ padding: '0.75rem', color: 'var(--text-muted)' }}>Redis Cluster for rate limiting</td>
                <td style={{ padding: '0.75rem', color: 'var(--accent-emerald)', fontWeight: 600 }}>$85 / mo</td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                <td style={{ padding: '0.75rem', fontWeight: 600, color: '#fff' }}>10,000 Users</td>
                <td style={{ padding: '0.75rem', color: 'var(--text-muted)' }}>AWS ECS Fargate (4-12 tasks auto-scaled)</td>
                <td style={{ padding: '0.75rem', color: 'var(--text-muted)' }}>RDS Multi-AZ Aurora Postgres</td>
                <td style={{ padding: '0.75rem', color: 'var(--text-muted)' }}>AWS ElastiCache Redis + SQS</td>
                <td style={{ padding: '0.75rem', color: 'var(--accent-cyan)', fontWeight: 600 }}>$540 / mo</td>
              </tr>
              <tr>
                <td style={{ padding: '0.75rem', fontWeight: 600, color: '#fff' }}>1,000,000 Users</td>
                <td style={{ padding: '0.75rem', color: 'var(--text-muted)' }}>EKS Kubernetes multi-region cluster</td>
                <td style={{ padding: '0.75rem', color: 'var(--text-muted)' }}>Aurora Serverless v2 + Read Replicas</td>
                <td style={{ padding: '0.75rem', color: 'var(--text-muted)' }}>Global Redis Mesh + CloudFront CDN</td>
                <td style={{ padding: '0.75rem', color: 'var(--accent-amber)', fontWeight: 600 }}>$8,420 / mo</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
