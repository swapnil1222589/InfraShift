import React from 'react';
import { Card } from '../common/Card';
import { TelemetrySignal } from '../../types';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

interface TelemetryChartProps {
  signal: TelemetrySignal;
}

export const TelemetryChart: React.FC<TelemetryChartProps> = ({ signal }) => {
  return (
    <Card className="flex flex-col gap-4">
      <div>
        <h4 className="text-base font-medium text-slate-100">{signal.metricName}</h4>
        <p className="text-sm text-slate-400 mt-1">{signal.description}</p>
      </div>

      <div className="h-64 mt-4">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={signal.data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
            <XAxis dataKey="time" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
            <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '4px' }}
              itemStyle={{ fontSize: '12px' }}
              labelStyle={{ color: '#94a3b8', marginBottom: '4px', fontSize: '12px' }}
            />
            <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
            <Line 
              type="monotone" 
              name="Baseline" 
              dataKey="baseline" 
              stroke="#64748b" 
              strokeWidth={2} 
              dot={false}
              strokeDasharray="4 4"
            />
            <Line 
              type="monotone" 
              name="Observed (Similar Deploys)" 
              dataKey="observed" 
              stroke="#818cf8" 
              strokeWidth={2}
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="flex justify-between items-center text-xs text-slate-400 mt-2 bg-slate-800/50 p-2 rounded">
        <span>Time Range: <strong className="text-slate-300">{signal.timeRange}</strong></span>
        <span>Metric: <strong className="text-slate-300">{signal.metricName}</strong></span>
      </div>
    </Card>
  );
};
