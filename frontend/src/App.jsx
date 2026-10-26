import React, { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import ChatInterface from './components/ChatInterface';
import DocumentManager from './components/DocumentManager';
import UsageDashboard from './components/UsageDashboard';
import ArchitectureView from './components/ArchitectureView';
import ChunksModal from './components/ChunksModal';
import LoginModal from './components/LoginModal';
import { api } from './services/api';

export default function App() {
  const [user, setUser] = useState(null);
  const [workspaces, setWorkspaces] = useState([]);
  const [currentWorkspace, setCurrentWorkspace] = useState(null);
  const [activeTab, setActiveTab] = useState('chat');

  // Documents
  const [documents, setDocuments] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [inspectingDoc, setInspectingDoc] = useState(null);
  const [docChunks, setDocChunks] = useState([]);

  // Chat & RAG
  const [chatSessions, setChatSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isAsking, setIsAsking] = useState(false);
  const [quotaError, setQuotaError] = useState(null);

  // Usage & Quotas
  const [usage, setUsage] = useState(null);
  const [requestHistory, setRequestHistory] = useState([]);

  // Modals
  const [showNewWorkspaceModal, setShowNewWorkspaceModal] = useState(false);
  const [newWorkspaceName, setNewWorkspaceName] = useState('');
  const [newWorkspaceDesc, setNewWorkspaceDesc] = useState('');

  // 1. Initial Load: Check Current User
  const loadInitialData = useCallback(async () => {
    try {
      const userData = await api.getCurrentUser();
      setUser(userData);
      
      const wsRes = await api.getWorkspaces();
      const wsList = Array.isArray(wsRes) ? wsRes : (wsRes?.results || []);
      setWorkspaces(wsList);
      if (wsList.length > 0) {
        setCurrentWorkspace(wsList[0]);
      }
      
      const usageData = await api.getUsageSummary();
      setUsage(usageData);
    } catch {
      // User not authenticated or token expired
      setUser(null);
    }
  }, []);

  useEffect(() => {
    loadInitialData();
  }, [loadInitialData]);

  // 2. Fetch Workspace Documents and Sessions whenever currentWorkspace changes
  const loadWorkspaceData = useCallback(async () => {
    if (!currentWorkspace) return;
    try {
      const [docsRes, sessionsRes, usageData] = await Promise.all([
        api.getDocuments(currentWorkspace.id),
        api.getChatSessions(currentWorkspace.id),
        api.getUsageSummary()
      ]);
      const docs = Array.isArray(docsRes) ? docsRes : (docsRes?.results || []);
      const sessions = Array.isArray(sessionsRes) ? sessionsRes : (sessionsRes?.results || []);
      setDocuments(docs);
      setChatSessions(sessions);
      setUsage(usageData);

      if (sessions.length > 0) {
        setCurrentSessionId(sessions[0].id);
        const sessionDetails = await api.getChatSessionDetails(sessions[0].id);
        setMessages(sessionDetails.messages || []);
      } else {
        setCurrentSessionId(null);
        setMessages([]);
      }
    } catch (err) {
      console.error("Error loading workspace details:", err);
    }
  }, [currentWorkspace]);

  useEffect(() => {
    loadWorkspaceData();
  }, [loadWorkspaceData]);

  // Load audit logs when switching to usage tab
  useEffect(() => {
    if (activeTab === 'usage') {
      api.getRequestHistory().then(res => setRequestHistory(res.results || [])).catch(() => {});
      api.getUsageSummary().then(setUsage).catch(() => {});
    }
  }, [activeTab]);

  // Select Chat Session
  const handleSelectSession = async (sessionId) => {
    setCurrentSessionId(sessionId);
    try {
      const details = await api.getChatSessionDetails(sessionId);
      setMessages(details.messages || []);
    } catch (e) {
      console.error(e);
    }
  };

  const handleNewSession = () => {
    setCurrentSessionId(null);
    setMessages([]);
  };

  // Send RAG Query
  const handleSendMessage = async (query) => {
    if (!currentWorkspace) return;
    setIsAsking(true);
    setQuotaError(null);

    // Optimistic user bubble
    const tempUserMsg = {
      id: `temp-${Date.now()}`,
      sender: 'USER',
      content: query,
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempUserMsg]);

    try {
      const res = await api.askQuestion(currentWorkspace.id, query, currentSessionId);
      
      if (!currentSessionId && res.session_id) {
        setCurrentSessionId(res.session_id);
        setChatSessions(prev => [{ id: res.session_id, title: res.session_title }, ...prev]);
      }

      const aiMsg = {
        id: res.message_id,
        sender: 'ASSISTANT',
        content: res.answer,
        citations: res.citations || [],
        latency_ms: res.latency_ms,
        total_tokens: res.total_tokens,
        model_used: res.model_used,
        is_fallback: res.is_fallback,
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, aiMsg]);

      // Refresh usage counter
      api.getUsageSummary().then(setUsage).catch(() => {});
    } catch (err) {
      if (err.status === 429) {
        setQuotaError(err.message || 'Daily query quota exceeded.');
      } else {
        alert(err.message || 'Error executing AI query');
      }
    } finally {
      setIsAsking(false);
    }
  };

  // Upload Document
  const handleUploadDocument = async (file) => {
    if (!currentWorkspace) return;
    setIsUploading(true);
    try {
      const res = await api.uploadDocument(currentWorkspace.id, file);
      alert(res.message || 'Document uploaded and indexed successfully!');
      loadWorkspaceData();
    } catch (err) {
      alert(`Upload error: ${err.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  // Delete Document
  const handleDeleteDocument = async (docId) => {
    if (!confirm('Are you sure you want to delete this document from the workspace?')) return;
    try {
      await api.deleteDocument(docId);
      setDocuments(prev => prev.filter(d => d.id !== docId));
      loadWorkspaceData();
    } catch (err) {
      alert(err.message || 'Delete failed');
    }
  };

  // View Chunks Modal
  const handleViewChunks = async (doc) => {
    setInspectingDoc(doc);
    try {
      const chunks = await api.getDocumentChunks(doc.id);
      setDocChunks(chunks);
    } catch (err) {
      console.error(err);
      setDocChunks([]);
    }
  };

  // Upgrade Tier
  const handleUpgradeTier = async (newTier) => {
    try {
      const res = await api.upgradeTier(newTier);
      setUser(res.user);
      const usageData = await api.getUsageSummary();
      setUsage(usageData);
      setQuotaError(null);
      alert(`Success: Tier upgraded to ${newTier}! Quota boundaries updated.`);
    } catch (err) {
      alert(`Upgrade failed: ${err.message}`);
    }
  };

  // Simulate Quota Actions
  const handleSimulateQuota = async (action) => {
    await api.simulateQuota(action);
    const usageData = await api.getUsageSummary();
    setUsage(usageData);
    const history = await api.getRequestHistory();
    setRequestHistory(history.results || []);
  };

  // Create Workspace
  const handleCreateWorkspace = async (e) => {
    e.preventDefault();
    if (!newWorkspaceName.trim()) return;
    try {
      const newWs = await api.createWorkspace(newWorkspaceName.trim(), newWorkspaceDesc.trim());
      setWorkspaces(prev => [newWs, ...prev]);
      setCurrentWorkspace(newWs);
      setShowNewWorkspaceModal(false);
      setNewWorkspaceName('');
      setNewWorkspaceDesc('');
    } catch (err) {
      alert(`Failed to create workspace: ${err.message}`);
    }
  };

  // Auth Handlers
  const handleLogin = async (email, password) => {
    const res = await api.login(email, password);
    setUser(res.user);
    loadInitialData();
  };

  const handleRegister = async (payload) => {
    await api.register(payload);
    await handleLogin(payload.email, payload.password);
  };

  const handleLogout = () => {
    api.setToken(null);
    setUser(null);
    setWorkspaces([]);
    setCurrentWorkspace(null);
  };

  if (!user) {
    return <LoginModal onLogin={handleLogin} onRegister={handleRegister} />;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', background: 'var(--bg-primary)' }}>
      {/* Top Navigation */}
      <Header
        user={user}
        workspaces={workspaces}
        currentWorkspace={currentWorkspace}
        onSelectWorkspace={setCurrentWorkspace}
        usage={usage}
        onUpgradeTier={handleUpgradeTier}
        onLogout={handleLogout}
      />

      {/* Main Workspace Body */}
      <div style={{ display: 'flex', flex: 1 }}>
        <Sidebar
          activeTab={activeTab}
          onSelectTab={setActiveTab}
          currentWorkspace={currentWorkspace}
          chatSessions={chatSessions}
          currentSessionId={currentSessionId}
          onSelectSession={handleSelectSession}
          onNewSession={handleNewSession}
          onOpenNewWorkspaceModal={() => setShowNewWorkspaceModal(true)}
        />

        <main style={{ flex: 1, overflowY: 'auto' }}>
          {activeTab === 'chat' && (
            <ChatInterface
              messages={messages}
              onSendMessage={handleSendMessage}
              isLoading={isAsking}
              currentWorkspace={currentWorkspace}
              quotaExceededError={quotaError}
              onClearQuotaError={() => setQuotaError(null)}
            />
          )}

          {activeTab === 'documents' && (
            <DocumentManager
              documents={documents}
              currentWorkspace={currentWorkspace}
              onUpload={handleUploadDocument}
              onDelete={handleDeleteDocument}
              onViewChunks={handleViewChunks}
              isUploading={isUploading}
            />
          )}

          {activeTab === 'usage' && (
            <UsageDashboard
              usage={usage}
              requestHistory={requestHistory}
              onSimulateQuota={handleSimulateQuota}
              onUpgradeTier={handleUpgradeTier}
            />
          )}

          {activeTab === 'architecture' && (
            <ArchitectureView />
          )}
        </main>
      </div>

      {/* Chunks Inspector Modal */}
      {inspectingDoc && (
        <ChunksModal
          document={inspectingDoc}
          chunks={docChunks}
          onClose={() => setInspectingDoc(null)}
        />
      )}

      {/* New Workspace Modal */}
      {showNewWorkspaceModal && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0,0,0,0.75)',
          backdropFilter: 'blur(8px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 70,
          padding: '1.5rem'
        }}>
          <div className="glass-panel" style={{ maxWidth: '480px', width: '100%', padding: '2rem', background: '#0d1220' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#fff', marginBottom: '0.4rem' }}>
              Create New Workspace
            </h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
              Multi-tenant isolated boundary for separate teams, projects, or compliance scopes.
            </p>
            <form onSubmit={handleCreateWorkspace} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ fontSize: '0.78rem', color: 'var(--text-dim)', display: 'block', marginBottom: '0.3rem' }}>
                  Workspace Name
                </label>
                <input
                  type="text"
                  value={newWorkspaceName}
                  onChange={(e) => setNewWorkspaceName(e.target.value)}
                  placeholder="e.g. Legal & Contracts Space"
                  required
                  className="input-text"
                />
              </div>
              <div>
                <label style={{ fontSize: '0.78rem', color: 'var(--text-dim)', display: 'block', marginBottom: '0.3rem' }}>
                  Description (Optional)
                </label>
                <textarea
                  value={newWorkspaceDesc}
                  onChange={(e) => setNewWorkspaceDesc(e.target.value)}
                  placeholder="Scope of documents and team members..."
                  rows="3"
                  className="input-text"
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
                <button
                  type="button"
                  onClick={() => setShowNewWorkspaceModal(false)}
                  className="btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-primary"
                >
                  Create Workspace
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
