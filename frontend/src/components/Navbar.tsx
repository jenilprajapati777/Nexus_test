import React from 'react';
import { useAuth } from '../context/AuthContext';
import { BookOpen, LogOut, User as UserIcon, Shield, Layers } from 'lucide-react';

interface NavbarProps {
  activeScript: string;
  setActiveScript: (script: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeScript, setActiveScript }) => {
  const { user, logout } = useAuth();

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/80 backdrop-blur-md sticky top-0 z-40 px-6 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-amber-700 flex items-center justify-center text-slate-950 font-bold font-devanagari text-xl shadow-lg shadow-amber-950/40">
          सं
        </div>
        <div>
          <h1 className="text-lg font-semibold tracking-wide text-slate-100 flex items-center gap-2">
            Sanskrit IR Enhancement Platform
            <span className="text-xs px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">
              v1.0 Production
            </span>
          </h1>
          <p className="text-xs text-slate-400">Deterministic NLP Engine & Exact Offset Retrieval</p>
        </div>
      </div>

      <div className="flex items-center gap-6">
        {/* Script Selector */}
        <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-lg border border-slate-800 text-xs">
          <span className="text-slate-400 px-2 flex items-center gap-1">
            <Layers className="w-3.5 h-3.5 text-amber-400" /> Display Script:
          </span>
          {['Devanagari', 'IAST', 'SLP1'].map((script) => (
            <button
              key={script}
              onClick={() => setActiveScript(script)}
              className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                activeScript === script
                  ? 'bg-amber-500 text-slate-950 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
              }`}
            >
              {script}
            </button>
          ))}
        </div>

        {/* User Badge & Logout */}
        {user && (
          <div className="flex items-center gap-4 border-l border-slate-800 pl-6">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-amber-400">
                <UserIcon className="w-4 h-4" />
              </div>
              <div className="text-xs">
                <div className="font-medium text-slate-200">{user.email}</div>
                <div className="text-slate-400 capitalize flex items-center gap-1">
                  <Shield className="w-3 h-3 text-amber-400" /> {user.role}
                </div>
              </div>
            </div>
            <button
              onClick={logout}
              className="p-2 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition-colors"
              title="Sign Out"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </header>
  );
};
