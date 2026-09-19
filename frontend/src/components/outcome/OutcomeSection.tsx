import React from 'react';
import { DeploymentOutcome } from '../../types';
import { StatusBadge } from '../common/StatusBadge';
import { OutcomeSummary } from './OutcomeSummary';
import { ForecastActualChart } from './ForecastActualChart';
import { PerformanceImpactChart } from './PerformanceImpactChart';
import { MetricComparison } from './MetricComparison';
import { ForecastErrorCard } from './ForecastErrorCard';
import { ValidationTimeline } from './ValidationTimeline';
import { ValidationEvidence } from './ValidationEvidence';
import { Info } from 'lucide-react';

interface OutcomeSectionProps {
  outcome: DeploymentOutcome;
}

export const OutcomeSection: React.FC<OutcomeSectionProps> = ({ outcome }) => {
  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      
      {/* Top Banner Explaining Distinction */}
      <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="p-2 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 shrink-0">
            <Info className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-100 font-sans">
              What happened?
            </h3>
            <p className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
              Deployment was <strong className="text-emerald-400 font-semibold">Successful</strong>. 
              Infrastructure Impact and Performance were <strong className="text-emerald-400 font-semibold">Within predicted range</strong>. 
              CloudWatch telemetry was available. Overall, the {outcome.postMortemNotes}.
            </p>
          </div>
        </div>

        <div className="shrink-0 flex items-center gap-3">
          <StatusBadge status="verified" size="md" />
        </div>
      </div>

      <OutcomeSummary outcome={outcome} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ForecastActualChart title="Cloud Cost Impact" data={outcome.chartData} />
        <PerformanceImpactChart outcome={outcome} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3">
          <MetricComparison outcome={outcome} />
        </div>
        <div className="lg:col-span-1">
          <ForecastErrorCard outcome={outcome} />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <ValidationTimeline outcome={outcome} />
        <ValidationEvidence outcome={outcome} />
      </div>

    </div>
  );
};
