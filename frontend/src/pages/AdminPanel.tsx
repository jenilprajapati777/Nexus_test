import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Settings, Activity, Database, Cpu, FileCheck, Layers, RefreshCw } from 'lucide-react';

export const AdminPanel: React.FC = () => {
  const [health, setHealth] = useState<any>(null);
  const [jobs, setJobs] = useState<any[]>([]);
  const [rules, setRules] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAdminData();
  }, []);

  const fetchAdminData = async () => {
    setLoading(true);
    try {
      const [hData, jData, rData] = await Promise.all([
        api.getAdminHealth(),
        api.getAdminJobs(),
        api.getAdminRules(),
      ]);
      setHealth(hData);
      setJobs(jData);
      setRules(rData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-100 flex items-center gap-3">
            <Settings className="w-7 h-7 text-amber-500" /> Admin & System Telemetry
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            System status monitoring, document ingestion job logs, and Sanskrit NLP rule registry.
          </p>
        </div>

        <button
          onClick={fetchAdminData}
          className="p-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs flex items-center gap-2 transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> Refresh Telemetry
        </button>
      </div>

      {/* System Telemetry Cards */}
      {health && (
        <div className="grid grid-cols-4 gap-4">
          <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400 font-medium">
              <span>System Health</span>
              <Activity className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-xl font-bold text-emerald-400">{health.status}</div>
            <p className="text-[11px] text-slate-500">{health.database}</p>
          </div>

          <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400 font-medium">
              <span>Total Documents</span>
              <FileCheck className="w-4 h-4 text-amber-400" />
            </div>
            <div className="text-xl font-bold text-slate-100">{health.telemetry.total_documents}</div>
            <p className="text-[11px] text-slate-500">{health.telemetry.total_corpora} Corpora</p>
          </div>

          <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400 font-medium">
              <span>Indexed Terms</span>
              <Database className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="text-xl font-bold text-cyan-400">{health.telemetry.total_indexed_terms}</div>
            <p className="text-[11px] text-slate-500">Multi-Layer Index</p>
          </div>

          <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400 font-medium">
              <span>Active Users</span>
              <Cpu className="w-4 h-4 text-amber-400" />
            </div>
            <div className="text-xl font-bold text-slate-100">{health.telemetry.total_users}</div>
            <p className="text-[11px] text-slate-500">JWT Isolated</p>
          </div>
        </div>
      )}

      {/* Grid: Job Monitor + Rule Engine */}
      <div className="grid grid-cols-12 gap-8">
        {/* Job Monitor */}
        <div className="col-span-6 space-y-4">
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
            <h3 className="text-sm font-semibold text-slate-200">Ingestion Job Queue Logs</h3>
            <div className="space-y-3 max-h-96 overflow-y-auto pr-1">
              {jobs.map((job) => (
                <div key={job.id} className="p-3.5 rounded-xl glass-card border border-slate-800 space-y-2 text-xs">
                  <div className="flex items-center justify-between font-medium">
                    <span className="text-slate-200">Document ID: {job.document_id.slice(0, 8)}...</span>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${
                        job.status === 'Ready'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      }`}
                    >
                      {job.status}
                    </span>
                  </div>
                  <p className="text-slate-400 text-[11px]">{job.current_step}</p>
                  <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-amber-500 to-cyan-500"
                      style={{ width: `${job.progress_pct}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Linguistic Rule Registry */}
        <div className="col-span-6 space-y-4">
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
            <h3 className="text-sm font-semibold text-slate-200">Active Deterministic Rule Engine</h3>
            <div className="space-y-3 max-h-96 overflow-y-auto pr-1">
              {rules.map((rule) => (
                <div key={rule.id} className="p-3.5 rounded-xl glass-card border border-slate-800 space-y-1 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-amber-400 font-bold">{rule.rule_code}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400">{rule.category}</span>
                  </div>
                  <p className="text-slate-300 font-medium">{rule.description}</p>
                  <div className="text-[10px] font-mono text-slate-500">Pattern: {rule.pattern}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
