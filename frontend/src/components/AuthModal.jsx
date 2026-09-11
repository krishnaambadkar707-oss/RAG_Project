import React, { useState } from 'react';
import { X, Lock, Mail, Shield, User } from 'lucide-react';

export default function AuthModal({ isOpen, onClose, onLogin, onSignup }) {
  const [isLoginView, setIsLoginView] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('employee');
  const [errorMsg, setErrorMsg] = useState('');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setLoading(true);

    try {
      if (isLoginView) {
        await onLogin(email, password);
      } else {
        await onSignup(email, password, role);
        setIsLoginView(true);
        setErrorMsg('Registration successful! Please sign in.');
      }
    } catch (err) {
      setErrorMsg(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.75)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 100
    }}>
      <div className="glass-panel" style={{ width: '100%', maxWidth: '420px', padding: '30px', position: 'relative' }}>
        <button
          onClick={onClose}
          style={{ position: 'absolute', top: '16px', right: '16px', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
        >
          <X size={20} />
        </button>

        <h3 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: '6px' }}>
          {isLoginView ? 'Sign In to Assistant' : 'Create Employee Account'}
        </h3>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '20px' }}>
          {isLoginView ? 'Enter your company credentials to access grounded search' : 'Register to start querying company knowledge base'}
        </p>

        {errorMsg && (
          <div style={{ padding: '10px 14px', borderRadius: '6px', background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.3)', color: '#fca5a5', fontSize: '0.82rem', marginBottom: '16px' }}>
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div>
            <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>Email Address</label>
            <div style={{ position: 'relative' }}>
              <Mail size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '12px' }} />
              <input
                type="email"
                placeholder="name@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                style={{ width: '100%', padding: '10px 12px 10px 38px', borderRadius: '6px', background: '#1e293b', border: '1px solid var(--border-color)', color: '#fff', fontSize: '0.9rem', outline: 'none' }}
              />
            </div>
          </div>

          <div>
            <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>Password</label>
            <div style={{ position: 'relative' }}>
              <Lock size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '12px' }} />
              <input
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                style={{ width: '100%', padding: '10px 12px 10px 38px', borderRadius: '6px', background: '#1e293b', border: '1px solid var(--border-color)', color: '#fff', fontSize: '0.9rem', outline: 'none' }}
              />
            </div>
          </div>

          {!isLoginView && (
            <div>
              <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>User Role</label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                style={{ width: '100%', padding: '10px 12px', borderRadius: '6px', background: '#1e293b', border: '1px solid var(--border-color)', color: '#fff', fontSize: '0.9rem' }}
              >
                <option value="employee">Employee (Query & Search)</option>
                <option value="admin">Admin (Upload & Document Management)</option>
              </select>
            </div>
          )}

          <button type="submit" className="btn-primary" disabled={loading} style={{ width: '100%', justifyContent: 'center', marginTop: '10px' }}>
            {loading ? 'Processing...' : (isLoginView ? 'Sign In' : 'Register Account')}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '16px' }}>
          <button
            onClick={() => setIsLoginView(!isLoginView)}
            style={{ background: 'none', border: 'none', color: 'var(--primary)', cursor: 'pointer', fontSize: '0.82rem' }}
          >
            {isLoginView ? "Don't have an account? Register" : "Already have an account? Sign In"}
          </button>
        </div>
      </div>
    </div>
  );
}
