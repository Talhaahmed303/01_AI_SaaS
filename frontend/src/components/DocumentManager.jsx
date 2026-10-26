import React, { useState, useRef } from 'react';

export default function DocumentManager({
  documents,
  currentWorkspace,
  onUpload,
  onDelete,
  onViewChunks,
  isUploading
}) {
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      onUpload(e.target.files[0]);
    }
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '1100px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Title & Description */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#fff', letterSpacing: '-0.02em' }}>
              Document Repository & Studio
            </h2>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
              Upload and manage enterprise knowledge files. Documents are automatically chunked, embedded, and isolated to <strong style={{ color: 'var(--accent-cyan)' }}>{currentWorkspace?.name}</strong>.
            </p>
          </div>
          <span className="badge badge-emerald">
            {documents.length} Indexed Files
          </span>
        </div>
      </div>

      {/* Upload Dropzone */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        style={{
          border: `2px dashed ${dragActive ? 'var(--accent-primary)' : 'rgba(255, 255, 255, 0.15)'}`,
          background: dragActive ? 'rgba(99, 102, 241, 0.08)' : 'rgba(15, 20, 34, 0.5)',
          borderRadius: '14px',
          padding: '2.5rem 1.5rem',
          textAlign: 'center',
          cursor: isUploading ? 'not-allowed' : 'pointer',
          transition: 'all 0.2s ease',
          boxShadow: dragActive ? '0 0 25px rgba(99, 102, 241, 0.2)' : 'none'
        }}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.txt,.md,.markdown"
          style={{ display: 'none' }}
          onChange={handleFileChange}
          disabled={isUploading}
        />
        <div style={{
          width: '3rem',
          height: '3rem',
          borderRadius: '12px',
          background: 'rgba(99, 102, 241, 0.15)',
          color: 'var(--accent-primary)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 1rem auto'
        }}>
          {isUploading ? (
            <span style={{ animation: 'spin 1s linear infinite' }}>⏳</span>
          ) : (
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="17 8 12 3 7 8"/>
              <line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
          )}
        </div>
        <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: '#fff' }}>
          {isUploading ? 'Extracting, Chunking & Embedding Document...' : 'Click or drag files here to upload'}
        </h3>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-dim)', marginTop: '0.4rem' }}>
          Supported Formats: PDF, DOCX, TXT, Markdown (Max file size: 10 MB per document)
        </p>
      </div>

      {/* Documents Table */}
      <div className="glass-panel" style={{ overflow: 'hidden' }}>
        <div style={{ padding: '1rem 1.5rem', borderBottom: '1px solid var(--border-subtle)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#fff' }}>
            Active Workspace Knowledge Base
          </h3>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
            SHA-256 Verified Storage
          </span>
        </div>

        {documents.length === 0 ? (
          <div style={{ padding: '3rem 1.5rem', textAlign: 'center', color: 'var(--text-muted)' }}>
            <p style={{ fontSize: '0.9rem' }}>No documents uploaded yet in this workspace.</p>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-dim)', marginTop: '0.3rem' }}>
              Upload your technical specifications, policies, or contracts above to ground your AI assistant!
            </p>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ background: 'rgba(255, 255, 255, 0.02)', borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-dim)', fontSize: '0.75rem', textTransform: 'uppercase' }}>
                  <th style={{ padding: '0.85rem 1.25rem' }}>Document Name</th>
                  <th style={{ padding: '0.85rem 1rem' }}>Size</th>
                  <th style={{ padding: '0.85rem 1rem' }}>Chunks</th>
                  <th style={{ padding: '0.85rem 1rem' }}>Tokens</th>
                  <th style={{ padding: '0.85rem 1rem' }}>Status</th>
                  <th style={{ padding: '0.85rem 1rem' }}>SHA-256 Hash</th>
                  <th style={{ padding: '0.85rem 1.25rem', textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {documents.map(doc => (
                  <tr key={doc.id} style={{ borderBottom: '1px solid var(--border-subtle)', transition: 'background 0.15s ease' }}>
                    <td style={{ padding: '1rem 1.25rem', fontWeight: 600, color: '#fff' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                        <span style={{ color: 'var(--accent-primary)' }}>📄</span>
                        <span>{doc.file_name}</span>
                      </div>
                    </td>
                    <td style={{ padding: '1rem 1rem', color: 'var(--text-muted)' }}>
                      {doc.file_size_formatted || `${Math.round(doc.file_size / 1024)} KB`}
                    </td>
                    <td style={{ padding: '1rem 1rem' }}>
                      <span className="badge badge-indigo">{doc.chunk_count} chunks</span>
                    </td>
                    <td style={{ padding: '1rem 1rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                      {doc.total_tokens}
                    </td>
                    <td style={{ padding: '1rem 1rem' }}>
                      <span className={`badge ${doc.status === 'INDEXED' ? 'badge-emerald' : doc.status === 'FAILED' ? 'badge-rose' : 'badge-amber'}`}>
                        {doc.status}
                      </span>
                    </td>
                    <td style={{ padding: '1rem 1rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>
                      {doc.file_hash ? `${doc.file_hash.substring(0, 8)}...${doc.file_hash.substring(56)}` : 'N/A'}
                    </td>
                    <td style={{ padding: '1rem 1.25rem', textAlign: 'right' }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '0.5rem' }}>
                        <button
                          onClick={() => onViewChunks(doc)}
                          style={{
                            background: 'rgba(99, 102, 241, 0.12)',
                            color: '#a5b4fc',
                            border: '1px solid rgba(99, 102, 241, 0.25)',
                            padding: '0.35rem 0.65rem',
                            borderRadius: '6px',
                            fontSize: '0.75rem',
                            fontWeight: 500,
                            cursor: 'pointer'
                          }}
                        >
                          View Chunks
                        </button>
                        <button
                          onClick={() => onDelete(doc.id)}
                          style={{
                            background: 'rgba(244, 63, 94, 0.1)',
                            color: '#fda4af',
                            border: '1px solid rgba(244, 63, 94, 0.25)',
                            padding: '0.35rem 0.65rem',
                            borderRadius: '6px',
                            fontSize: '0.75rem',
                            fontWeight: 500,
                            cursor: 'pointer'
                          }}
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
