import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Library } from './pages/Library';
import { SearchWorkspace } from './pages/SearchWorkspace';
import { EvaluationSuite } from './pages/EvaluationSuite';
import { AdminPanel } from './pages/AdminPanel';

const ProtectedLayout: React.FC<{ activeScript: string; setActiveScript: (s: string) => void }> = ({
  activeScript,
  setActiveScript,
}) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-[#090d16] flex items-center justify-center text-slate-400 text-sm">
        Initializing Sanskrit IR Environment...
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="min-h-screen flex flex-col bg-[#090d16]">
      <Navbar activeScript={activeScript} setActiveScript={setActiveScript} />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 bg-[#0b101c] overflow-y-auto">
          <Routes>
            <Route path="/" element={<SearchWorkspace activeScript={activeScript} />} />
            <Route path="/library" element={<Library />} />
            <Route path="/evaluation" element={<EvaluationSuite />} />
            <Route path="/admin" element={<AdminPanel />} />
          </Routes>
        </main>
      </div>
    </div>
  );
};

export const App: React.FC = () => {
  const [activeScript, setActiveScript] = useState('Devanagari');

  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/*"
            element={
              <ProtectedLayout activeScript={activeScript} setActiveScript={setActiveScript} />
            }
          />
        </Routes>
      </Router>
    </AuthProvider>
  );
};
export default App;
