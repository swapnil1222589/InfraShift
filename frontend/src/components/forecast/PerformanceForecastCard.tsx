import React from 'react';
import { PerformanceForecast } from '../../types/forecast';
import { Link, useParams } from 'react-router-dom';
import { Card } from '../common/Card';
import { ConfidenceMeter } from '../common/ConfidenceMeter';
import { Activity, Clock, Zap, Database, AlertCircle, HelpCircle } from 'lucide-react';

interface PerformanceForecastCardProps {
  performance: PerformanceForecast;
}

export const PerformanceForecastCard: React.FC<PerformanceForecastCardProps> = ({ performance }) => {
  const { id } = useParams<{ id: string }>();
  const { latency } = performance;

  return (
    <Card
      title="Performance Forecast Range"
      subtitle="Latency distribution & capacity pressure"
      badge={<Activity className="w-4 h-4 text-sky-400" />}
      headerAction={<ConfidenceMeter score={performance.confidence} />}
    >
      <div className="space-y-4">
        {/* P99 Latency Shift */}
        <div className="p-4 rounded-lg bg-slate-950/80 border border-slate-800">
          <div className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-2">
            <div>
              <span className="text-[10px] font-mono uppercase text-slate-500 block">
                P99 TAIL LATENCY IMPACT (RANGE)
              </span>
              <div className="text-2xl sm:text-3xl font-bold font-mono text-amber-400 mt-1">
                {latency.p99CurrentMs}ms → {latency.p99ProjectedMs}ms
                <span className="text-xs sm:text-sm text-amber-300 font-mono ml-2">(+14.2%)</span>
              </div>
            </div>

            <div className="text-right font-mono">
              <span className="text-xs px-2 py-0.5 rounded bg-amber-950/80 text-amber-300 border border-amber-800 font-semibold">
                +5% to +12%
              </span>
              <span className="text-[10px] text-slate-500 block mt-1">Expected delta band</span>
            </div>
          </div>

          {/* Percentile Breakdown */}
          <div className="mt-4 pt-3 border-t border-slate-800/80 grid grid-cols-3 gap-2 text-xs font-mono text-center">
            <div className="p-2 rounded bg-slate-900/60 border border-slate-800/80">
              <span className="text-slate-500 text-[10px] block">P50 (Median)</span>
              <span className="text-slate-200 font-medium">{latency.p50CurrentMs}ms → {latency.p50ProjectedMs}ms</span>
            </div>
            <div className="p-2 rounded bg-slate-900/60 border border-slate-800/80">
              <span className="text-slate-500 text-[10px] block">P90</span>
              <span className="text-slate-200 font-medium">{latency.p90CurrentMs}ms → {latency.p90ProjectedMs}ms</span>
            </div>
            <div className="p-2 rounded bg-slate-900/60 border border-slate-800/80">
              <span className="text-slate-500 text-[10px] block">P99</span>
              <span className="text-amber-400 font-medium">{latency.p99CurrentMs}ms → {latency.p99ProjectedMs}ms</span>
            </div>
          </div>
        </div>

        {/* Telemetry Metrics Grid */}
        <div className="grid grid-cols-2 gap-3">
          <div className="p-3.5 rounded-lg bg-slate-950/60 border border-slate-800">
            <div className="flex items-center gap-1.5 text-slate-400 text-xs">
              <Database className="w-3.5 h-3.5 text-orange-400" />
              <span className="font-mono text-[10px] uppercase">DynamoDB RCU Spike</span>
            </div>
            <div className="mt-2 text-xl font-bold font-mono text-orange-400">
              +{performance.resourceUtilizationDeltaPct}%
            </div>
            <p className="text-[10px] text-slate-500 mt-1">
              Read capacity consumption jump during composite key scan
            </p>
          </div>

          <div className="p-3.5 rounded-lg bg-slate-950/60 border border-slate-800">
            <div className="flex items-center gap-1.5 text-slate-400 text-xs">
              <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
              <span className="font-mono text-[10px] uppercase">Throttling Probability</span>
            </div>
            <div className="mt-2 text-xl font-bold font-mono text-amber-400">
              {performance.throttlingRiskPct}%
            </div>
            <p className="text-[10px] text-slate-500 mt-1">
              Estimated risk during unannounced traffic surges
            </p>
          </div>
        </div>

        <div className="pt-2">
          <Link
            to={`/analyses/${id}/evidence`}
            className="w-full inline-flex justify-center items-center gap-2 px-4 py-2 text-xs font-medium text-slate-300 bg-slate-800 hover:bg-slate-700 hover:text-white border border-slate-700 rounded-md transition"
          >
            <HelpCircle className="w-3.5 h-3.5" />
            Why This Forecast?
          </Link>
        </div>
      </div>
    </Card>
  );
};
