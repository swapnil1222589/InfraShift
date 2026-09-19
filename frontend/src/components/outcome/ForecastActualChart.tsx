import React from 'react';
import { Card } from '../common/Card';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';
import { ForecastVsActualPoint } from '../../types';

interface ForecastActualChartProps {
  title: string;
  data: ForecastVsActualPoint[];
}

export const ForecastActualChart: React.FC<ForecastActualChartProps> = ({ title, data }) => {
  return (
    <Card className="flex flex-col h-full">
      <h3 className="text-base font-bold text-slate-100 font-sans tracking-tight mb-4">{title}</h3>
      <div className="flex-1 min-h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.6} />
            <XAxis dataKey="timestamp" stroke="#94a3b8" fontSize={11} fontStyle="mono" />
            <YAxis
              stroke="#94a3b8"
              fontSize={11}
              fontStyle="mono"
              tickFormatter={(val) => `+${val}%`}
              domain={[0, 'dataMax + 5']}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0f172a',
                borderColor: '#334155',
                borderRadius: '8px',
                fontSize: '11px',
                fontFamily: 'monospace',
              }}
              formatter={(value: any) => [`+${value}%`, '']}
            />
            <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
            
            {/* Forecast Band */}
            <Line
              type="monotone"
              dataKey="forecastMax"
              name="Forecast Range (Max)"
              stroke="#f59e0b"
              strokeDasharray="4 4"
              strokeWidth={1}
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="forecastMin"
              name="Forecast Range (Min)"
              stroke="#d97706"
              strokeDasharray="4 4"
              strokeWidth={1}
              dot={false}
            />
            
            {/* Actual Realized Line */}
            <Line
              type="monotone"
              dataKey="actual"
              name="Actual Realized"
              stroke="#10b981"
              strokeWidth={3}
              dot={{ r: 4, fill: '#10b981' }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
};
