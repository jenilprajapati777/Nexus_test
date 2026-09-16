import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { SearchResponse, SearchHit, ExplainResponse, Corpus } from '../types';
import { HighlightedText } from '../components/HighlightedText';
import { ExplainModal } from '../components/ExplainModal';
import { Search, SlidersHorizontal, Sparkles, Cpu, Layers, BookOpen, User, Bookmark } from 'lucide-react';

interface SearchWorkspaceProps {
  activeScript: string;
}

export const SearchWorkspace: React.FC<SearchWorkspaceProps> = ({ activeScript }) => {
  const [query, setQuery] = useState('hitopadesa');
  const [searchMode, setSearchMode] = useState<'baseline' | 'enhanced'>('enhanced');
  const [corpora, setCorpora] = useState<Corpus[]>([]);
  const [selectedCorpusIds, setSelectedCorpusIds] = useState<string[]>([]);
  const [authorFilter, setAuthorFilter] = useState('');
  const [chapterFilter, setChapterFilter] = useState('');

  const [results, setResults] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);

  // Explain Modal State
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);
  const [explainData, setExplainData] = useState<ExplainResponse | null>(null);
  const [explainLoading, setExplainLoading] = useState(false);
  const [isExplainOpen, setIsExplainOpen] = useState(false);

  useEffect(() => {
    api.getCorpora().then(setCorpora).catch(console.error);
    handleSearch();
  }, []);

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    try {
      const res = await api.search({
        query,
        mode: searchMode,
        corpus_ids: selectedCorpusIds.length > 0 ? selectedCorpusIds : undefined,
        author_filter: authorFilter || undefined,
        chapter_filter: chapterFilter || undefined,
        top_k: 15,
      });
      setResults(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleExplain = async (docId: string) => {
    setSelectedDocId(docId);
    setIsExplainOpen(true);
    setExplainLoading(true);

    try {
      const data = await api.explain(docId, query);
      setExplainData(data);
    } catch (err) {
      console.error(err);
    } finally {
      setExplainLoading(false);
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Top Search Bar */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4 shadow-xl">
        <form onSubmit={handleSearch} className="flex gap-3">
          <div className="relative flex-1">
            <Search className="w-5 h-5 text-amber-400 absolute left-4 top-3.5" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search Sanskrit literature (e.g., hitopadesa, rāmeṇa, गच्छति, rājalakṣmī)..."
              className="w-full bg-slate-950/80 border border-slate-800 rounded-2xl py-3 pl-12 pr-4 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500 transition-colors font-devanagari"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="px-6 py-3 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-slate-950 font-bold rounded-2xl text-xs uppercase tracking-wider transition-all shadow-lg shadow-amber-950/30 flex items-center gap-2"
          >
            {loading ? 'Searching Index...' : 'Run Search Query'}
          </button>
        </form>

        {/* Mode Selector & Quick Filter Pills */}
        <div className="flex items-center justify-between border-t border-slate-800/80 pt-4 text-xs">
          <div className="flex items-center gap-2">
            <span className="text-slate-400 font-medium">Search Strategy:</span>
            <button
              type="button"
              onClick={() => setSearchMode('baseline')}
              className={`px-3 py-1.5 rounded-xl font-medium transition-all ${
                searchMode === 'baseline'
                  ? 'bg-slate-800 text-slate-200 border border-slate-700'
                  : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              Baseline (Exact Lexical Surface)
            </button>
            <button
              type="button"
              onClick={() => setSearchMode('enhanced')}
              className={`px-3 py-1.5 rounded-xl font-medium flex items-center gap-1.5 transition-all ${
                searchMode === 'enhanced'
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-sm'
                  : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              <Sparkles className="w-3.5 h-3.5 text-amber-400" /> Enhanced (Sandhi, Morphology & Samasa)
            </button>
          </div>

          <div className="text-slate-400 text-[11px]">
            Mode: <span className="font-semibold text-slate-200 uppercase">{searchMode}</span> • Results Preserved in Original Text
          </div>
        </div>
      </div>

      {/* Main Grid: Filters Sidebar + Results List */}
      <div className="grid grid-cols-12 gap-8">
        {/* Sidebar Filters */}
        <div className="col-span-3 space-y-4">
          <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-2">
              <SlidersHorizontal className="w-4 h-4 text-amber-400" /> Search Filters
            </h3>

            {/* Author Filter */}
            <div className="space-y-1">
              <label className="text-[11px] font-medium text-slate-400">Author Filter</label>
              <input
                type="text"
                placeholder="e.g., Vyasa, Narayana"
                value={authorFilter}
                onChange={(e) => setAuthorFilter(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
              />
            </div>

            {/* Chapter Filter */}
            <div className="space-y-1">
              <label className="text-[11px] font-medium text-slate-400">Chapter / Section</label>
              <input
                type="text"
                placeholder="e.g., Prathama, Chapter 1"
                value={chapterFilter}
                onChange={(e) => setChapterFilter(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
              />
            </div>

            {/* Corpora Checkboxes */}
            <div className="space-y-2 pt-2 border-t border-slate-800/80">
              <label className="text-[11px] font-medium text-slate-400 block">Corpora Scope</label>
              {corpora.map((corp) => (
                <label key={corp.id} className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedCorpusIds.includes(corp.id)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedCorpusIds([...selectedCorpusIds, corp.id]);
                      } else {
                        setSelectedCorpusIds(selectedCorpusIds.filter((id) => id !== corp.id));
                      }
                    }}
                    className="rounded bg-slate-950 border-slate-800 text-amber-500 focus:ring-0"
                  />
                  <span>{corp.title}</span>
                </label>
              ))}
            </div>

            <button
              onClick={() => handleSearch()}
              className="w-full py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium rounded-xl text-xs transition-colors"
            >
              Apply Filters
            </button>
          </div>
        </div>

        {/* Results List */}
        <div className="col-span-9 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-200">
              Query Results for "{results?.query || query}"
            </h3>
            <span className="text-xs text-slate-400">
              {results?.total_hits || 0} Passages Matched
            </span>
          </div>

          {loading ? (
            <div className="py-20 text-center text-slate-400 space-y-3">
              <div className="w-8 h-8 border-2 border-amber-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
              Evaluating Multi-Layer Inverted Index...
            </div>
          ) : results && results.hits.length > 0 ? (
            results.hits.map((hit) => (
              <div
                key={hit.doc_id}
                className="glass-panel p-6 rounded-2xl border border-slate-800 hover:border-slate-700 transition-all space-y-4 shadow-lg"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="text-base font-bold text-slate-100 flex items-center gap-2">
                      <BookOpen className="w-4 h-4 text-amber-400" /> {hit.title}
                    </h4>
                    <div className="flex items-center gap-3 text-xs text-slate-400 mt-1">
                      <span>Author: {hit.author}</span>
                      <span>•</span>
                      <span>Section: {hit.chapter}</span>
                      <span>•</span>
                      <span className="text-emerald-400 font-mono">Relevance Score: {hit.score}</span>
                    </div>
                  </div>

                  <button
                    onClick={() => handleExplain(hit.doc_id)}
                    className="px-3 py-1.5 bg-amber-500/10 border border-amber-500/30 hover:bg-amber-500/20 text-amber-300 font-semibold rounded-xl text-xs flex items-center gap-1.5 transition-all shadow-sm"
                  >
                    <Cpu className="w-3.5 h-3.5" /> Explain Match
                  </button>
                </div>

                {/* Match Highlighting on Original Text */}
                <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800/80 font-devanagari text-sm">
                  <HighlightedText originalText={hit.snippet} highlights={hit.highlights} />
                </div>

                {/* Match Highlights Badge Summary */}
                <div className="flex flex-wrap gap-2 text-[10px]">
                  {hit.highlights.map((h, i) => (
                    <span
                      key={i}
                      className="px-2 py-0.5 rounded bg-slate-900 text-slate-300 border border-slate-800 font-mono"
                    >
                      {h.matched_type}: "{h.matched_text}" [{h.start_char}:{h.end_char}]
                    </span>
                  ))}
                </div>
              </div>
            ))
          ) : (
            <div className="glass-panel p-16 rounded-2xl border border-slate-800 text-center space-y-3">
              <Search className="w-10 h-10 mx-auto text-slate-600" />
              <h4 className="text-base font-semibold text-slate-300">No Matched Passages</h4>
              <p className="text-xs text-slate-500 max-w-sm mx-auto">
                No literature passages matched your query terms. Try switching to <strong>Enhanced Search</strong> or ingest additional Sanskrit literature in the Library.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Explain Trace Modal */}
      <ExplainModal
        isOpen={isExplainOpen}
        onClose={() => setIsExplainOpen(false)}
        explainData={explainData}
        loading={explainLoading}
      />
    </div>
  );
};
