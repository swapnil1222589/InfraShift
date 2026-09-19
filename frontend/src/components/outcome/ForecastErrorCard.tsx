import React from 'react';
import { Card } from '../common/Card';
import { DeploymentOutcome } from '../../types';
import { HelpCircle, AlertTriangle } from 'lucide-react';

interface ForecastErrorCardProps {
  outcome: DeploymentOutcome;
}

export const ForecastErrorCard: React.FC<ForecastErrorCardProps> = ({ outcome }) => {
  const errors = [
    { label: 'Cost Error', value: outcome.costForecastErrorPct },
    { label: 'Latency Error', value: outcome.latencyForecastErrorPct },
    { label: 'Lambda Duration Error', value: outcome.lambdaDurationErrorPct },
    { label: 'DynamoDB Read Error', value: outcome.dynamoDbReadErrorPct },
  ];

  return (
    <Card className="flex flex-col h-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-base font-bold text-slate-100 font-sans tracking-tight">Forecast Error</h3>
        <div className="group relative">
          <HelpCircle className="w-4 h-4 text-slate-500 cursor-help hover:text-slate-300 transition-colors" />
          <div className="absolute right-0 top-6 w-64 p-2 bg-slate-800 border border-slate-700 text-xs text-slate-300 rounded shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10 pointer-events-none">
            Forecast error compares the observed post-deployment value with the forecasted range/value.
          </div>
        </div>
      </div>
      
      <div className="space-y-4 flex-1">
        {errors.map((err, idx) => (
          <div key={idx}>
            <div className="flex justify-between items-center text-sm mb-1 font-mono">
              <span className="text-slate-400">{err.label}:</span>
              <span className="font-bold text-amber-400">{err.value}%</span>
            </div>
            <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
              <div 
                className="h-full bg-amber-500/80 rounded-full" 
                style={{ width: `${Math.min(100, err.value * 10)}%` }} 
              />
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 pt-4 border-t border-slate-800/80 flex items-start gap-2">
        <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
        <p className="text-xs text-slate-500 font-mono">
          Errors &lt; 5% indicate a highly calibrated model. Errors &gt; 15% automatically trigger a model retraining pipeline.
        </p>
      </div>
    </Card>
  );
};
