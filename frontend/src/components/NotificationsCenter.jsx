import React, { useState } from 'react';
import { Bell, CheckCircle2, AlertTriangle, FileText, BarChart2, ShieldCheck, Check, Trash2, Filter } from 'lucide-react';

export default function NotificationsCenter({ notifications, onMarkAsRead, onMarkAllAsRead, onDeleteNotification, onClearAll }) {
  const [filter, setFilter] = useState('all');

  const filteredNotifications = notifications.filter(n => {
    if (filter === 'unread') return !n.read;
    if (filter === 'documents') return n.category === 'document';
    if (filter === 'evaluation') return n.category === 'evaluation';
    if (filter === 'system') return n.category === 'system';
    return true;
  });

  const unreadCount = notifications.filter(n => !n.read).length;

  const getCategoryIcon = (category, type) => {
    if (type === 'error') return <AlertTriangle size={18} color="#f87171" />;
    if (category === 'document') return <FileText size={18} color="#818cf8" />;
    if (category === 'evaluation') return <BarChart2 size={18} color="#34d399" />;
    return <ShieldCheck size={18} color="#fbbf24" />;
  };

  return (
    <div style={{ flex: 1, padding: '24px', maxWidth: '1000px', margin: '0 auto', width: '100%', overflowY: 'auto' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <h2 style={{ fontSize: '1.3rem', fontWeight: 700 }}>Notifications & Alerts</h2>
            {unreadCount > 0 && (
              <span className="badge badge-amber" style={{ borderRadius: '12px' }}>
                {unreadCount} Unread
              </span>
            )}
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Real-time indexing status, evaluation benchmark alerts, and platform security events.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          {unreadCount > 0 && (
            <button onClick={onMarkAllAsRead} className="btn-secondary" style={{ padding: '8px 14px', fontSize: '0.82rem' }}>
              <Check size={14} /> Mark All Read
            </button>
          )}
          {notifications.length > 0 && (
            <button onClick={onClearAll} className="btn-secondary" style={{ padding: '8px 14px', fontSize: '0.82rem', color: '#f87171' }}>
              <Trash2 size={14} /> Clear History
            </button>
          )}
        </div>
      </div>

      {/* Filter Tabs */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px' }}>
        {[
          { key: 'all', label: `All (${notifications.length})` },
          { key: 'unread', label: `Unread (${unreadCount})` },
          { key: 'documents', label: 'Documents' },
          { key: 'evaluation', label: 'Evaluation' },
          { key: 'system', label: 'System' }
        ].map(t => (
          <button
            key={t.key}
            onClick={() => setFilter(t.key)}
            className={filter === t.key ? 'btn-primary' : 'btn-secondary'}
            style={{ padding: '6px 14px', fontSize: '0.8rem', borderRadius: '16px' }}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Notifications List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {filteredNotifications.length === 0 ? (
          <div className="glass-panel" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
            <Bell size={36} color="#6366f1" style={{ marginBottom: '12px', opacity: 0.6 }} />
            <h4 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '4px' }}>No notifications found</h4>
            <p style={{ fontSize: '0.82rem' }}>You're all caught up! New alerts will appear here when documents are uploaded or benchmark tests run.</p>
          </div>
        ) : (
          filteredNotifications.map((item) => (
            <div
              key={item.id}
              className="glass-panel"
              style={{
                padding: '16px 20px',
                display: 'flex',
                alignItems: 'flex-start',
                justifyContent: 'space-between',
                gap: '16px',
                background: item.read ? 'rgba(17, 24, 39, 0.4)' : 'rgba(99, 102, 241, 0.1)',
                borderLeft: item.read ? '1px solid var(--border-color)' : '4px solid #6366f1',
                transition: 'all 0.2s ease'
              }}
            >
              <div style={{ display: 'flex', gap: '14px', alignItems: 'flex-start' }}>
                <div style={{ padding: '8px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', marginTop: '2px' }}>
                  {getCategoryIcon(item.category, item.type)}
                </div>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                    <h4 style={{ fontSize: '0.92rem', fontWeight: 600, color: 'var(--text-main)' }}>{item.title}</h4>
                    <span className="badge badge-indigo" style={{ fontSize: '0.65rem' }}>{item.category}</span>
                  </div>
                  <p style={{ fontSize: '0.84rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>{item.message}</p>
                  <span style={{ fontSize: '0.74rem', color: 'var(--text-subtle)', marginTop: '6px', display: 'inline-block' }}>{item.timestamp}</span>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                {!item.read && (
                  <button
                    onClick={() => onMarkAsRead(item.id)}
                    style={{ background: 'none', border: 'none', color: '#818cf8', cursor: 'pointer', fontSize: '0.78rem', display: 'flex', alignItems: 'center', gap: '4px' }}
                    title="Mark as read"
                  >
                    <CheckCircle2 size={14} /> Mark Read
                  </button>
                )}
                <button
                  onClick={() => onDeleteNotification(item.id)}
                  style={{ background: 'none', border: 'none', color: 'var(--text-subtle)', cursor: 'pointer' }}
                  title="Delete notification"
                >
                  <Trash2 size={15} />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
