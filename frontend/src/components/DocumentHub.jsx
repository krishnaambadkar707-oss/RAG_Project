import React, { useState, useRef } from 'react';
import { UploadCloud, FolderPlus, FileText, CheckCircle2, AlertTriangle, Clock, Trash2, Sparkles, X } from 'lucide-react';

export default function DocumentHub({
  documents,
  collections,
  onUploadDocument,
  onCreateCollection,
  onDeleteDocument,
  isLoading
}) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [targetCollectionId, setTargetCollectionId] = useState('');
  const [newCollectionName, setNewCollectionName] = useState('');
  const [newCollectionDesc, setNewCollectionDesc] = useState('');
  const [showCreateCollectionModal, setShowCreateCollectionModal] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null); // { type: 'success' | 'error', message: string }

  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setUploadStatus(null);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
      setUploadStatus(null);
    }
  };

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile || isUploading) return;

    setIsUploading(true);
    setUploadStatus(null);

    try {
      const res = await onUploadDocument(selectedFile, targetCollectionId ? parseInt(targetCollectionId) : null);
      setUploadStatus({
        type: 'success',
        message: `Successfully uploaded and indexed '${selectedFile.name}' into vector corpus (${res?.chunk_count || 0} text chunks created across ${res?.page_count || 1} pages).`
      });
      setSelectedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch (err) {
      setUploadStatus({
        type: 'error',
        message: `Upload failed: ${err.message || 'Error uploading document to backend server.'}`
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleCreateCollectionSubmit = (e) => {
    e.preventDefault();
    if (!newCollectionName.trim()) return;
    onCreateCollection(newCollectionName.trim(), newCollectionDesc.trim());
    setNewCollectionName('');
    setNewCollectionDesc('');
    setShowCreateCollectionModal(false);
  };

  return (
    <div style={{ flex: 1, padding: '24px', maxWidth: '1100px', margin: '0 auto', width: '100%', overflowY: 'auto' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h2 style={{ fontSize: '1.3rem', fontWeight: 700 }}>Document Hub & Corpus Manager</h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Upload company PDFs/DOCXs, assign collections, and inspect chunking & vector indexing status.
          </p>
        </div>

        <button
          onClick={() => setShowCreateCollectionModal(!showCreateCollectionModal)}
          className="btn-secondary"
        >
          <FolderPlus size={16} />
          New Collection
        </button>
      </div>

      {/* Create Collection Inline Panel */}
      {showCreateCollectionModal && (
        <form onSubmit={handleCreateCollectionSubmit} className="glass-panel" style={{ padding: '16px', marginBottom: '24px', display: 'flex', gap: '12px', alignItems: 'flex-end' }}>
          <div style={{ flex: 1 }}>
            <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' }}>Collection Name</label>
            <input
              type="text"
              placeholder="e.g. Legal & Compliance"
              value={newCollectionName}
              onChange={(e) => setNewCollectionName(e.target.value)}
              required
              style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', background: '#1e293b', border: '1px solid var(--border-color)', color: '#fff', fontSize: '0.85rem', marginTop: '4px' }}
            />
          </div>
          <div style={{ flex: 1.5 }}>
            <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' }}>Description (Optional)</label>
            <input
              type="text"
              placeholder="e.g. Internal contracts and compliance frameworks"
              value={newCollectionDesc}
              onChange={(e) => setNewCollectionDesc(e.target.value)}
              style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', background: '#1e293b', border: '1px solid var(--border-color)', color: '#fff', fontSize: '0.85rem', marginTop: '4px' }}
            />
          </div>
          <button type="submit" className="btn-primary" style={{ padding: '9px 16px', fontSize: '0.85rem' }}>
            Save Collection
          </button>
        </form>
      )}

      {/* Status Alert Banner */}
      {uploadStatus && (
        <div
          style={{
            padding: '12px 16px',
            borderRadius: 'var(--radius-sm)',
            marginBottom: '20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            background: uploadStatus.type === 'success' ? 'rgba(34, 197, 94, 0.15)' : 'rgba(239, 68, 68, 0.15)',
            border: uploadStatus.type === 'success' ? '1px solid rgba(34, 197, 94, 0.4)' : '1px solid rgba(239, 68, 68, 0.4)',
            color: uploadStatus.type === 'success' ? '#4ade80' : '#f87171',
            fontSize: '0.88rem'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {uploadStatus.type === 'success' ? <CheckCircle2 size={18} /> : <AlertTriangle size={18} />}
            <span>{uploadStatus.message}</span>
          </div>
          <button onClick={() => setUploadStatus(null)} style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer' }}>
            <X size={16} />
          </button>
        </div>
      )}

      {/* Upload Zone & Drag Drop */}
      <form
        onSubmit={handleUploadSubmit}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className="glass-panel"
        style={{
          padding: '28px 24px',
          marginBottom: '30px',
          textAlign: 'center',
          border: isDragging ? '2px dashed #818cf8' : '2px dashed rgba(99, 102, 241, 0.4)',
          background: isDragging ? 'rgba(99, 102, 241, 0.08)' : 'rgba(15, 23, 42, 0.6)',
          transition: 'all 0.2s ease'
        }}
      >
        <UploadCloud size={44} color={isDragging ? '#a5b4fc' : '#818cf8'} style={{ marginBottom: '10px' }} />
        <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '6px' }}>Upload Document Into Vector Corpus</h3>
        <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '18px' }}>
          Drag & drop or browse PDF, DOCX, TXT, and Markdown files up to 25MB.
        </p>

        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '14px', maxWidth: '650px', margin: '0 auto', flexWrap: 'wrap' }}>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.doc,.txt,.md"
            onChange={handleFileChange}
            id="file-upload"
            style={{ display: 'none' }}
          />
          <label htmlFor="file-upload" className="btn-secondary" style={{ cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
            <FileText size={16} />
            {selectedFile ? selectedFile.name : 'Choose File'}
          </label>

          {selectedFile && (
            <span style={{ fontSize: '0.78rem', color: '#a5b4fc', background: 'rgba(99, 102, 241, 0.15)', padding: '4px 10px', borderRadius: '12px' }}>
              {(selectedFile.size / 1024).toFixed(1)} KB
            </span>
          )}

          <select
            value={targetCollectionId}
            onChange={(e) => setTargetCollectionId(e.target.value)}
            disabled={isUploading}
            style={{
              padding: '10px 14px',
              borderRadius: 'var(--radius-sm)',
              background: '#1e293b',
              color: 'var(--text-main)',
              border: '1px solid var(--border-color)',
              fontSize: '0.85rem',
              outline: 'none'
            }}
          >
            <option value="">No Collection (Unassigned)</option>
            {collections.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>

          <button
            type="submit"
            className="btn-primary"
            disabled={!selectedFile || isUploading || isLoading}
            style={{
              opacity: !selectedFile || isUploading || isLoading ? 0.6 : 1,
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              cursor: !selectedFile || isUploading || isLoading ? 'not-allowed' : 'pointer'
            }}
          >
            {isUploading ? (
              <>
                <Sparkles size={16} className="animate-spin" color="#ffffff" />
                Uploading & Indexing...
              </>
            ) : (
              <>
                <UploadCloud size={16} />
                Upload & Index
              </>
            )}
          </button>
        </div>
      </form>

      {/* Document Corpus Table */}
      <div className="glass-panel" style={{ overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>Indexed Documents ({documents.length})</h3>
        </div>

        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.88rem' }}>
          <thead>
            <tr style={{ background: 'rgba(255, 255, 255, 0.03)', borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
              <th style={{ padding: '12px 20px' }}>Filename</th>
              <th style={{ padding: '12px 16px' }}>Collection</th>
              <th style={{ padding: '12px 16px' }}>Status</th>
              <th style={{ padding: '12px 16px' }}>Pages</th>
              <th style={{ padding: '12px 16px' }}>Chunks</th>
              <th style={{ padding: '12px 20px', textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {documents.length === 0 ? (
              <tr>
                <td colSpan="6" style={{ padding: '30px', textAlign: 'center', color: 'var(--text-muted)' }}>
                  No documents uploaded yet. Upload your first PDF or DOCX file above.
                </td>
              </tr>
            ) : (
              documents.map((doc) => {
                const collectionName = collections.find((c) => c.id === doc.collection_id)?.name || 'Unassigned';

                return (
                  <tr key={doc.id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                    <td style={{ padding: '14px 20px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <FileText size={16} color="#818cf8" />
                      {doc.filename}
                    </td>
                    <td style={{ padding: '14px 16px', color: 'var(--text-muted)' }}>
                      <span className="badge badge-indigo" style={{ fontSize: '0.7rem' }}>{collectionName}</span>
                    </td>
                    <td style={{ padding: '14px 16px' }}>
                      {doc.status === 'processed' && (
                        <span className="badge badge-green" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                          <CheckCircle2 size={12} /> Indexed
                        </span>
                      )}
                      {doc.status === 'pending' && (
                        <span className="badge badge-amber" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                          <Clock size={12} /> Processing
                        </span>
                      )}
                      {doc.status === 'failed' && (
                        <span className="badge badge-red" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }} title={doc.error_message}>
                          <AlertTriangle size={12} /> Failed
                        </span>
                      )}
                    </td>
                    <td style={{ padding: '14px 16px', color: 'var(--text-muted)' }}>{doc.page_count || 1}</td>
                    <td style={{ padding: '14px 16px', color: '#a5b4fc', fontWeight: 600 }}>{doc.chunk_count || 0}</td>
                    <td style={{ padding: '14px 20px', textAlign: 'right' }}>
                      <button
                        onClick={() => onDeleteDocument(doc.id)}
                        style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer', opacity: 0.75 }}
                        title="Delete Document"
                      >
                        <Trash2 size={16} />
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
