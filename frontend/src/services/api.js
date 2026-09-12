const API_BASE = '/api';
const REQUEST_TIMEOUT = 30000; // 30 seconds

// Helper function to create a timeout promise
function timeoutPromise(ms) {
  return new Promise((_, reject) =>
    setTimeout(() => reject(new Error(`Request timeout after ${ms}ms`)), ms)
  );
}

export const getAuthToken = () => localStorage.getItem('rag_token');
export const setAuthToken = (token) => localStorage.setItem('rag_token', token);
export const removeAuthToken = () => localStorage.removeItem('rag_token');

export const getCurrentUser = () => {
  const userStr = localStorage.getItem('rag_user');
  try {
    return userStr ? JSON.parse(userStr) : null;
  } catch {
    return null;
  }
};

export const setCurrentUser = (user) => localStorage.setItem('rag_user', JSON.stringify(user));

async function request(endpoint, options = {}) {
  const token = getAuthToken();
  const headers = {
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  let response;
  try {
    // Use Promise.race to implement timeout
    response = await Promise.race([
      fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers,
      }),
      timeoutPromise(REQUEST_TIMEOUT)
    ]);
  } catch (netErr) {
    if (netErr.message.includes('timeout')) {
      throw new Error('Request timeout. The backend server may be unreachable or slow to respond.');
    }
    throw new Error('Backend server is unreachable. Please ensure the FastAPI server is running on port 8000.');
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: response.statusText || `HTTP ${response.status}` }));
    throw new Error(errorData.detail || `Request failed with status ${response.status}`);
  }

  return response.json();
}

export const api = {
  // Auth
  login: async (email, password) => {
    const data = await request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    setAuthToken(data.access_token);
    setCurrentUser(data.user);
    return data;
  },

  signup: async (email, password, role = 'employee') => {
    return request('/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ email, password, role }),
    });
  },

  getMe: () => request('/auth/me'),

  // Collections
  getCollections: () => request('/collections'),
  createCollection: (name, description) => request('/collections', {
    method: 'POST',
    body: JSON.stringify({ name, description }),
  }),
  deleteCollection: (id) => request(`/collections/${id}`, { method: 'DELETE' }),

  // Documents
  getDocuments: (collectionId = null) => {
    const query = collectionId ? `?collection_id=${collectionId}` : '';
    return request(`/documents${query}`);
  },
  uploadDocument: (file, collectionId = null) => {
    const formData = new FormData();
    formData.append('file', file);
    if (collectionId) formData.append('collection_id', collectionId);

    return request('/documents/upload', {
      method: 'POST',
      body: formData,
    });
  },
  deleteDocument: (id) => request(`/documents/${id}`, { method: 'DELETE' }),

  // RAG Query
  sendQuery: (question, collectionId = null, conversationId = null, topK = 5) => {
    return request('/query', {
      method: 'POST',
      body: JSON.stringify({
        question,
        collection_id: collectionId ? parseInt(collectionId) : null,
        conversation_id: conversationId ? parseInt(conversationId) : null,
        top_k: topK,
      }),
    });
  },

  // Conversations
  getConversations: () => request('/conversations'),
  getConversationDetail: (id) => request(`/conversations/${id}`),
  deleteConversation: (id) => request(`/conversations/${id}`, { method: 'DELETE' }),

  // Evaluation
  getEvalRuns: () => request('/evaluation/runs'),
  getEvalRunDetail: (id) => request(`/evaluation/runs/${id}`),
  triggerEvalRun: (name = "Benchmark Run", collectionId = null) => request('/evaluation/run', {
    method: 'POST',
    body: JSON.stringify({ name, collection_id: collectionId }),
  }),
};
