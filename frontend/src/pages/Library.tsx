import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Corpus, DocumentItem, JobStatus } from '../types';
import { Upload, FolderPlus, FileText, CheckCircle2, Clock, FileCode, Plus, AlertCircle, RefreshCw } from 'lucide-react';

export const Library: React.FC = () => {
  const [corpora, setCorpora] = useState<Corpus[]>([]);
  const [selectedCorpusId, setSelectedCorpusId] = useState<string>('');
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);

  // New Corpus Form
  const [showCorpusModal, setShowCorpusModal] = useState(false);
  const [newCorpusTitle, setNewCorpusTitle] = useState('');
  const [newCorpusDesc, setNewCorpusDesc] = useState('');

  // Upload Form
  const [file, setFile] = useState<File | null>(null);
  const [docTitle, setDocTitle] = useState('');
  const [author, setAuthor] = useState('');
  const [chapter, setChapter] = useState('');
  const [uploading, setUploading] = useState(false);
  const [activeJob, setActiveJob] = useState<JobStatus | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchCorpora();
  }, []);

  useEffect(() => {
    if (selectedCorpusId) {
      fetchDocuments(selectedCorpusId);
    }
  }, [selectedCorpusId]);

  const fetchCorpora = async () => {
    try {
      const data = await api.getCorpora();
      setCorpora(data);
      if (data.length > 0 && !selectedCorpusId) {
        setSelectedCorpusId(data[0].id);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchDocuments = async (corpusId: string) => {
    try {
      const docs = await api.getDocuments(corpusId);
      setDocuments(docs);
    } catch (err: any) {
      console.error(err);
    }
  };

  const handleCreateCorpus = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCorpusTitle.trim()) return;

    try {
      const created = await api.createCorpus(newCorpusTitle, newCorpusDesc);
      setCorpora([...corpora, created]);
      setSelectedCorpusId(created.id);
      setShowCorpusModal(false);
      setNewCorpusTitle('');
      setNewCorpusDesc('');
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    setUploading(true);
    setError('');

    try {
      const job = await api.uploadDocument(file, selectedCorpusId, docTitle, author, chapter);
      setActiveJob(job);
      pollJobStatus(job.id);
      setFile(null);
      setDocTitle('');
      setAuthor('');
      setChapter('');
    } catch (err: any) {
      setError(err.message || 'Upload failed');
      setUploading(false);
    }
  };

  const pollJobStatus = (jobId: string) => {
    const interval = setInterval(async () => {
      try {
        const job = await api.getJobStatus(jobId);
        setActiveJob(job);
        if (job.status === 'Ready' || job.status === 'Failed') {
          clearInterval(interval);
          setUploading(false);
          if (selectedCorpusId) fetchDocuments(selectedCorpusId);
          fetchCorpora();
        }
      } catch (err) {
        clearInterval(interval);
        setUploading(false);
      }
    }, 1200);
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-100 flex items-center gap-3">
            <FolderPlus className="w-7 h-7 text-amber-500" /> Corpus & Document Ingestion
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Ingest Sanskrit TXT, JSON, CSV, XML, or EPUB literature. Preserves exact immutable original text.
          </p>
        </div>

        <button
          onClick={() => setShowCorpusModal(true)}
          className="px-4 py-2.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 text-slate-950 font-semibold rounded-xl text-xs flex items-center gap-2 shadow-lg shadow-amber-950/30 transition-all"
        >
          <Plus className="w-4 h-4" /> Create New Corpus
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4" /> {error}
        </div>
      )}

      {/* Grid: Corpora List + Document Uploader & Table */}
      <div className="grid grid-cols-12 gap-8">
        {/* Left Column: Corpora Selection */}
        <div className="col-span-4 space-y-4">
          <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">Your Corpora</h3>
              <span className="text-xs text-slate-500">{corpora.length} Available</span>
            </div>

            <div className="space-y-2">
              {corpora.map((corpus) => (
                <div
                  key={corpus.id}
                  onClick={() => setSelectedCorpusId(corpus.id)}
                  className={`p-4 rounded-xl border cursor-pointer transition-all ${
                    selectedCorpusId === corpus.id
                      ? 'bg-amber-500/10 border-amber-500/40 text-amber-300 shadow-md'
                      : 'bg-slate-950/40 border-slate-800/80 hover:border-slate-700 text-slate-400'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <h4 className="font-semibold text-sm text-slate-200">{corpus.title}</h4>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-300">
                      {corpus.document_count} Docs
                    </span>
                  </div>
                  {corpus.description && (
                    <p className="text-xs text-slate-400 mt-1 line-clamp-2">{corpus.description}</p>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Upload Box */}
          <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
            <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
              <Upload className="w-4 h-4 text-amber-400" /> Upload File to Selected Corpus
            </h3>

            <form onSubmit={handleUpload} className="space-y-3">
              <div className="border-2 border-dashed border-slate-800 hover:border-amber-500/50 rounded-xl p-6 text-center bg-slate-950/40 transition-colors">
                <input
                  type="file"
                  onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)}
                  accept=".txt,.json,.csv,.xml,.epub"
                  className="hidden"
                  id="file-upload"
                />
                <label htmlFor="file-upload" className="cursor-pointer space-y-2 block">
                  <FileCode className="w-8 h-8 mx-auto text-amber-500/80" />
                  <span className="text-xs text-slate-300 block font-medium">
                    {file ? file.name : 'Choose File (TXT, JSON, CSV, XML, EPUB)'}
                  </span>
                  <span className="text-[10px] text-slate-500 block">Maximum file size: 25MB</span>
                </label>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <input
                  type="text"
                  placeholder="Title (Optional)"
                  value={docTitle}
                  onChange={(e) => setDocTitle(e.target.value)}
                  className="bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-amber-500"
                />
                <input
                  type="text"
                  placeholder="Author (e.g., Vyasa)"
                  value={author}
                  onChange={(e) => setAuthor(e.target.value)}
                  className="bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-amber-500"
                />
              </div>

              <input
                type="text"
                placeholder="Chapter / Section (e.g., Chapter 1)"
                value={chapter}
                onChange={(e) => setChapter(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
              />

              <button
                type="submit"
                disabled={!file || uploading}
                className="w-full py-2.5 bg-amber-500 hover:bg-amber-600 disabled:opacity-50 text-slate-950 font-semibold rounded-xl text-xs transition-all flex items-center justify-center gap-2"
              >
                {uploading ? 'Processing Ingestion Pipeline...' : 'Start Document Ingestion'}
              </button>
            </form>

            {/* Live Processing Pipeline Bar */}
            {activeJob && (
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between text-xs font-medium">
                  <span className="text-amber-400 flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5 animate-spin" /> {activeJob.status}
                  </span>
                  <span className="text-slate-400">{activeJob.progress_pct}%</span>
                </div>
                <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-amber-500 to-cyan-500 transition-all duration-300"
                    style={{ width: `${activeJob.progress_pct}%` }}
                  ></div>
                </div>
                <p className="text-[11px] text-slate-400">{activeJob.current_step}</p>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Ingested Documents List */}
        <div className="col-span-8 space-y-4">
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
              <div>
                <h3 className="text-base font-semibold text-slate-100">Ingested Literature</h3>
                <p className="text-xs text-slate-400">Indexed & Mapped Sanskrit Texts</p>
              </div>
              <button
                onClick={() => selectedCorpusId && fetchDocuments(selectedCorpusId)}
                className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-colors"
                title="Refresh Documents"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>

            {documents.length === 0 ? (
              <div className="py-16 text-center text-slate-500 text-xs space-y-2">
                <FileText className="w-10 h-10 mx-auto text-slate-700" />
                <p>No documents ingested in this corpus yet.</p>
                <p className="text-[11px] text-slate-600">Upload a TXT, JSON, CSV, or XML file to populate the index.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {documents.map((doc) => (
                  <div
                    key={doc.id}
                    className="p-4 rounded-xl glass-card border border-slate-800 space-y-2 hover:border-slate-700 transition-all"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4 text-amber-400" />
                        <h4 className="font-semibold text-sm text-slate-200">{doc.title}</h4>
                      </div>
                      <span className="text-[10px] px-2 py-0.5 rounded uppercase bg-amber-500/10 text-amber-400 border border-amber-500/20 font-mono">
                        {doc.file_type}
                      </span>
                    </div>

                    <div className="flex items-center gap-4 text-xs text-slate-400">
                      <span>Author: {doc.author}</span>
                      <span>•</span>
                      <span>Chapter: {doc.chapter}</span>
                      <span>•</span>
                      <span>{doc.character_count} Chars</span>
                      <span>•</span>
                      <span>{doc.word_count} Words</span>
                    </div>

                    {/* Original Text Preview */}
                    <div className="mt-2 p-3 rounded-lg bg-slate-950/70 border border-slate-800/80 font-devanagari text-xs text-slate-300 max-h-24 overflow-y-auto whitespace-pre-wrap">
                      {doc.original_text}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Modal for Creating Corpus */}
      {showCorpusModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
            <h3 className="text-base font-semibold text-slate-100">Create Sanskrit Corpus</h3>
            <form onSubmit={handleCreateCorpus} className="space-y-3">
              <input
                type="text"
                placeholder="Corpus Title (e.g., Mahābhārata)"
                value={newCorpusTitle}
                onChange={(e) => setNewCorpusTitle(e.target.value)}
                required
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-slate-200 focus:outline-none focus:border-amber-500"
              />
              <textarea
                placeholder="Description / Context"
                value={newCorpusDesc}
                onChange={(e) => setNewCorpusDesc(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-slate-200 focus:outline-none focus:border-amber-500 h-24"
              />
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCorpusModal(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 rounded-xl text-xs hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-amber-500 text-slate-950 font-semibold rounded-xl text-xs hover:bg-amber-600"
                >
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
