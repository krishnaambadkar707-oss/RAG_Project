import React from 'react';
import { Sparkles, Shield, User as UserIcon, LogOut, LogIn, Sun, Moon, Bell } from 'lucide-react';

export default function Navbar({
  currentUser,
  onOpenAuth,
  onLogout,
  theme,
  onToggleTheme,
  unreadNotificationCount = 0,
  onOpenNotifications
}) {
  return (
    <header className="glass-panel" style={{ borderRadius: 0, borderBottom: '1px solid var(--border-color)', padding: '14px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', zIndex: 10 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{
          width: '38px',
          height: '38px',
          borderRadius: '10px',
          background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 0 16px rgba(99, 102, 241, 0.4)'
        }}>
          <Sparkles size={20} color="#ffffff" />
        </div>
        <div>
          <h1 style={{ fontSize: '1.15rem', fontWeight: 700, background: 'linear-gradient(90deg, #ffffff, #c7d2fe)', WebkitBackgroundClip: 'text', WebkitTextFillColor: theme === 'light' ? '#0f172a' : 'transparent' }}>
            Enterprise RAG Assistant
          </h1>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Grounded Knowledge Retrieval & Performance Evaluation Platform
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        {/* Theme Toggle Button */}
        <button
          onClick={onToggleTheme}
          className="btn-secondary"
          style={{ padding: '8px 12px', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '6px' }}
          title={`Switch to ${theme === 'dark' ? 'Bright / Light' : 'Dark'} Mode`}
        >
          {theme === 'dark' ? <Sun size={17} color="#f59e0b" /> : <Moon size={17} color="#6366f1" />}
          <span>{theme === 'dark' ? 'Light' : 'Dark'}</span>
        </button>

        {/* Notifications Icon Button */}
        <button
          onClick={onOpenNotifications}
          className="btn-secondary"
          style={{ padding: '8px 12px', position: 'relative', display: 'flex', alignItems: 'center', gap: '6px' }}
          title="Notifications & System Alerts"
        >
          <Bell size={17} />
          {unreadNotificationCount > 0 && (
            <span style={{
              position: 'absolute',
              top: '-4px',
              right: '-4px',
              background: '#ef4444',
              color: '#ffffff',
              fontSize: '0.65rem',
              fontWeight: 700,
              width: '18px',
              height: '18px',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '2px solid var(--bg-dark)'
            }}>
              {unreadNotificationCount}
            </span>
          )}
        </button>

        {currentUser ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '6px 12px',
              background: 'rgba(255, 255, 255, 0.05)',
              borderRadius: '20px',
              border: '1px solid var(--border-color)'
            }}>
              <UserIcon size={16} color="#a5b4fc" />
              <span style={{ fontSize: '0.85rem', fontWeight: 500 }}>{currentUser.email}</span>
              <span className={`badge ${currentUser.role === 'admin' ? 'badge-amber' : 'badge-indigo'}`} style={{ fontSize: '0.65rem' }}>
                {currentUser.role}
              </span>
            </div>

            <button onClick={onLogout} className="btn-secondary" style={{ padding: '6px 12px', fontSize: '0.85rem' }} title="Logout">
              <LogOut size={16} />
              Logout
            </button>
          </div>
        ) : (
          <button onClick={onOpenAuth} className="btn-primary" style={{ padding: '8px 16px', fontSize: '0.85rem' }}>
            <LogIn size={16} />
            Sign In / Register
          </button>
        )}
      </div>
    </header>
  );
}
