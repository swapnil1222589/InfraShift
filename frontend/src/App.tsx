import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { Dashboard } from './pages/Dashboard';
import { Analyses } from './pages/Analyses';
import { AnalysisDetails } from './pages/AnalysisDetails';
import { History } from './pages/History';
import { Settings } from './pages/Settings';
import { Login } from './pages/Login';
import { GithubAuthorize } from './pages/GithubAuthorize';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { AuthProvider } from './contexts/AuthContext';
import { ToastProvider } from './contexts/ToastContext';

export function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/github-authorize" element={<GithubAuthorize />} />
            <Route path="/" element={<ProtectedRoute />}>
              <Route element={<Layout />}>
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard" element={<Dashboard />} />
                <Route path="analyses" element={<Analyses />} />
                <Route path="analyses/:id" element={<AnalysisDetails />} />
                <Route path="analyses/:id/impact" element={<AnalysisDetails />} />
                <Route path="analyses/:id/forecast" element={<AnalysisDetails />} />
                <Route path="analyses/:id/evidence" element={<AnalysisDetails />} />
                <Route path="analyses/:id/recommendations" element={<AnalysisDetails />} />
                <Route path="analyses/:id/outcome" element={<AnalysisDetails />} />
                <Route path="history" element={<History />} />
                <Route path="settings" element={<Settings />} />
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
              </Route>
            </Route>
          </Routes>
        </BrowserRouter>
      </ToastProvider>
    </AuthProvider>
  );
}

export default App;
