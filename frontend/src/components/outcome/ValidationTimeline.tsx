import React from 'react';
import { Card } from '../common/Card';
import { DeploymentOutcome } from '../../types';
import { CheckCircle2, ArrowRight } from 'lucide-react';

interface ValidationTimelineProps {
  outcome: DeploymentOutcome;
}

export const ValidationTimeline: React.FC<ValidationTimelineProps> = ({ outcome }) => {
  const steps = [
    { label: 'Analysis Created', time: outcome.validationTimeline.analysisCreated },
    { label: 'Forecast Generated', time: outcome.validationTimeline.forecastGenerated },
    { label: 'Controlled Deployment', time: outcome.validationTimeline.controlledDeployment },
    { label: 'Telemetry Collected', time: outcome.validationTimeline.telemetryCollected },
    { label: 'Forecast Compared', time: outcome.validationTimeline.forecastCompared },
    { label: 'Outcome Validated', time: outcome.validationTimeline.outcomeValidated },
  ];

  return (
    <Card className="flex flex-col h-full overflow-hidden">
      <h3 className="text-base font-bold text-slate-100 font-sans tracking-tight mb-6">Validation Timeline</h3>
      
      <div className="relative flex-1">
        <div className="absolute left-3.5 top-2 bottom-6 w-0.5 bg-slate-800"></div>
        <div className="space-y-6 relative z-10">
          {steps.map((step, idx) => {
            const isLast = idx === steps.length - 1;
            return (
              <div key={idx} className="flex gap-4 items-start">
                <div className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 border-2 ${isLast ? 'bg-emerald-950 border-emerald-500 text-emerald-400' : 'bg-slate-900 border-slate-700 text-slate-400'}`}>
                  {isLast ? <CheckCircle2 className="w-4 h-4" /> : <div className="w-2 h-2 rounded-full bg-slate-500"></div>}
                </div>
                <div className="pt-0.5">
                  <div className={`text-sm font-semibold ${isLast ? 'text-emerald-400' : 'text-slate-200'}`}>
                    {step.label}
                  </div>
                  <div className="text-xs font-mono text-slate-500 mt-1">
                    {new Date(step.time).toLocaleString()}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </Card>
  );
};
