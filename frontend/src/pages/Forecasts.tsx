import React from 'react';
import { mockForecastPR248 } from '../mock/forecasts';
import { Card } from '../components/common/Card';
import { ConfidenceMeter } from '../components/common/ConfidenceMeter';
import { DollarSign, Activity, TrendingUp, Cpu, Database, AlertTriangle } from 'lucide-react';

export const Forecasts: React.FC = () => {
  const f = mockForecastPR248;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 font-sans tracking-tight">
            Cost & Performance Forecasts
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Predictive modeling calibrated against historical CloudWatch telemetry and PR AST mutations.
          </p>
        </div>
        <ConfidenceMeter score={f.cost.confidence} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Cost Forecast Card */}
        <Card
          title="AWS Cost Forecast"
          subtitle="Non-parametric range modeling for PR #248"
          badge={<DollarSign className="w-4 h-4 text-emerald-400" />}
          headerAction={<span className="text-xs font-mono text-slate-400">Baseline: ${f.cost.currentMonthlyBaselineUsd}/mo</span>}
        >
          <div className="space-y-4">
            <div className="p-4 rounded-lg bg-slate-950/80 border border-slate-800">
              <span className="text-[10px] font-mono text-slate-500 uppercase">Projected Monthly Delta</span>
              <div className="text-3xl font-bold font-mono text-orange-400 mt-1">
                ${f.cost.projectedMonthlyMinUsd - f.cost.currentMonthlyBaselineUsd} – ${f.cost.projectedMonthlyMaxUsd - f.cost.currentMonthlyBaselineUsd}
                <span className="text-sm text-slate-400 font-sans ml-2">/ month</span>
              </div>
              <div className="text-xs font-mono text-slate-400 mt-1">
                Percent change: <span className="text-orange-400 font-semibold">+{f.cost.percentageChangeMin}% to +{f.cost.percentageChangeMax}%</span>
              </div>
            </div>

            <div>
              <span className="text-[11px] font-mono uppercase text-slate-400 block mb-2">
                COST DRIVER BREAKDOWN:
              </span>
              <div className="space-y-2">
                {f.cost.driverBreakdown.map((item, idx) => (
                  <div key={idx} className="p-3 rounded-lg bg-slate-950/50 border border-slate-800/80 text-xs">
                    <div className="flex justify-between items-center">
                      <span className="font-semibold text-slate-200">{item.awsService}</span>
                      <span className="font-mono text-orange-400 font-medium">
                        +${item.estimatedDeltaUsd.toFixed(2)}/mo
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400 mt-1">{item.description}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </Card>

        {/* Performance Forecast Card */}
        <Card
          title="Performance & Latency Forecast"
          subtitle="Distribution percentiles and resource concurrency"
          badge={<Activity className="w-4 h-4 text-sky-400" />}
          headerAction={<span className="text-xs font-mono text-slate-400">Confidence: {f.performance.latency.confidence}%</span>}
        >
          <div className="space-y-4">
            <div className="p-4 rounded-lg bg-slate-950/80 border border-slate-800">
              <span className="text-[10px] font-mono text-slate-500 uppercase">P99 Latency Shift</span>
              <div className="text-3xl font-bold font-mono text-amber-400 mt-1">
                {f.performance.latency.p99CurrentMs}ms → {f.performance.latency.p99ProjectedMs}ms
                <span className="text-sm text-amber-300 font-mono ml-2">(+14.2%)</span>
              </div>
              <div className="text-xs font-mono text-slate-400 mt-1">
                P50: {f.performance.latency.p50CurrentMs}ms → {f.performance.latency.p50ProjectedMs}ms · P90: {f.performance.latency.p90CurrentMs}ms → {f.performance.latency.p90ProjectedMs}ms
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 rounded-lg bg-slate-950/50 border border-slate-800/80">
                <span className="text-[10px] font-mono text-slate-500 uppercase block">DynamoDB RCU Spike</span>
                <span className="text-lg font-bold font-mono text-orange-400 mt-1 block">
                  +{f.performance.resourceUtilizationDeltaPct}%
                </span>
                <span className="text-[10px] text-slate-400">Read capacity jump</span>
              </div>

              <div className="p-3 rounded-lg bg-slate-950/50 border border-slate-800/80">
                <span className="text-[10px] font-mono text-slate-500 uppercase block">Throttling Risk</span>
                <span className="text-lg font-bold font-mono text-amber-400 mt-1 block">
                  {f.performance.throttlingRiskPct}%
                </span>
                <span className="text-[10px] text-slate-400">During flash events</span>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};
