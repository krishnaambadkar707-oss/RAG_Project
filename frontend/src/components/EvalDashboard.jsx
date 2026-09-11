import React, { useState } from 'react';
import { Play, CheckCircle2, AlertTriangle, ShieldCheck, Clock, Award, ListFilter } from 'lucide-react';

export default function EvalDashboard({
  evalRuns,
  onTriggerEvalRun,
  isLoading
}) {
  const [selectedRunId, setSelectedRunId] = useState(null);

  const activeRun = selectedRunId
    ? evalRuns.find((r) => r.id === selectedRunId) || evalRuns[0]
    : evalRuns[0];

  return (
    <div style={{ flex: 1, padding: '24px', maxWidth: '1200px', margin: '0 auto', width: '100%', overflowY: 'auto' }}>
      
      {/* Dashboard Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h2 style={{ fontSize: '1.3rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Award color="#818cf8" size={24} />
            RAG Quality & Benchmark Evaluation System
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Automated measurement of Retrieval Precision@k, Answer Relevance, Hallucination Rate, and Latency.
          </p>
        </div>

        <button
          onClick={() => onTriggerEvalRun()}
          className="btn-primary"
          disabled={isLoading}
          style={{ opacity: isLoading ? 0.6 : 1 }}
        >
          <Play size={16} />
          {isLoading ? 'Running Benchmark Suite...' : 'Run Benchmark Evaluation'}
        </button>
      </div>

      {evalRuns.length === 0 ? (
        <div className="glass-panel" style={{ padding: '40px', textAlign: 'center', margin: '20px 0' }}>
          <ShieldCheck size={48} color="#818cf8" style={{ marginBottom: '12px' }} />
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '8px' }}>No Evaluation Runs Logged Yet</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '20px', maxWidth: '500px', margin: '0 auto 20px' }}>
            Click 'Run Benchmark Evaluation' to execute the test suite against your labeled Q&A dataset (`data/benchmark_test_set.json`).
          </p>
          <button onClick={() => onTriggerEvalRun()} className="btn-primary">
            <Play size={16} /> Execute Initial Benchmark
          </button>
        </div>
      ) : (
        <>
          {/* Run Selector Header */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)' }}>Select Evaluation Run:</span>
            <select
              value={activeRun?.id || ''}
              onChange={(e) => setSelectedRunId(parseInt(e.target.value))}
              style={{
                padding: '8px 14px',
                borderRadius: 'var(--radius-sm)',
                background: '#1e293b',
                color: '#fff',
                border: '1px solid var(--border-color)',
                fontSize: '0.85rem'
              }}
            >
              {evalRuns.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name} - Run #{r.id} ({new Date(r.run_date).toLocaleString()})
                </option>
              ))}
            </select>
          </div>

          {/* Metric Scorecards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px', marginBottom: '30px' }}>
            
            {/* Precision@k Card */}
            <div className="glass-card" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>RETRIEVAL PRECISION@5</span>
                <CheckCircle2 size={18} color="#10b981" />
              </div>
              <div style={{ fontSize: '1.8rem', fontWeight: 700, color: activeRun?.avg_precision_k >= 0.8 ? '#10b981' : '#f59e0b' }}>
                {Math.round((activeRun?.avg_precision_k || 0) * 100)}%
              </div>
              <p style={{ fontSize: '0.72rem', color: 'var(--text-subtle)', marginTop: '4px' }}>
                Target: ≥ 80% (Did correct chunk get retrieved?)
              </p>
            </div>

            {/* Answer Relevance Card */}
            <div className="glass-card" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>ANSWER RELEVANCE</span>
                <Award size={18} color="#818cf8" />
              </div>
              <div style={{ fontSize: '1.8rem', fontWeight: 700, color: '#818cf8' }}>
                {Math.round((activeRun?.avg_relevance || 0) * 100)}%
              </div>
              <p style={{ fontSize: '0.72rem', color: 'var(--text-subtle)', marginTop: '4px' }}>
                Similarity match vs reference ground truth
              </p>
            </div>

            {/* Hallucination Rate Card */}
            <div className="glass-card" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>HALLUCINATION RATE</span>
                <AlertTriangle size={18} color={activeRun?.hallucination_rate < 0.1 ? '#10b981' : '#ef4444'} />
              </div>
              <div style={{ fontSize: '1.8rem', fontWeight: 700, color: activeRun?.hallucination_rate < 0.1 ? '#10b981' : '#ef4444' }}>
                {Math.round((activeRun?.hallucination_rate || 0) * 100)}%
              </div>
              <p style={{ fontSize: '0.72rem', color: 'var(--text-subtle)', marginTop: '4px' }}>
                Target: &lt; 10% ungrounded responses
              </p>
            </div>

            {/* Latency Card */}
            <div className="glass-card" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>AVG RESPONSE LATENCY</span>
                <Clock size={18} color="#a5b4fc" />
              </div>
              <div style={{ fontSize: '1.8rem', fontWeight: 700, color: '#a5b4fc' }}>
                {Math.round(activeRun?.avg_latency_ms || 0)} <span style={{ fontSize: '1rem' }}>ms</span>
              </div>
              <p style={{ fontSize: '0.72rem', color: 'var(--text-subtle)', marginTop: '4px' }}>
                Target: &lt; 5000 ms total pipeline speed
              </p>
            </div>

          </div>

          {/* Detailed Question Breakdown Table */}
          <div className="glass-panel" style={{ overflow: 'hidden' }}>
            <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>Detailed Benchmark Test Set Results ({activeRun?.results?.length || 0} Questions)</h3>
            </div>

            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ background: 'rgba(255, 255, 255, 0.03)', borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
                  <th style={{ padding: '12px 16px', width: '25%' }}>Test Question</th>
                  <th style={{ padding: '12px 16px', width: '30%' }}>Generated Grounded Answer</th>
                  <th style={{ padding: '12px 12px', textAlign: 'center' }}>Retrieval Score</th>
                  <th style={{ padding: '12px 12px', textAlign: 'center' }}>Relevance</th>
                  <th style={{ padding: '12px 12px', textAlign: 'center' }}>Faithful</th>
                  <th style={{ padding: '12px 16px', textAlign: 'right' }}>Latency</th>
                </tr>
              </thead>
              <tbody>
                {activeRun?.results?.map((res) => (
                  <tr key={res.id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                    <td style={{ padding: '14px 16px', fontWeight: 600, color: '#ffffff' }}>
                      {res.question}
                    </td>
                    <td style={{ padding: '14px 16px', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                      <div style={{ maxHeight: '80px', overflowY: 'auto' }}>
                        {res.generated_answer}
                      </div>
                    </td>
                    <td style={{ padding: '14px 12px', textAlign: 'center' }}>
                      <span className={`badge ${res.retrieval_score >= 0.8 ? 'badge-green' : 'badge-amber'}`}>
                        {Math.round(res.retrieval_score * 100)}%
                      </span>
                    </td>
                    <td style={{ padding: '14px 12px', textAlign: 'center' }}>
                      <span className="badge badge-indigo">
                        {Math.round(res.relevance_score * 100)}%
                      </span>
                    </td>
                    <td style={{ padding: '14px 12px', textAlign: 'center' }}>
                      {res.hallucination_flag ? (
                        <span className="badge badge-red">Hallucinated</span>
                      ) : (
                        <span className="badge badge-green">Grounded</span>
                      )}
                    </td>
                    <td style={{ padding: '14px 16px', textAlign: 'right', color: 'var(--text-muted)' }}>
                      {Math.round(res.latency_ms)} ms
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
