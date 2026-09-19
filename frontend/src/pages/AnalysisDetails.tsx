import React from 'react';
import { useParams, useLocation, Link } from 'react-router-dom';
import { useAnalysis } from '../hooks/useAnalysis';
import { Breadcrumbs } from '../components/navigation/Breadcrumbs';
import { TabNav } from '../components/navigation/TabNav';
import { AnalysisHeader } from '../components/analysis/AnalysisHeader';
import { Timeline } from '../components/analysis/Timeline';
import { ChangeSummary } from '../components/analysis/ChangeSummary';
import { CostForecastCard } from '../components/forecast/CostForecastCard';
import { PerformanceForecastCard } from '../components/forecast/PerformanceForecastCard';
import { ImpactGraphView } from '../components/impact/ImpactGraphView';
import { EvidenceSection } from '../components/evidence/EvidenceSection';
import { RecommendationsSection } from '../components/recommendations/RecommendationsSection';
import { OutcomeSection } from '../components/outcome/OutcomeSection';
import { LoadingState, ErrorState } from '../components/common/States';
import { ArrowRight, Network, FileQuestion, ShieldCheck, CheckCircle2 } from 'lucide-react';

export const AnalysisDetails: React.FC = () => {
  const { id = 'analysis-pr-248' } = useParams<{ id: string }>();
  const location = useLocation();

  const {
    analysis,
    forecast,
    impactGraph,
    evidence,
    recommendations,
    decision,
    outcome,
    loading,
    error,
    refresh,
    makeDecision,
  } = useAnalysis(id);

  if (loading) {
    return (
      <div className="py-20">
        <LoadingState
          message={`Correlating PR #${id.replace('analysis-pr-', '')} with AWS telemetry...`}
          subtext="Synthesizing CloudWatch metrics, AST diff, and DynamoDB secondary index mutations"
        />
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="py-12">
        <ErrorState
          error={error || `Analysis "${id}" could not be found.`}
          onRetry={refresh}
        />
      </div>
    );
  }

  // Determine subroute view
  const pathname = location.pathname;
  const isImpactRoute = pathname.endsWith('/impact');
  const isForecastRoute = pathname.endsWith('/forecast');
  const isEvidenceRoute = pathname.endsWith('/evidence');
  const isRecommendationsRoute = pathname.endsWith('/recommendations');
  const isOverviewRoute = !isImpactRoute && !isForecastRoute && !isEvidenceRoute && !isRecommendationsRoute;

  return (
    <div className="space-y-6">
      {/* Breadcrumbs */}
      <Breadcrumbs />

      {/* Header */}
      <AnalysisHeader analysis={analysis} onRefresh={refresh} />

      {/* Timeline Progress */}
      {analysis.timeline && <Timeline steps={analysis.timeline} />}

      {/* Tab Navigation for Subroutes */}
      <TabNav recommendationsCount={recommendations.length} />

      {/* Route Views */}
      <div className="pt-2">
        {isOverviewRoute && (
          <div className="space-y-6">
            {/* Section 1: Change Summary */}
            {analysis.summary && <ChangeSummary summary={analysis.summary} />}

            {/* Section 2: Impact Summary (Cost & Performance Cards) */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-base font-bold text-slate-100 font-sans tracking-tight">
                    SECTION 2 — Infrastructure Impact Summary
                  </h2>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Calibrated ranges for monthly cost and tail latency
                  </p>
                </div>
                <Link
                  to={`/analyses/${id}/forecast`}
                  className="text-xs font-medium text-amber-400 hover:text-amber-300 inline-flex items-center gap-1 font-mono"
                >
                  <span>Detailed Forecast Breakdown</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {forecast && <CostForecastCard cost={forecast.cost} />}
                {forecast && <PerformanceForecastCard performance={forecast.performance} />}
              </div>
            </div>

            {/* Quick Teaser for Impact Graph */}
            <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20 shrink-0">
                  <Network className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-slate-100 font-sans">
                    SECTION 3 — Interactive AWS Impact Graph
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Explore visual dependency chains from GitHub PR diff to DynamoDB and Lambda workers.
                  </p>
                </div>
              </div>
              <Link
                to={`/analyses/${id}/impact`}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition shrink-0"
              >
                <span>Launch Graph</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            {/* Section: Deployment Outcome (Forecast vs Actual) */}
            {outcome && (
              <div className="pt-4 border-t border-slate-800/80">
                <OutcomeSection outcome={outcome} />
              </div>
            )}
          </div>
        )}

        {isImpactRoute && (
          <div className="space-y-4">
            <div>
              <h2 className="text-base font-bold text-slate-100 font-sans tracking-tight">
                SECTION 3 — AWS Architecture Impact Graph
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Trace the causal blast radius from PR code diffs to AWS cloud resources.
              </p>
            </div>
            {impactGraph && <ImpactGraphView data={impactGraph} />}
          </div>
        )}

        {isForecastRoute && (
          <div className="space-y-6">
            <div>
              <h2 className="text-base font-bold text-slate-100 font-sans tracking-tight">
                SECTION 2 — Cost & Performance Range Forecast
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Non-parametric projection ranges calibrated against 14 days of CloudWatch telemetry.
              </p>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {forecast && <CostForecastCard cost={forecast.cost} />}
              {forecast && <PerformanceForecastCard performance={forecast.performance} />}
            </div>
          </div>
        )}

        {isEvidenceRoute && (
          <div className="space-y-4">
            <div>
              <h2 className="text-xl font-bold text-slate-100 font-sans tracking-tight">
                Why This Forecast?
              </h2>
              <p className="text-sm text-slate-400 mt-0.5">
                Understand the evidence, assumptions and signals behind the predicted infrastructure impact.
              </p>
            </div>
            {evidence && <EvidenceSection evidence={evidence} />}
          </div>
        )}

        {isRecommendationsRoute && (
          <div className="space-y-4">
            <div>
              <h2 className="text-xl font-bold text-slate-100 font-sans tracking-tight">
                Recommendations
              </h2>
              <p className="text-sm text-slate-400 mt-0.5">
                Actions to validate and reduce potential infrastructure impact before deployment.
              </p>
            </div>
            <RecommendationsSection
              recommendations={recommendations}
              decision={decision}
              onDecision={makeDecision}
            />
          </div>
        )}
      </div>
    </div>
  );
};
