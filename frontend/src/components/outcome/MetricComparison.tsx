import React from 'react';
import { Card } from '../common/Card';
import { DeploymentOutcome } from '../../types';
import { CheckCircle2, AlertTriangle } from 'lucide-react';

interface MetricComparisonProps {
  outcome: DeploymentOutcome;
}

export const MetricComparison: React.FC<MetricComparisonProps> = ({ outcome }) => {
  const metrics = [
    {
      label: 'Cost',
      forecast: `+${outcome.forecastCostRange.minPct}% to +${outcome.forecastCostRange.maxPct}%`,
      actual: `+${outcome.actualCost.deltaPct}%`,
      status: 'Within Range',
      isValidated: true,
    },
    {
      label: 'Latency',
      forecast: `+${outcome.forecastLatencyRange.minPct}% to +${outcome.forecastLatencyRange.maxPct}%`,
      actual: `+${outcome.actualLatency.deltaPct}%`,
      status: 'Within Range',
      isValidated: true,
    },
    {
      label: 'Lambda Duration',
      forecast: `+${outcome.forecastLambdaDurationRange.minPct}% to +${outcome.forecastLambdaDurationRange.maxPct}%`,
      actual: `+${outcome.actualLambdaDurationPct}%`,
      status: 'Within Range',
      isValidated: true,
    },
    {
      label: 'DynamoDB Reads',
      forecast: `+${outcome.forecastDynamoDbRange.minPct}% to +${outcome.forecastDynamoDbRange.maxPct}%`,
      actual: `+${outcome.actualDynamoDbPct}%`,
      status: 'Within Range',
      isValidated: true,
    },
  ];

  return (
    <Card noPadding>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-900/80 text-[10px] font-mono uppercase text-slate-500 border-b border-slate-800">
            <tr>
              <th className="py-3 px-4">Metric</th>
              <th className="py-3 px-4">Forecast</th>
              <th className="py-3 px-4">Actual</th>
              <th className="py-3 px-4">Difference</th>
              <th className="py-3 px-4">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono">
            {metrics.map((m, idx) => (
              <tr key={idx} className="hover:bg-slate-800/40 transition">
                <td className="py-3 px-4 font-bold text-slate-200">{m.label}</td>
                <td className="py-3 px-4 text-slate-400">{m.forecast}</td>
                <td className="py-3 px-4 font-bold text-emerald-400">{m.actual}</td>
                <td className="py-3 px-4 text-emerald-400">{m.status}</td>
                <td className="py-3 px-4">
                  <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full border bg-emerald-500/10 text-emerald-400 border-emerald-500/20 w-fit">
                    {m.isValidated ? <CheckCircle2 className="w-3 h-3" /> : <AlertTriangle className="w-3 h-3" />}
                    <span className="text-[10px] font-bold uppercase tracking-wider">
                      {m.isValidated ? 'Validated' : 'Flagged'}
                    </span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
};
