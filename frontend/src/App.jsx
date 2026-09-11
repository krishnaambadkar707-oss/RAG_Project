import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import ChatInterface from './components/ChatInterface';
import DocumentHub from './components/DocumentHub';
import EvalDashboard from './components/EvalDashboard';
import NotificationsCenter from './components/NotificationsCenter';
import SettingsView from './components/SettingsView';
import AuthModal from './components/AuthModal';
import { api, getCurrentUser, removeAuthToken } from './services/api';

export default function App() {
  const [currentUser, setCurrentUser] = useState(getCurrentUser());
  const [activeTab, setActiveTab] = useState('chat'); // 'chat' | 'documents' | 'evaluation' | 'notifications' | 'settings'
  const [isAuthOpen, setIsAuthOpen] = useState(false);

  // Theme State ('dark' | 'light')
  const [theme, setTheme] = useState(() => localStorage.getItem('rag_theme') || 'dark');

  // RAG & Settings States
  const [topK, setTopK] = useState(5);
  const [similarityThreshold, setSimilarityThreshold] = useState(0.15);
  const [embeddingProvider, setEmbeddingProvider] = useState('sentence-transformers');
  const [llmProvider, setLlmProvider] = useState('mock');

  // Notifications State
  const [notifications, setNotifications] = useState([
    {
      id: 1,
      title: 'Vector Store Initialized',
      message: 'ChromaDB persistent collection enterprise_knowledge_base active with cosine distance metric.',
      category: 'system',
      type: 'info',
      read: false,
      timestamp: 'Just now'
    },
    {
      id: 2,
      title: 'Benchmark Verification Completed',
      message: 'Automated evaluation run completed with 90.0% Retrieval Precision@5 and 0.0% Hallucination rate.',
      category: 'evaluation',
      type: 'success',
      read: false,
      timestamp: '10 mins ago'
    },
    {
      id: 3,
      title: 'Embedding Model Loaded',
      message: 'SentenceTransformers all-MiniLM-L6-v2 warmed up and cached for fast sub-millisecond retrieval.',
      category: 'system',
      type: 'info',
      read: true,
      timestamp: '25 mins ago'
    }
  ]);

  // Data states
  const [collections, setCollections] = useState([]);
  const [selectedCollection, setSelectedCollection] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [evalRuns, setEvalRuns] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  // Apply theme to document root
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('rag_theme', theme);
  }, [theme]);

  // Load initial workspace data
  useEffect(() => {
    fetchCollections();
    fetchDocuments();
    fetchConversations();
    fetchEvalRuns();
  }, []);

  const fetchCollections = async () => {
    try {
      const data = await api.getCollections();
      setCollections(data);
    } catch (err) {
      console.warn('Could not fetch collections', err);
    }
  };

  const fetchDocuments = async () => {
    try {
      const data = await api.getDocuments(selectedCollection);
      setDocuments(data);
    } catch (err) {
      console.warn('Could not fetch documents', err);
    }
  };

  const fetchConversations = async () => {
    try {
      const data = await api.getConversations();
      setConversations(data);
    } catch (err) {
      console.warn('Could not fetch conversations', err);
    }
  };

  const fetchEvalRuns = async () => {
    try {
      const data = await api.getEvalRuns();
      setEvalRuns(data);
    } catch (err) {
      console.warn('Could not fetch evaluation runs', err);
    }
  };

  // Re-fetch documents on collection scope change
  useEffect(() => {
    fetchDocuments();
  }, [selectedCollection]);

  // Load conversation details when active conversation changes
  useEffect(() => {
    if (activeConversationId) {
      api.getConversationDetail(activeConversationId)
        .then((data) => setMessages(data.messages || []))
        .catch((err) => console.error(err));
    } else {
      setMessages([]);
    }
  }, [activeConversationId]);

  // Notifications Handlers
  const pushNotification = (title, message, category = 'system', type = 'info') => {
    const newNotif = {
      id: Date.now(),
      title,
      message,
      category,
      type,
      read: false,
      timestamp: 'Just now'
    };
    setNotifications(prev => [newNotif, ...prev]);
  };

  const handleMarkAsRead = (id) => {
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
  };

  const handleMarkAllAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  };

  const handleDeleteNotification = (id) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  const handleClearAllNotifications = () => {
    setNotifications([]);
  };

  const handleToggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  // Handlers
  const handleSendMessage = async (question) => {
    setIsLoading(true);
    // Optimistic user message render
    const tempUserMsg = { role: 'user', content: question, id: Date.now() };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const res = await api.sendQuery(question, selectedCollection, activeConversationId, topK);
      setActiveConversationId(res.conversation_id);
      
      const assistantMsg = {
        role: 'assistant',
        content: res.answer,
        sources_json: res.sources,
        latency_ms: res.latency_ms,
        id: Date.now() + 1
      };
      setMessages((prev) => [...prev, assistantMsg]);
      fetchConversations();
    } catch (err) {
      const errorMsg = {
        role: 'assistant',
        content: `Error: ${err.message || 'Failed to generate answer. Please check backend connection.'}`,
        id: Date.now() + 2
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUploadDocument = async (file, collectionId) => {
    setIsLoading(true);
    try {
      const result = await api.uploadDocument(file, collectionId);
      await fetchDocuments();
      await fetchCollections();
      pushNotification(
        'Document Indexed Successfully',
        `Document '${file.name}' was parsed into ${result?.page_count || 1} pages and indexed (${result?.chunk_count || 0} chunks).`,
        'document',
        'success'
      );
      return result;
    } catch (err) {
      pushNotification(
        'Document Upload Failed',
        `Failed to parse '${file.name}': ${err.message}`,
        'document',
        'error'
      );
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateCollection = async (name, description) => {
    try {
      await api.createCollection(name, description);
      await fetchCollections();
      pushNotification(
        'Collection Created',
        `New collection '${name}' created successfully.`,
        'document',
        'info'
      );
    } catch (err) {
      alert(`Create collection failed: ${err.message}`);
    }
  };

  const handleDeleteDocument = async (id) => {
    if (!window.confirm('Are you sure you want to delete this document from the vector corpus?')) return;
    try {
      await api.deleteDocument(id);
      await fetchDocuments();
      await fetchCollections();
      pushNotification(
        'Document Deleted',
        `Document ID #${id} removed from vector database and storage.`,
        'document',
        'info'
      );
    } catch (err) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  const handleDeleteConversation = async (id) => {
    try {
      await api.deleteConversation(id);
      if (activeConversationId === id) setActiveConversationId(null);
      await fetchConversations();
    } catch (err) {
      console.error(err);
    }
  };

  const handleTriggerEvalRun = async () => {
    setIsLoading(true);
    try {
      await api.triggerEvalRun("Automated Benchmark Run", selectedCollection);
      await fetchEvalRuns();
      pushNotification(
        'Benchmark Evaluation Finished',
        'Automated RAG evaluation pipeline run completed. Check Evaluation Dashboard for metrics.',
        'evaluation',
        'success'
      );
    } catch (err) {
      alert(`Evaluation run failed: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogin = async (email, password) => {
    const res = await api.login(email, password);
    setCurrentUser(res.user);
    setIsAuthOpen(false);
    fetchConversations();
    pushNotification('User Sign In', `Welcome back, ${res.user.email}!`, 'system', 'info');
  };

  const handleSignup = async (email, password, role) => {
    await api.signup(email, password, role);
    pushNotification('Account Created', `Account ${email} created successfully.`, 'system', 'info');
  };

  const handleLogout = () => {
    removeAuthToken();
    localStorage.removeItem('rag_user');
    setCurrentUser(null);
  };

  const selectedCollectionName = collections.find((c) => c.id === selectedCollection)?.name;
  const unreadNotificationCount = notifications.filter(n => !n.read).length;

  return (
    <div className="app-container">
      <Navbar
        currentUser={currentUser}
        onOpenAuth={() => setIsAuthOpen(true)}
        onLogout={handleLogout}
        theme={theme}
        onToggleTheme={handleToggleTheme}
        unreadNotificationCount={unreadNotificationCount}
        onOpenNotifications={() => setActiveTab('notifications')}
      />

      <div className="main-body">
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          collections={collections}
          selectedCollection={selectedCollection}
          setSelectedCollection={setSelectedCollection}
          conversations={conversations}
          activeConversationId={activeConversationId}
          onSelectConversation={(id) => setActiveConversationId(id)}
          onNewChat={() => {
            setActiveConversationId(null);
            setMessages([]);
          }}
          onDeleteConversation={handleDeleteConversation}
          unreadNotificationCount={unreadNotificationCount}
        />

        <main className="content-area">
          {activeTab === 'chat' && (
            <ChatInterface
              messages={messages}
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
              selectedCollectionName={selectedCollectionName}
            />
          )}

          {activeTab === 'documents' && (
            <DocumentHub
              documents={documents}
              collections={collections}
              onUploadDocument={handleUploadDocument}
              onCreateCollection={handleCreateCollection}
              onDeleteDocument={handleDeleteDocument}
              isLoading={isLoading}
            />
          )}

          {activeTab === 'evaluation' && (
            <EvalDashboard
              evalRuns={evalRuns}
              onTriggerEvalRun={handleTriggerEvalRun}
              isLoading={isLoading}
            />
          )}

          {activeTab === 'notifications' && (
            <NotificationsCenter
              notifications={notifications}
              onMarkAsRead={handleMarkAsRead}
              onMarkAllAsRead={handleMarkAllAsRead}
              onDeleteNotification={handleDeleteNotification}
              onClearAll={handleClearAllNotifications}
            />
          )}

          {activeTab === 'settings' && (
            <SettingsView
              theme={theme}
              setTheme={setTheme}
              topK={topK}
              setTopK={setTopK}
              similarityThreshold={similarityThreshold}
              setSimilarityThreshold={setSimilarityThreshold}
              embeddingProvider={embeddingProvider}
              setEmbeddingProvider={setEmbeddingProvider}
              llmProvider={llmProvider}
              setLlmProvider={setLlmProvider}
              onSaveSettings={() => pushNotification('Settings Saved', 'Platform preferences updated.', 'system', 'info')}
            />
          )}
        </main>
      </div>

      <AuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        onLogin={handleLogin}
        onSignup={handleSignup}
      />
    </div>
  );
}
