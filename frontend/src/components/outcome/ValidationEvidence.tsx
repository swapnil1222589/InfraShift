import React from 'react';
import { Card } from '../common/Card';
import { DeploymentOutcome } from '../../types';
import { Activity, Clock, CheckCircle2 } from 'lucide-react';

interface ValidationEvidenceProps {
  outcome: DeploymentOutcome;
}

export const ValidationEvidence: React.FC<ValidationEvidenceProps> = ({ outcome }) => {
  const ev = outcome.validationEvidence;
  
  return (
    <Card className="flex flex-col h-full">
      <h3 className="text-base font-bold text-slate-100 font-sans tracking-tight mb-4">Validation Evidence</h3>
      
      <div className="space-y-3">
        <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900 border border-slate-800">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-emerald-400" />
            <span className="text-sm font-semibold text-slate-200">CloudWatch Metrics</span>
          </div>
          <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-bold uppercase">
            {ev.cloudWatchMetrics}
          </span>
        </div>

        <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900 border border-slate-800">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span className="text-sm font-semibold text-slate-200">Deployment Telemetry</span>
          </div>
          <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-bold uppercase">
            {ev.deploymentTelemetry}
          </span>
        </div>

        <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900 border border-slate-800">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-indigo-400" />
            <span className="text-sm font-semibold text-slate-200">Comparison Window</span>
          </div>
          <span className="text-xs font-mono text-slate-300">
            {ev.comparisonWindow}
          </span>
        </div>

        <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900 border border-slate-800">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-slate-400" />
            <span className="text-sm font-semibold text-slate-200">Baseline Window</span>
          </div>
          <span className="text-xs font-mono text-slate-300">
            {ev.baselineWindow}
          </span>
        </div>

        <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900 border border-slate-800">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span className="text-sm font-semibold text-slate-200">Historical Comparison</span>
          </div>
          <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-bold uppercase">
            {ev.historicalComparison}
          </span>
        </div>
      </div>
    </Card>
  );
};
