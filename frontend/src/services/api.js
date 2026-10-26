const API_BASE = '/api';

class ApiService {
  constructor() {
    this.token = localStorage.getItem('falcon_token') || null;
  }

  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('falcon_token', token);
    } else {
      localStorage.removeItem('falcon_token');
    }
  }

  getHeaders(isMultipart = false) {
    const headers = {};
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    if (!isMultipart) {
      headers['Content-Type'] = 'application/json';
    }
    return headers;
  }

  async request(endpoint, options = {}) {
    const isMultipart = options.body instanceof FormData;
    const config = {
      ...options,
      headers: {
        ...this.getHeaders(isMultipart),
        ...(options.headers || {})
      }
    };

    const response = await fetch(`${API_BASE}${endpoint}`, config);
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      const error = new Error(data.message || data.detail || 'API Request failed');
      error.status = response.status;
      error.data = data;
      throw error;
    }

    return data;
  }

  // Authentication
  async login(email, password) {
    const data = await this.request('/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    if (data.access) {
      this.setToken(data.access);
    }
    return data;
  }

  async register(payload) {
    return this.request('/auth/register/', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  async getCurrentUser() {
    return this.request('/auth/me/');
  }

  async upgradeTier(tier) {
    return this.request('/auth/upgrade-tier/', {
      method: 'POST',
      body: JSON.stringify({ tier })
    });
  }

  // Workspaces
  async getWorkspaces() {
    return this.request('/workspaces/');
  }

  async createWorkspace(name, description) {
    return this.request('/workspaces/', {
      method: 'POST',
      body: JSON.stringify({ name, description })
    });
  }

  // Documents
  async getDocuments(workspaceId) {
    return this.request(`/documents/workspace/${workspaceId}/`);
  }

  async uploadDocument(workspaceId, file) {
    const formData = new FormData();
    formData.append('workspace_id', workspaceId);
    formData.append('file', file);
    return this.request('/documents/upload/', {
      method: 'POST',
      body: formData
    });
  }

  async deleteDocument(documentId) {
    return this.request(`/documents/${documentId}/`, {
      method: 'DELETE'
    });
  }

  async getDocumentChunks(documentId) {
    return this.request(`/documents/${documentId}/chunks/`);
  }

  // RAG and Discussions
  async askQuestion(workspaceId, query, sessionId = null) {
    return this.request('/rag/ask/', {
      method: 'POST',
      body: JSON.stringify({
        workspace_id: workspaceId,
        query,
        session_id: sessionId
      })
    });
  }

  async getChatSessions(workspaceId) {
    return this.request(`/rag/sessions/?workspace_id=${workspaceId}`);
  }

  async getChatSessionDetails(sessionId) {
    return this.request(`/rag/sessions/${sessionId}/`);
  }

  // Usage and Quotas
  async getUsageSummary() {
    return this.request('/usage/summary/');
  }

  async getRequestHistory() {
    return this.request('/usage/history/');
  }

  async simulateQuota(action) {
    return this.request('/usage/simulate-quota/', {
      method: 'POST',
      body: JSON.stringify({ action })
    });
  }
}

export const api = new ApiService();
