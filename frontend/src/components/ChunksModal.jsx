import React from 'react';

export default function ChunksModal({ document, chunks, onClose }) {
  if (!document) return null;

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(0, 0, 0, 0.75)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 50,
      padding: '1.5rem'
    }}>
      <div className="glass-panel" style={{
        width: '100%',
        maxWidth: '750px',
        maxHeight: '85vh',
        display: 'flex',
        flexDirection: 'column',
        background: '#0d121f',
        border: '1px solid rgba(255, 255, 255, 0.12)',
        overflow: 'hidden'
      }}>
        {/* Header */}
        <div style={{
          padding: '1.25rem 1.5rem',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff' }}>
              Document Chunks & Vector Embeddings
            </h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Source: <span style={{ color: 'var(--accent-cyan)' }}>{document.file_name}</span> ({chunks.length} chunks indexed)
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'rgba(255, 255, 255, 0.05)',
              border: 'none',
              color: 'var(--text-muted)',
              borderRadius: '6px',
              padding: '0.4rem 0.75rem',
              cursor: 'pointer',
              fontSize: '0.9rem'
            }}
          >
            ✕ Close
          </button>
        </div>

        {/* Chunks List */}
        <div style={{ padding: '1.25rem 1.5rem', overflowY: 'auto', flex: 1, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {chunks.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>No chunks found for this document.</p>
          ) : (
            chunks.map(chunk => (
              <div key={chunk.id} style={{
                background: 'rgba(255, 255, 255, 0.03)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '8px',
                padding: '1rem'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span className="badge badge-indigo">Chunk #{chunk.chunk_index + 1}</span>
                    {chunk.page_number && (
                      <span className="badge badge-amber">Page {chunk.page_number}</span>
                    )}
                  </div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
                    {chunk.token_count} tokens
                  </span>
                </div>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-main)', lineHeight: 1.5, whiteSpace: 'pre-wrap' }}>
                  {chunk.content}
                </p>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
