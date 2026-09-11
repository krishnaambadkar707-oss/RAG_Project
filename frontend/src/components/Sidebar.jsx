import React from 'react';
import { MessageSquare, Folder, BarChart3, Bell, Settings, Plus, Layers, Trash2, Filter } from 'lucide-react';

export default function Sidebar({
  activeTab,
  setActiveTab,
  collections,
  selectedCollection,
  setSelectedCollection,
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewChat,
  onDeleteConversation,
  unreadNotificationCount = 0
}) {
  return (
    <aside style={{
      width: '260px',
      background: 'rgba(15, 23, 42, 0.85)',
      borderRight: '1px solid var(--border-color)',
      display: 'flex',
      flexDirection: 'column',
      padding: '16px',
      gap: '20px'
    }}>
      {/* Primary Navigation */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
        <button
          onClick={() => setActiveTab('chat')}
          className={activeTab === 'chat' ? 'btn-primary' : 'btn-secondary'}
          style={{ width: '100%', justifyContent: 'flex-start' }}
        >
          <MessageSquare size={18} />
          Q&A Assistant
        </button>

        <button
          onClick={() => setActiveTab('documents')}
          className={activeTab === 'documents' ? 'btn-primary' : 'btn-secondary'}
          style={{ width: '100%', justifyContent: 'flex-start' }}
        >
          <Folder size={18} />
          Document Hub
        </button>

        <button
          onClick={() => setActiveTab('evaluation')}
          className={activeTab === 'evaluation' ? 'btn-primary' : 'btn-secondary'}
          style={{ width: '100%', justifyContent: 'flex-start' }}
        >
          <BarChart3 size={18} />
          Evaluation Dashboard
        </button>

        <button
          onClick={() => setActiveTab('notifications')}
          className={activeTab === 'notifications' ? 'btn-primary' : 'btn-secondary'}
          style={{ width: '100%', justifyContent: 'space-between' }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Bell size={18} />
            Notifications
          </div>
          {unreadNotificationCount > 0 && (
            <span style={{ background: '#ef4444', color: '#fff', fontSize: '0.7rem', fontWeight: 700, padding: '2px 7px', borderRadius: '10px' }}>
              {unreadNotificationCount}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveTab('settings')}
          className={activeTab === 'settings' ? 'btn-primary' : 'btn-secondary'}
          style={{ width: '100%', justifyContent: 'flex-start' }}
        >
          <Settings size={18} />
          Settings
        </button>
      </div>

      {/* Collection Scope Selector */}
      <div style={{ padding: '12px', background: 'rgba(255, 255, 255, 0.03)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px', color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase' }}>
          <Filter size={14} color="#6366f1" />
          Collection Scope
        </div>
        <select
          value={selectedCollection || ''}
          onChange={(e) => setSelectedCollection(e.target.value ? parseInt(e.target.value) : null)}
          style={{
            width: '100%',
            padding: '8px 10px',
            borderRadius: '6px',
            background: '#1e293b',
            color: 'var(--text-main)',
            border: '1px solid var(--border-color)',
            fontSize: '0.85rem',
            outline: 'none'
          }}
        >
          <option value="">All Collections (Global)</option>
          {collections.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name} ({c.document_count || 0})
            </option>
          ))}
        </select>
      </div>

      {/* Conversation Sessions History (Only when in chat tab) */}
      {activeTab === 'chat' && (
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
              Past Chats
            </span>
            <button
              onClick={onNewChat}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--primary)',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                fontSize: '0.8rem',
                fontWeight: 600
              }}
            >
              <Plus size={14} /> New
            </button>
          </div>

          <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {conversations.length === 0 ? (
              <p style={{ fontSize: '0.8rem', color: 'var(--text-subtle)', fontStyle: 'italic' }}>No past conversations</p>
            ) : (
              conversations.map((c) => (
                <div
                  key={c.id}
                  onClick={() => onSelectConversation(c.id)}
                  style={{
                    padding: '8px 10px',
                    borderRadius: '6px',
                    background: activeConversationId === c.id ? 'rgba(99, 102, 241, 0.25)' : 'transparent',
                    border: activeConversationId === c.id ? '1px solid rgba(99, 102, 241, 0.4)' : '1px solid transparent',
                    color: activeConversationId === c.id ? '#ffffff' : 'var(--text-muted)',
                    cursor: 'pointer',
                    fontSize: '0.82rem',
                    display: 'flex',
                    justify: 'space-between',
                    alignItems: 'center',
                    transition: 'all 0.15s ease'
                  }}
                >
                  <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '170px' }}>
                    {c.title || `Chat #${c.id}`}
                  </span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteConversation(c.id);
                    }}
                    style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer', opacity: 0.6 }}
                    title="Delete Chat"
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </aside>
  );
}
