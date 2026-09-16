import React from 'react';
import { NavLink } from 'react-router-dom';
import { Search, FolderKanban, BarChart3, Settings, ShieldCheck, FileCheck } from 'lucide-react';

export const Sidebar: React.FC = () => {
  const navItems = [
    { to: '/', label: 'Search Workspace', icon: Search },
    { to: '/library', label: 'Corpus & Ingestion', icon: FolderKanban },
    { to: '/evaluation', label: 'Ablation Benchmark', icon: BarChart3 },
    { to: '/admin', label: 'Admin Telemetry', icon: Settings },
  ];

  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-900/40 p-4 flex flex-col justify-between">
      <div className="space-y-1">
        <div className="px-3 py-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
          Research Modules
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-gradient-to-r from-amber-500/20 to-transparent text-amber-400 border border-amber-500/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`
              }
            >
              <Icon className="w-4 h-4" />
              {item.label}
            </NavLink>
          );
        })}
      </div>

      <div className="p-4 rounded-xl glass-card space-y-2 border border-slate-800">
        <div className="flex items-center gap-2 text-xs font-semibold text-amber-400">
          <ShieldCheck className="w-4 h-4" /> Core Invariant Status
        </div>
        <p className="text-[11px] text-slate-400 leading-relaxed">
          Original Text Preservation guaranteed via character offset matrix indexing.
        </p>
        <div className="flex items-center gap-1.5 text-[10px] text-emerald-400 pt-1">
          <FileCheck className="w-3 h-3" /> <span className="font-mono">stored == original</span>
        </div>
      </div>
    </aside>
  );
};
