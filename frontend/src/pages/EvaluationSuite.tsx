import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { AblationReport, BenchmarkQuery } from '../types';
import { BarChart3, Play, TrendingUp, CheckCircle2, Plus, RefreshCw, Layers } from 'lucide-react';

export const EvaluationSuite: React.FC = () => {
  const [report, setReport] = useState<AblationReport | null>(null);
  const [benchmarks, setBenchmarks] = useState<BenchmarkQuery[]>([]);
  const [loading, setLoading] = useState(false);

  // New Benchmark Query Modal State
  const [showModal, setShowModal] = useState(false);
  const [newQueryText, setNewQueryText] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [newCategory, setNewCategory] = useState('Sandhi Resolution');

  useEffect(() => {
    fetchBenchmarks();
  }, []);

  const fetchBenchmarks = async () => {
    try {
      const data = await api.getBenchmarks();
      setBenchmarks(data);
    } catch (err) {
      console.error(err);
    }
  };

  const runAblationStudy = async () => {
    setLoading(true);
    try {
      const rep = await api.runAblation();
      setReport(rep);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddBenchmark = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newQueryText.trim()) return;

    try {
      await api.createBenchmark(newQueryText, newDesc, newCategory);
      setShowModal(false);
      setNewQueryText('');
      setNewDesc('');
      fetchBenchmarks();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-100 flex items-center gap-3">
            <BarChart3 className="w-7 h-7 text-amber-500" /> Information Retrieval Evaluation Suite
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Automated Ablation Study comparing Baseline Surface Search vs Enhanced Deterministic Sanskrit Engine.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowModal(true)}
            className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold rounded-xl text-xs flex items-center gap-2 transition-colors border border-slate-700"
          >
            <Plus className="w-4 h-4 text-amber-400" /> Add Custom Benchmark Query
          </button>

          <button
            onClick={runAblationStudy}
            disabled={loading}
            className="px-6 py-2.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 text-slate-950 font-bold rounded-xl text-xs uppercase tracking-wider transition-all shadow-lg shadow-amber-950/30 flex items-center gap-2"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" /> Running Benchmark Suite...
              </>
            ) : (
              <>
                <Play className="w-4 h-4" /> Run Ablation Study Benchmark
              </>
            )}
          </button>
        </div>
      </div>

      {/* Benchmark Summary Cards */}
      {report && (
        <div className="space-y-6">
          <div className="grid grid-cols-5 gap-4">
            {[
              { label: 'Precision@5', baseline: report.baseline_summary.precision, enhanced: report.enhanced_summary.precision, key: 'precision' },
              { label: 'Recall@5', baseline: report.baseline_summary.recall, enhanced: report.enhanced_summary.recall, key: 'recall' },
              { label: 'F1-Score', baseline: report.baseline_summary.f1, enhanced: report.enhanced_summary.f1, key: 'f1' },
              { label: 'MRR', baseline: report.baseline_summary.mrr, enhanced: report.enhanced_summary.mrr, key: 'mrr' },
              { label: 'nDCG@5', baseline: report.baseline_summary.ndcg, enhanced: report.enhanced_summary.ndcg, key: 'ndcg' },
            ].map((metric) => (
              <div key={metric.label} className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3 shadow-lg">
                <span className="text-xs font-semibold text-slate-400 block">{metric.label}</span>

                <div className="flex items-baseline justify-between">
                  <div>
                    <span className="text-2xl font-extrabold text-amber-400">{metric.enhanced}</span>
                    <span className="text-[10px] text-slate-500 block">ENHANCED</span>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-semibold text-slate-400">{metric.baseline}</span>
                    <span className="text-[10px] text-slate-500 block">BASELINE</span>
                  </div>
                </div>

                <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-xs">
                  <span className="text-emerald-400 font-bold flex items-center gap-1">
                    <TrendingUp className="w-3.5 h-3.5" /> +{report.improvements_pct[metric.key] || 0}%
                  </span>
                  <span className="text-[10px] text-slate-500">Gain</span>
                </div>
              </div>
            ))}
          </div>

          {/* Detailed Ablation Table */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-slate-200">Query-by-Query Metric Breakdown</h3>
              <span className="text-xs text-slate-400">{report.query_details.length} Queries Benchmarked</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px]">
                    <th className="py-3 px-4">Benchmark Query</th>
                    <th className="py-3 px-4">Description</th>
                    <th className="py-3 px-4">Baseline P@5</th>
                    <th className="py-3 px-4">Enhanced P@5</th>
                    <th className="py-3 px-4">Baseline nDCG</th>
                    <th className="py-3 px-4">Enhanced nDCG</th>
                    <th className="py-3 px-4 text-right">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {report.query_details.map((qd, idx) => (
                    <tr key={idx} className="hover:bg-slate-800/40">
                      <td className="py-3.5 px-4 font-devanagari text-slate-200 font-semibold">{qd.query}</td>
                      <td className="py-3.5 px-4 text-slate-400">{qd.description}</td>
                      <td className="py-3.5 px-4 font-mono text-slate-400">{qd.baseline.precision}</td>
                      <td className="py-3.5 px-4 font-mono text-amber-400 font-bold">{qd.enhanced.precision}</td>
                      <td className="py-3.5 px-4 font-mono text-slate-400">{qd.baseline.ndcg}</td>
                      <td className="py-3.5 px-4 font-mono text-emerald-400 font-bold">{qd.enhanced.ndcg}</td>
                      <td className="py-3.5 px-4 text-right">
                        <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px]">
                          Evaluated
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Registered Benchmarks Dataset Section */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-slate-200">Registered Gold-Standard Evaluation Queries</h3>
            <p className="text-xs text-slate-400">Total {benchmarks.length} Test Words Registered</p>
          </div>
          <button
            onClick={runAblationStudy}
            className="px-3 py-1.5 bg-amber-500/10 text-amber-300 border border-amber-500/20 hover:bg-amber-500/20 rounded-lg text-xs transition-colors"
          >
            Run All Benchmarks
          </button>
        </div>

        <div className="grid grid-cols-2 gap-4">
          {benchmarks.map((bq) => (
            <div key={bq.id} className="p-4 rounded-xl glass-card border border-slate-800 space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-devanagari text-sm font-bold text-amber-400">{bq.query_text}</span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
                  {bq.category}
                </span>
              </div>
              <p className="text-xs text-slate-400">{bq.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Modal to Add Custom Benchmark Query */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
            <h3 className="text-base font-semibold text-slate-100">Add Benchmark Test Query</h3>
            <form onSubmit={handleAddBenchmark} className="space-y-3">
              <div>
                <label className="text-xs font-medium text-slate-400 block mb-1">Query Word / Term</label>
                <input
                  type="text"
                  placeholder="e.g., purusottama, yadyapi, krishnasya"
                  value={newQueryText}
                  onChange={(e) => setNewQueryText(e.target.value)}
                  required
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-slate-200 font-devanagari focus:outline-none focus:border-amber-500"
                />
              </div>

              <div>
                <label className="text-xs font-medium text-slate-400 block mb-1">Category</label>
                <select
                  value={newCategory}
                  onChange={(e) => setNewCategory(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-slate-200 focus:outline-none focus:border-amber-500"
                >
                  <option value="Sandhi Resolution">Sandhi Resolution</option>
                  <option value="Morphology Declension">Morphology Declension</option>
                  <option value="Morphology Conjugation">Morphology Conjugation</option>
                  <option value="Samasa Compound">Samasa Compound</option>
                  <option value="Unicode Normalization">Unicode Normalization</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-medium text-slate-400 block mb-1">Description / Linguistic Intent</label>
                <textarea
                  placeholder="e.g., Evaluation of Guna Sandhi split (purusa + uttama)"
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-slate-200 focus:outline-none focus:border-amber-500 h-20"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 rounded-xl text-xs hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-amber-500 text-slate-950 font-semibold rounded-xl text-xs hover:bg-amber-600"
                >
                  Add Query to Suite
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
