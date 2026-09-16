import React from 'react';
import { ExplainResponse } from '../types';
import { X, Cpu, CheckCircle2, HelpCircle, Code2 } from 'lucide-react';

interface ExplainModalProps {
  isOpen: boolean;
  onClose: () => void;
  explainData: ExplainResponse | null;
  loading: boolean;
}

export const ExplainModal: React.FC<ExplainModalProps> = ({
  isOpen,
  onClose,
  explainData,
  loading,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden glass-panel">
        <div className="p-6 border-b border-slate-800 flex items-center justify-between bg-slate-950/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                Deterministic Linguistic Explanation
              </h3>
              <p className="text-xs text-slate-400">Rule Trace for Query: "{explainData?.query}"</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 max-h-[70vh] overflow-y-auto space-y-4">
          {loading ? (
            <div className="py-12 text-center text-slate-400 flex flex-col items-center gap-3">
              <div className="w-8 h-8 border-2 border-amber-500 border-t-transparent rounded-full animate-spin"></div>
              Computing NLP Rule Resolution Trace...
            </div>
          ) : explainData && explainData.explanation_steps.length > 0 ? (
            explainData.explanation_steps.map((step, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl glass-card border border-slate-800 hover:border-slate-700 transition-all space-y-2"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-amber-400 flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Step {step.step}: {step.matched_type}
                  </span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                    Char Offset [{step.start_char}:{step.end_char}]
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-3 text-xs bg-slate-950/60 p-3 rounded-lg border border-slate-800">
                  <div>
                    <span className="text-slate-500 block text-[10px]">SURFACE TOKEN</span>
                    <span className="font-devanagari text-slate-200 font-semibold">{step.surface_token}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[10px]">MATCHED TERM</span>
                    <span className="font-devanagari text-amber-300 font-semibold">{step.matched_term}</span>
                  </div>
                </div>

                <p className="text-xs text-slate-300 leading-relaxed font-sans">{step.explanation}</p>

                {step.rule_info && Object.keys(step.rule_info).length > 0 && (
                  <div className="text-[11px] text-slate-400 bg-slate-950/40 p-2.5 rounded border border-slate-800/80 font-mono space-y-1">
                    <div className="flex items-center gap-1 text-[10px] text-slate-500 font-sans">
                      <Code2 className="w-3 h-3 text-cyan-400" /> Rule Metadata:
                    </div>
                    <div>Code: {step.rule_info.rule_id || step.rule_info.rule_code || 'NLP_RULE'}</div>
                    {step.rule_info.split_parts && <div>Splits: {JSON.stringify(step.rule_info.split_parts)}</div>}
                    {step.rule_info.case_tense && <div>Grammar: {step.rule_info.case_tense} ({step.rule_info.number_person})</div>}
                  </div>
                )}
              </div>
            ))
          ) : (
            <div className="py-8 text-center text-slate-400 flex flex-col items-center gap-2">
              <HelpCircle className="w-8 h-8 text-slate-600" />
              No rule resolution steps found for this document match.
            </div>
          )}
        </div>

        <div className="p-4 border-t border-slate-800 bg-slate-950/50 flex justify-between items-center text-xs text-slate-400">
          <span>Score Weight: {explainData?.total_score || 0}</span>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg font-medium transition-colors"
          >
            Close Trace
          </button>
        </div>
      </div>
    </div>
  );
};
