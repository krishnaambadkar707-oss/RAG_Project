import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, FileText, CheckCircle2, Clock, Info, ShieldAlert, ChevronDown, ChevronUp } from 'lucide-react';

export default function ChatInterface({
  messages,
  onSendMessage,
  isLoading,
  selectedCollectionName
}) {
  const [inputQuery, setInputQuery] = useState('');
  const [expandedSourcesMsgId, setExpandedSourcesMsgId] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputQuery.trim() || isLoading) return;
    onSendMessage(inputQuery);
    setInputQuery('');
  };

  const suggestedQuestions = [
    "What is the company leave policy?",
    "How do I request a VPN certificate?",
    "What database is used for platform persistence?",
    "What is the home office stipend amount?"
  ];

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', padding: '20px', maxWidth: '1000px', margin: '0 auto', width: '100%' }}>
      
      {/* Scope Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', paddingBottom: '12px', borderBottom: '1px solid var(--border-color)' }}>
        <div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 600 }}>Enterprise Knowledge Q&A</h2>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Answers strictly grounded in internal documents with verifiable citations.
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className="badge badge-indigo">
            Scope: {selectedCollectionName || 'All Collections'}
          </span>
        </div>
      </div>

      {/* Message Feed */}
      <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '16px', paddingRight: '6px' }}>
        {messages.length === 0 ? (
          <div style={{ textAlign: 'center', margin: 'auto', maxWidth: '600px', padding: '30px' }} className="glass-panel">
            <div style={{
              width: '56px',
              height: '56px',
              borderRadius: '50%',
              background: 'rgba(99, 102, 241, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 16px'
            }}>
              <Sparkles size={28} color="#818cf8" />
            </div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '8px' }}>Ask internal policy or technical questions</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '20px' }}>
              The assistant searches your document corpus, extracts grounded context, and returns cited answers.
            </p>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', justifyContent: 'center' }}>
              {suggestedQuestions.map((q, idx) => (
                <button
                  key={idx}
                  onClick={() => onSendMessage(q)}
                  className="btn-secondary"
                  style={{ fontSize: '0.8rem', padding: '6px 12px', borderRadius: '16px' }}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg, index) => {
            const isUser = msg.role === 'user';
            const hasSources = msg.sources_json && msg.sources_json.length > 0;
            const isSourcesExpanded = expandedSourcesMsgId === msg.id || (index === messages.length - 1 && hasSources);

            return (
              <div
                key={msg.id || index}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: isUser ? 'flex-end' : 'flex-start',
                  width: '100%'
                }}
              >
                <div
                  style={{
                    maxWidth: '85%',
                    padding: '14px 18px',
                    borderRadius: 'var(--radius-md)',
                    background: isUser ? 'linear-gradient(135deg, #4f46e5 0%, #6366f1 100%)' : 'rgba(31, 41, 55, 0.8)',
                    border: isUser ? 'none' : '1px solid var(--border-color)',
                    color: '#ffffff',
                    fontSize: '0.92rem',
                    lineHeight: '1.5',
                    boxShadow: isUser ? '0 4px 12px rgba(79, 70, 229, 0.3)' : 'none'
                  }}
                >
                  <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>

                  {/* Assistant Message Extra Info: Latency & Grounded Badge */}
                  {!isUser && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '12px', paddingTop: '8px', borderTop: '1px solid rgba(255,255,255,0.08)', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      {hasSources ? (
                        <span className="badge badge-green" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                          <CheckCircle2 size={12} /> Grounded ({msg.sources_json.length} cited sources)
                        </span>
                      ) : (
                        <span className="badge badge-amber" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                          <ShieldAlert size={12} /> Fallback / Low Context
                        </span>
                      )}

                      {msg.latency_ms && (
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                          <Clock size={12} /> {msg.latency_ms} ms
                        </span>
                      )}
                    </div>
                  )}
                </div>

                {/* Sources Inspector Drawer */}
                {!isUser && hasSources && (
                  <div style={{ width: '85%', marginTop: '6px' }}>
                    <button
                      onClick={() => setExpandedSourcesMsgId(isSourcesExpanded ? null : msg.id)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: 'var(--primary)',
                        cursor: 'pointer',
                        fontSize: '0.78rem',
                        fontWeight: 600,
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                        padding: '4px 0'
                      }}
                    >
                      <FileText size={14} />
                      {isSourcesExpanded ? 'Hide Cited Sources' : `View ${msg.sources_json.length} Cited Sources`}
                      {isSourcesExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                    </button>

                    {isSourcesExpanded && (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '6px' }}>
                        {msg.sources_json.map((src, sIdx) => (
                          <div
                            key={sIdx}
                            style={{
                              padding: '10px 14px',
                              background: 'rgba(15, 23, 42, 0.7)',
                              border: '1px solid var(--border-color)',
                              borderRadius: 'var(--radius-sm)',
                              fontSize: '0.8rem'
                            }}
                          >
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px', fontWeight: 600, color: '#a5b4fc' }}>
                              <span>📄 {src.filename} (Page {src.page_number})</span>
                              <span className="badge badge-indigo" style={{ fontSize: '0.65rem' }}>
                                Similarity: {Math.round(src.similarity_score * 100)}%
                              </span>
                            </div>
                            <div style={{ color: 'var(--text-muted)', fontSize: '0.78rem', fontStyle: 'italic' }}>
                              Section: "{src.section_title}"
                            </div>
                            <p style={{ marginTop: '6px', color: '#d1d5db', background: 'rgba(0,0,0,0.2)', padding: '6px', borderRadius: '4px', borderLeft: '3px solid #6366f1' }}>
                              "{src.snippet}"
                            </p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })
        )}

        {isLoading && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            <Sparkles size={16} className="animate-spin" color="#818cf8" />
            Retrieving documents & generating grounded response...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Box */}
      <form onSubmit={handleSubmit} style={{ marginTop: '16px', display: 'flex', gap: '10px' }}>
        <input
          type="text"
          placeholder="Ask a question about leave policies, VPN certificates, architecture..."
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          disabled={isLoading}
          style={{
            flex: 1,
            padding: '14px 18px',
            borderRadius: 'var(--radius-md)',
            background: '#1e293b',
            color: '#ffffff',
            border: '1px solid var(--border-color)',
            fontSize: '0.95rem',
            outline: 'none',
            boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.2)'
          }}
        />
        <button
          type="submit"
          className="btn-primary"
          disabled={isLoading || !inputQuery.trim()}
          style={{ padding: '0 24px', opacity: isLoading || !inputQuery.trim() ? 0.6 : 1 }}
        >
          <Send size={18} />
          Ask
        </button>
      </form>
    </div>
  );
}
