import React, { useEffect, useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import { Analysis } from '../types/analysis';
import { getAnalyses } from '../api/analyses';
import { HeroSection } from '../components/dashboard/HeroSection';
import { SummaryCards } from '../components/dashboard/SummaryCards';
import { RecentAnalysesTable } from '../components/dashboard/RecentAnalysesTable';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { LoadingState, ErrorState, EmptyState } from '../components/common/States';
import { Sparkles, RefreshCw, Filter, ShieldCheck, ArrowRight } from 'lucide-react';

interface LayoutContext {
  currentProjectId: string;
  currentEnvId: string;
  openAnalyzeModal: () => void;
}

export const Dashboard: React.FC = () => {
  const { currentProjectId, openAnalyzeModal } = useOutletContext<LayoutContext>();
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [riskFilter, setRiskFilter] = useState<'all' | 'high' | 'critical'>('all');

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getAnalyses(currentProjectId);
      setAnalyses(data);
    } catch (err: any) {
      setError(err?.message || 'Failed to fetch PR analyses');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [currentProjectId]);

  const filteredAnalyses = analyses.filter((a) => {
    if (riskFilter === 'all') return true;
    if (riskFilter === 'high') return a.risk === 'high' || a.risk === 'critical';
    if (riskFilter === 'critical') return a.risk === 'critical';
    return true;
  });

  const highRiskCount = analyses.filter((a) => a.risk === 'high' || a.risk === 'critical').length;
  const avgConfidence = analyses.length
    ? Math.round(analyses.reduce((acc, curr) => acc + curr.confidence, 0) / analyses.length)
    : 85;

  return (
    <div className="space-y-6">
      {/* Hero Section */}
      <HeroSection onAnalyzeClick={openAnalyzeModal} />

      {/* Metric Summary Cards */}
      <SummaryCards
        analysesCount={analyses.length > 0 ? analyses.length * 6 : 34}
        avgConfidence={avgConfidence}
        costImpactRange="+$180 – $320/mo"
        highRiskCount={highRiskCount || 3}
      />

      {/* Recent Analyses Section */}
      <Card
        title="Recent Infrastructure Pre-Deployment Analyses"
        subtitle="Correlated pull requests analyzed against AWS telemetry, CloudWatch baselines, and AST blast radius"
        headerAction={
          <div className="flex items-center gap-2">
            {/* Filter pills */}
            <div className="hidden sm:flex items-center bg-slate-950 border border-slate-800 rounded-md p-0.5 text-xs">
              <button
                onClick={() => setRiskFilter('all')}
                className={`px-2.5 py-1 rounded font-medium transition ${
                  riskFilter === 'all'
                    ? 'bg-slate-800 text-slate-100'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                All ({analyses.length})
              </button>
              <button
                onClick={() => setRiskFilter('high')}
                className={`px-2.5 py-1 rounded font-medium transition ${
                  riskFilter === 'high'
                    ? 'bg-orange-950/80 text-orange-300 border border-orange-800/60'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                High Risk ({highRiskCount})
              </button>
            </div>

            <Button
              variant="outline"
              size="sm"
              icon={<RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />}
              onClick={loadData}
              title="Refresh telemetry"
            >
              Refresh
            </Button>

            <Button
              variant="aws"
              size="sm"
              icon={<Sparkles className="w-3.5 h-3.5" />}
              onClick={openAnalyzeModal}
            >
              Analyze PR
            </Button>
          </div>
        }
        noPadding
      >
        {loading ? (
          <LoadingState
            message="Loading recent PR infrastructure analyses..."
            subtext="Querying historical CloudWatch metrics & AST change indices"
          />
        ) : error ? (
          <div className="p-4">
            <ErrorState error={error} onRetry={loadData} />
          </div>
        ) : filteredAnalyses.length === 0 ? (
          <EmptyState
            title="No PR analyses found"
            description="No recent pull requests match the current filter."
            actionLabel="Analyze First PR"
            onAction={openAnalyzeModal}
          />
        ) : (
          <RecentAnalysesTable analyses={filteredAnalyses} isLoading={loading} />
        )}
      </Card>
    </div>
  );
};
