import React from 'react';
import { Card } from '../common/Card';
import { Target, CheckCircle2, ShieldCheck, Activity } from 'lucide-react';
import { DeploymentOutcome } from '../../types';

interface OutcomeSummaryProps {
  outcome: DeploymentOutcome;
}

export const OutcomeSummary: React.FC<OutcomeSummaryProps> = ({ outcome }) => {
  // Compute accuracy from cost error for mock purposes
  const accuracy = Math.max(0, 100 - outcome.costForecastErrorPct).toFixed(1);

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <Card className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-full bg-indigo-500/10 flex items-center justify-center shrink-0">
          <Activity className="w-6 h-6 text-indigo-400" />
        </div>
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 block mb-0.5">
            Forecast Confidence
          </span>
          <span className="text-xl font-bold font-mono text-slate-100">82%</span>
        </div>
      </Card>

      <Card className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-full bg-amber-500/10 flex items-center justify-center shrink-0">
          <Target className="w-6 h-6 text-amber-400" />
        </div>
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 block mb-0.5">
            Forecast Accuracy
          </span>
          <span className="text-xl font-bold font-mono text-amber-400">{accuracy}%</span>
        </div>
      </Card>

      <Card className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-full bg-emerald-500/10 flex items-center justify-center shrink-0">
          <CheckCircle2 className="w-6 h-6 text-emerald-400" />
        </div>
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 block mb-0.5">
            Deployment Result
          </span>
          <span className="text-lg font-bold text-slate-100">{outcome.deploymentResult}</span>
        </div>
      </Card>

      <Card className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-full bg-teal-500/10 flex items-center justify-center shrink-0">
          <ShieldCheck className="w-6 h-6 text-teal-400" />
        </div>
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 block mb-0.5">
            Validation Status
          </span>
          <span className="text-lg font-bold text-slate-100">{outcome.validationStatus}</span>
        </div>
      </Card>
    </div>
  );
};
