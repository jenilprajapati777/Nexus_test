export interface User {
  id: string;
  email: string;
  role: string;
  created_at: string;
}

export interface Corpus {
  id: string;
  title: string;
  description?: string;
  owner_id: string;
  document_count: number;
  created_at: string;
}

export interface DocumentItem {
  id: string;
  corpus_id: string;
  title: string;
  author: string;
  chapter: string;
  file_name: string;
  file_type: string;
  character_count: number;
  word_count: number;
  created_at: string;
  original_text: string;
}

export interface JobStatus {
  id: string;
  document_id: string;
  corpus_id: string;
  status: string; // Uploaded | Processing | Indexing | Ready | Failed
  current_step: string;
  progress_pct: number;
  error_message?: string;
}

export interface HighlightSpan {
  start_char: number;
  end_char: number;
  matched_text: string;
  matched_type: string;
  matched_term: string;
}

export interface SearchHit {
  doc_id: string;
  score: number;
  title: string;
  author: string;
  chapter: string;
  corpus_id: string;
  original_text: string;
  snippet: string;
  highlights: HighlightSpan[];
  match_count: number;
  match_details: any[];
}

export interface SearchResponse {
  query: string;
  mode: string;
  total_hits: number;
  hits: SearchHit[];
}

export interface ExplanationStep {
  step: number;
  surface_token: string;
  matched_type: string;
  matched_term: string;
  start_char: number;
  end_char: number;
  explanation: string;
  rule_info: any;
}

export interface ExplainResponse {
  doc_id: string;
  query: string;
  total_score: number;
  total_matches: number;
  explanation_steps: ExplanationStep[];
}

export interface BenchmarkQuery {
  id: string;
  query_text: string;
  description: string;
  category: string;
  gold_relevance: Record<string, number>;
}

export interface MetricSummary {
  precision: number;
  recall: number;
  f1: number;
  mrr: number;
  ndcg: number;
}

export interface AblationReport {
  total_queries_evaluated: number;
  baseline_summary: MetricSummary;
  enhanced_summary: MetricSummary;
  improvements_pct: Record<string, number>;
  query_details: any[];
}
