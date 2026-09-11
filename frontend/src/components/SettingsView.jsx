import React from 'react';
import { Sun, Moon, Sliders, Database, Cpu, Shield, Save, CheckCircle2, RefreshCw } from 'lucide-react';

export default function SettingsView({
  theme,
  setTheme,
  topK,
  setTopK,
  similarityThreshold,
  setSimilarityThreshold,
  embeddingProvider,
  setEmbeddingProvider,
  llmProvider,
  setLlmProvider,
  onSaveSettings
}) {
  const [savedSuccess, setSavedSuccess] = React.useState(false);

  const handleSave = (e) => {
    e.preventDefault();
    onSaveSettings();
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  return (
    <div style={{ flex: 1, padding: '24px', maxWidth: '1000px', margin: '0 auto', width: '100%', overflowY: 'auto' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h2 style={{ fontSize: '1.3rem', fontWeight: 700 }}>Platform Settings & Preferences</h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Configure theme aesthetics, RAG retrieval parameters, and model engine providers.
          </p>
        </div>

        {savedSuccess && (
          <div className="badge badge-green" style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 14px' }}>
            <CheckCircle2 size={16} /> Settings Saved!
          </div>
        )}
      </div>

      <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        
        {/* Section 1: Appearance & Theme */}
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px', borderBottom: '1px solid var(--border-color)', paddingBottom: '10px' }}>
            <Sun size={20} color="#818cf8" />
            <h3 style={{ fontSize: '1.05rem', fontWeight: 600 }}>Appearance & Theme</h3>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
            {/* Dark Theme Option */}
            <div
              onClick={() => setTheme('dark')}
              className="glass-card"
              style={{
                padding: '16px',
                cursor: 'pointer',
                border: theme === 'dark' ? '2px solid #6366f1' : '1px solid var(--border-color)',
                background: 'rgba(15, 23, 42, 0.9)',
                borderRadius: 'var(--radius-md)'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 600, color: '#f9fafb' }}>
                  <Moon size={18} color="#a5b4fc" /> Dark Mode (Default)
                </div>
                {theme === 'dark' && <CheckCircle2 size={18} color="#6366f1" />}
              </div>
              <p style={{ fontSize: '0.8rem', color: '#9ca3af' }}>
                Sleek glassmorphic dark theme tailored for prolonged technical workflows and reduced eye strain.
              </p>
            </div>

            {/* Bright / Light Theme Option */}
            <div
              onClick={() => setTheme('light')}
              className="glass-card"
              style={{
                padding: '16px',
                cursor: 'pointer',
                border: theme === 'light' ? '2px solid #6366f1' : '1px solid var(--border-color)',
                background: theme === 'light' ? '#f8fafc' : 'rgba(255, 255, 255, 0.05)',
                color: theme === 'light' ? '#0f172a' : 'inherit',
                borderRadius: 'var(--radius-md)'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 600, color: theme === 'light' ? '#0f172a' : '#f9fafb' }}>
                  <Sun size={18} color="#f59e0b" /> Bright / Light Theme
                </div>
                {theme === 'light' && <CheckCircle2 size={18} color="#6366f1" />}
              </div>
              <p style={{ fontSize: '0.8rem', color: theme === 'light' ? '#64748b' : '#9ca3af' }}>
                Clean, high-contrast bright theme ideal for daytime presentation and document auditing.
              </p>
            </div>
          </div>
        </div>

        {/* Section 2: RAG Vector Retrieval Parameters */}
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px', borderBottom: '1px solid var(--border-color)', paddingBottom: '10px' }}>
            <Sliders size={20} color="#34d399" />
            <h3 style={{ fontSize: '1.05rem', fontWeight: 600 }}>RAG Vector Retrieval Parameters</h3>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Top-K Retrieval Count ({topK} chunks)</label>
              </div>
              <input
                type="range"
                min="1"
                max="10"
                step="1"
                value={topK}
                onChange={(e) => setTopK(parseInt(e.target.value))}
                style={{ width: '100%', accentColor: '#6366f1', cursor: 'pointer' }}
              />
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Number of top vector chunks retrieved from ChromaDB per user query.
              </span>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Context Grounding Threshold ({similarityThreshold})</label>
              </div>
              <input
                type="range"
                min="0.0"
                max="0.5"
                step="0.05"
                value={similarityThreshold}
                onChange={(e) => setSimilarityThreshold(parseFloat(e.target.value))}
                style={{ width: '100%', accentColor: '#34d399', cursor: 'pointer' }}
              />
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Minimum similarity score cutoff before falling back to out-of-context warning.
              </span>
            </div>
          </div>
        </div>

        {/* Section 3: Model & Provider Engine */}
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px', borderBottom: '1px solid var(--border-color)', paddingBottom: '10px' }}>
            <Cpu size={20} color="#fbbf24" />
            <h3 style={{ fontSize: '1.05rem', fontWeight: 600 }}>AI Model & Provider Config</h3>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
            <div>
              <label style={{ fontSize: '0.85rem', fontWeight: 600, display: 'block', marginBottom: '6px' }}>Embedding Model Provider</label>
              <select
                value={embeddingProvider}
                onChange={(e) => setEmbeddingProvider(e.target.value)}
                style={{ width: '100%', padding: '10px', borderRadius: '6px', background: '#1e293b', border: '1px solid var(--border-color)', color: 'var(--text-main)', fontSize: '0.85rem' }}
              >
                <option value="sentence-transformers">SentenceTransformers (all-MiniLM-L6-v2) - Local</option>
                <option value="openai">OpenAI (text-embedding-3-small) - API</option>
              </select>
            </div>

            <div>
              <label style={{ fontSize: '0.85rem', fontWeight: 600, display: 'block', marginBottom: '6px' }}>Grounded LLM Generation Engine</label>
              <select
                value={llmProvider}
                onChange={(e) => setLlmProvider(e.target.value)}
                style={{ width: '100%', padding: '10px', borderRadius: '6px', background: '#1e293b', border: '1px solid var(--border-color)', color: 'var(--text-main)', fontSize: '0.85rem' }}
              >
                <option value="mock">Local Grounded Engine (No API Key Required)</option>
                <option value="openai">OpenAI (GPT-4o-mini)</option>
                <option value="gemini">Google Gemini (Gemini 1.5 Flash)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Section 4: Storage Infrastructure Status */}
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px', borderBottom: '1px solid var(--border-color)', paddingBottom: '10px' }}>
            <Database size={20} color="#a5b4fc" />
            <h3 style={{ fontSize: '1.05rem', fontWeight: 600 }}>Storage & Infrastructure Status</h3>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
            <div style={{ padding: '14px', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Vector Store</span>
              <h4 style={{ fontSize: '0.95rem', fontWeight: 600, marginTop: '2px', color: '#4ade80' }}>ChromaDB Persistent (HNSW)</h4>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', marginTop: '4px' }}>Path: ./chroma_data</p>
            </div>

            <div style={{ padding: '14px', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Relational DB</span>
              <h4 style={{ fontSize: '0.95rem', fontWeight: 600, marginTop: '2px', color: '#4ade80' }}>SQLAlchemy + SQLite</h4>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', marginTop: '4px' }}>Path: ./rag_assistant.db</p>
            </div>

            <div style={{ padding: '14px', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Backend Service</span>
              <h4 style={{ fontSize: '0.95rem', fontWeight: 600, marginTop: '2px', color: '#818cf8' }}>FastAPI Python 3.13</h4>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', marginTop: '4px' }}>Port: 8000 (Active)</p>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '10px' }}>
          <button type="submit" className="btn-primary" style={{ padding: '12px 28px', fontSize: '0.95rem' }}>
            <Save size={18} /> Save Settings & Apply Theme
          </button>
        </div>
      </form>
    </div>
  );
}
