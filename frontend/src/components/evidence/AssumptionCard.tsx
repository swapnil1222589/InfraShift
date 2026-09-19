import React from 'react';
import { Card } from '../common/Card';
import { Info } from 'lucide-react';
import { Assumptions } from '../../types';

interface AssumptionCardProps {
  assumptions: Assumptions;
}

export const AssumptionCard: React.FC<AssumptionCardProps> = ({ assumptions }) => {
  const assumptionItems = [
    { label: 'Baseline Window', value: assumptions.baselineWindow, tooltip: 'The period used to calculate normal operating metrics before the deployment.' },
    { label: 'Comparison Window', value: assumptions.comparisonWindow, tooltip: 'The historical deployments considered similar enough to inform this forecast.' },
    { label: 'Telemetry Availability', value: assumptions.telemetryAvailability, tooltip: 'Percentage of requested metrics available in CloudWatch/Datadog for the target resources.' },
    { label: 'Historical Samples', value: assumptions.historicalSamples.toString(), tooltip: 'Total number of past PRs matching the fingerprint of this code change.' },
    { label: 'Affected Environment', value: assumptions.affectedEnvironment, tooltip: 'The target environment assumed for the forecast (e.g., Staging vs Production).' },
  ];

  return (
    <Card className="flex flex-col gap-4">
      <h3 className="text-lg font-semibold text-slate-100 border-b border-slate-700/50 pb-3 mb-2">Assumptions</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-y-6 gap-x-8">
        {assumptionItems.map((item, index) => (
          <div key={index} className="flex flex-col gap-1">
            <div className="flex items-center gap-2 group relative">
              <span className="text-sm font-medium text-slate-400">{item.label}</span>
              <div className="relative flex items-center justify-center">
                <Info className="w-4 h-4 text-slate-500 cursor-help hover:text-slate-300 transition-colors" />
                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 p-2 bg-slate-800 text-xs text-slate-200 rounded border border-slate-700 shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10 text-center">
                  {item.tooltip}
                  <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-slate-700"></div>
                </div>
              </div>
            </div>
            <span className="text-base text-slate-100">{item.value}</span>
          </div>
        ))}
      </div>
    </Card>
  );
};
