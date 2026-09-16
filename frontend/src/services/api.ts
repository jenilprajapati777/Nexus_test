import { SearchResponse, ExplainResponse, Corpus, DocumentItem, JobStatus, AblationReport, BenchmarkQuery } from '../types';

const API_BASE = '/api/v1';

const getHeaders = () => {
  const token = localStorage.getItem('sanskrit_ir_token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
};

export const api = {
  // Auth
  register: async (email: string, password: string, role = 'user') => {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, role }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Registration failed');
    }
    return res.json();
  },

  login: async (email: string, password: string) => {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Login failed');
    }
    return res.json();
  },

  getMe: async () => {
    const res = await fetch(`${API_BASE}/auth/me`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Unauthorized');
    return res.json();
  },

  // Corpora & Documents
  getCorpora: async (): Promise<Corpus[]> => {
    const res = await fetch(`${API_BASE}/ingestion/corpora`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch corpora');
    return res.json();
  },

  createCorpus: async (title: string, description?: string): Promise<Corpus> => {
    const res = await fetch(`${API_BASE}/ingestion/corpora`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ title, description }),
    });
    if (!res.ok) throw new Error('Failed to create corpus');
    return res.json();
  },

  uploadDocument: async (
    file: File,
    corpusId?: string,
    title?: string,
    author?: string,
    chapter?: string
  ): Promise<JobStatus> => {
    const token = localStorage.getItem('sanskrit_ir_token');
    const formData = new FormData();
    formData.append('file', file);
    if (corpusId) formData.append('corpus_id', corpusId);
    if (title) formData.append('title', title);
    if (author) formData.append('author', author);
    if (chapter) formData.append('chapter', chapter);

    const res = await fetch(`${API_BASE}/ingestion/upload`, {
      method: 'POST',
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: formData,
    });
    if (!res.ok) throw new Error('Upload failed');
    return res.json();
  },

  getJobStatus: async (jobId: string): Promise<JobStatus> => {
    const res = await fetch(`${API_BASE}/ingestion/jobs/${jobId}`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to get job status');
    return res.json();
  },

  getDocuments: async (corpusId?: string): Promise<DocumentItem[]> => {
    const url = corpusId ? `${API_BASE}/ingestion/documents?corpus_id=${corpusId}` : `${API_BASE}/ingestion/documents`;
    const res = await fetch(url, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch documents');
    return res.json();
  },

  // Search
  search: async (params: {
    query: string;
    mode?: string;
    corpus_ids?: string[];
    author_filter?: string;
    chapter_filter?: string;
    top_k?: number;
  }): Promise<SearchResponse> => {
    const res = await fetch(`${API_BASE}/search/query`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(params),
    });
    if (!res.ok) throw new Error('Search failed');
    return res.json();
  },

  explain: async (docId: string, query: string): Promise<ExplainResponse> => {
    const res = await fetch(`${API_BASE}/search/explain`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ doc_id: docId, query }),
    });
    if (!res.ok) throw new Error('Explain request failed');
    return res.json();
  },

  // Evaluation
  getBenchmarks: async (): Promise<BenchmarkQuery[]> => {
    const res = await fetch(`${API_BASE}/evaluation/benchmarks`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch benchmarks');
    return res.json();
  },

  createBenchmark: async (query_text: string, description: string, category: string): Promise<BenchmarkQuery> => {
    const res = await fetch(`${API_BASE}/evaluation/benchmarks`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ query_text, description, category, gold_relevance: {} }),
    });
    if (!res.ok) throw new Error('Failed to create benchmark');
    return res.json();
  },

  runAblation: async (): Promise<AblationReport> => {
    const res = await fetch(`${API_BASE}/evaluation/ablation`, {
      method: 'POST',
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Ablation study failed');
    return res.json();
  },

  // Admin
  getAdminHealth: async () => {
    const res = await fetch(`${API_BASE}/admin/health`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Admin health fetch failed');
    return res.json();
  },

  getAdminJobs: async () => {
    const res = await fetch(`${API_BASE}/admin/jobs`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Admin jobs fetch failed');
    return res.json();
  },

  getAdminRules: async () => {
    const res = await fetch(`${API_BASE}/admin/rules`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Admin rules fetch failed');
    return res.json();
  },
};
