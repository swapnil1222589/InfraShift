import React from 'react';
import { Card } from '../common/Card';
import { DeploymentOutcome } from '../../types';
import {
  ResponsiveContainer,
  ComposedChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  Scatter,
  ErrorBar,
} from 'recharts';

interface PerformanceImpactChartProps {
  outcome: DeploymentOutcome;
}

export const PerformanceImpactChart: React.FC<PerformanceImpactChartProps> = ({ outcome }) => {
  const data = [
    {
      name: 'Latency',
      forecastMin: outcome.forecastLatencyRange.minPct,
      forecastMax: outcome.forecastLatencyRange.maxPct,
      actual: outcome.actualLatency.deltaPct,
      // For ErrorBar to work with Scatter/Bar:
      avg: (outcome.forecastLatencyRange.maxPct + outcome.forecastLatencyRange.minPct) / 2,
      error: [
        ((outcome.forecastLatencyRange.maxPct + outcome.forecastLatencyRange.minPct) / 2) - outcome.forecastLatencyRange.minPct,
        outcome.forecastLatencyRange.maxPct - ((outcome.forecastLatencyRange.maxPct + outcome.forecastLatencyRange.minPct) / 2)
      ]
    },
    {
      name: 'Lambda Duration',
      forecastMin: outcome.forecastLambdaDurationRange.minPct,
      forecastMax: outcome.forecastLambdaDurationRange.maxPct,
      actual: outcome.actualLambdaDurationPct,
      avg: (outcome.forecastLambdaDurationRange.maxPct + outcome.forecastLambdaDurationRange.minPct) / 2,
      error: [
        ((outcome.forecastLambdaDurationRange.maxPct + outcome.forecastLambdaDurationRange.minPct) / 2) - outcome.forecastLambdaDurationRange.minPct,
        outcome.forecastLambdaDurationRange.maxPct - ((outcome.forecastLambdaDurationRange.maxPct + outcome.forecastLambdaDurationRange.minPct) / 2)
      ]
    },
    {
      name: 'DynamoDB Reads',
      forecastMin: outcome.forecastDynamoDbRange.minPct,
      forecastMax: outcome.forecastDynamoDbRange.maxPct,
      actual: outcome.actualDynamoDbPct,
      avg: (outcome.forecastDynamoDbRange.maxPct + outcome.forecastDynamoDbRange.minPct) / 2,
      error: [
        ((outcome.forecastDynamoDbRange.maxPct + outcome.forecastDynamoDbRange.minPct) / 2) - outcome.forecastDynamoDbRange.minPct,
        outcome.forecastDynamoDbRange.maxPct - ((outcome.forecastDynamoDbRange.maxPct + outcome.forecastDynamoDbRange.minPct) / 2)
      ]
    },
  ];

  return (
    <Card className="flex flex-col h-full">
      <h3 className="text-base font-bold text-slate-100 font-sans tracking-tight mb-4">Performance Impact</h3>
      <div className="flex-1 min-h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} layout="vertical" margin={{ top: 10, right: 30, left: 20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.6} horizontal={false} />
            <XAxis type="number" stroke="#94a3b8" fontSize={11} fontStyle="mono" tickFormatter={(val) => `+${val}%`} />
            <YAxis dataKey="name" type="category" stroke="#94a3b8" fontSize={11} fontStyle="sans" width={100} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0f172a',
                borderColor: '#334155',
                borderRadius: '8px',
                fontSize: '11px',
                fontFamily: 'monospace',
              }}
              cursor={{ fill: '#1e293b' }}
              formatter={(value: any, name: any) => {
                if (name === 'Actual Realized') return [`+${value}%`, name];
                if (name === 'Forecast Range') return [`±${value[0]}%`, name];
                return null;
              }}
            />
            <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
            
            <Bar dataKey="avg" fill="transparent" name="Forecast Range">
              <ErrorBar dataKey="error" width={8} strokeWidth={2} stroke="#f59e0b" direction="x" />
            </Bar>
            
            <Scatter dataKey="actual" name="Actual Realized" fill="#10b981" line={false} />
            
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
};
