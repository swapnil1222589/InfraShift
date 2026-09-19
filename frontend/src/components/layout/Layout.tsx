import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { AnalyzePRModal } from '../dashboard/AnalyzePRModal';

export const Layout: React.FC = () => {
  const [currentProjectId, setCurrentProjectId] = useState('proj-checkout-core');
  const [currentEnvId, setCurrentEnvId] = useState('env-prod');
  const [isAnalyzeModalOpen, setIsAnalyzeModalOpen] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Header
        currentProjectId={currentProjectId}
        onProjectChange={setCurrentProjectId}
        currentEnvId={currentEnvId}
        onEnvChange={setCurrentEnvId}
        onOpenAnalyzeModal={() => setIsAnalyzeModalOpen(true)}
      />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          collapsed={isSidebarCollapsed}
          onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        />
        <main className="flex-1 overflow-y-auto bg-slate-950/60 p-6">
          <div className="max-w-7xl mx-auto space-y-6">
            <Outlet context={{ currentProjectId, currentEnvId, openAnalyzeModal: () => setIsAnalyzeModalOpen(true) }} />
          </div>
        </main>
      </div>

      <AnalyzePRModal
        isOpen={isAnalyzeModalOpen}
        onClose={() => setIsAnalyzeModalOpen(false)}
        projectId={currentProjectId}
      />
    </div>
  );
};
