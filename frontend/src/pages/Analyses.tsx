import React, { useEffect, useState } from 'react';
import { useOutletContext, Link } from 'react-router-dom';
import { Analysis } from '../types/analysis';
import { getAnalyses } from '../api/analyses';
import { Card } from '../components/common/Card';
import { RecentAnalysesTable } from '../components/dashboard/RecentAnalysesTable';
import { Button } from '../components/common/Button';
import { LoadingState } from '../components/common/States';
import { Sparkles, GitPullRequest, ArrowRight } from 'lucide-react';

interface LayoutContext {
  currentProjectId: string;
  openAnalyzeModal: () => void;
}

export const Analyses: React.FC = () => {
  const { currentProjectId, openAnalyzeModal } = useOutletContext<LayoutContext>();
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAnalyses(currentProjectId).then((data) => {
      setAnalyses(data);
      setLoading(false);
    });
  }, [currentProjectId]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 font-sans tracking-tight">
            Pull Request Analyses
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            All code changes mapped to AWS resources, CloudWatch telemetry, and forecast models.
          </p>
        </div>
        <Button variant="aws" size="sm" icon={<Sparkles className="w-3.5 h-3.5" />} onClick={openAnalyzeModal}>
          Analyze Pull Request
        </Button>
      </div>

      <Card noPadding>
        {loading ? (
          <LoadingState message="Fetching all repository PR analyses..." />
        ) : (
          <RecentAnalysesTable analyses={analyses} />
        )}
      </Card>
    </div>
  );
};
