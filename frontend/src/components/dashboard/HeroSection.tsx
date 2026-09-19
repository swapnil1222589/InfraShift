import React from 'react';
import { Sparkles, Terminal, Activity, ArrowRight, ShieldAlert } from 'lucide-react';
import { Button } from '../common/Button';

interface HeroSectionProps {
  onAnalyzeClick: () => void;
}

export const HeroSection: React.FC<HeroSectionProps> = ({ onAnalyzeClick }) => {
  return (
    <div className="relative overflow-hidden rounded-xl border border-slate-800 bg-gradient-to-b from-slate-900 via-slate-900/90 to-slate-950 p-6 md:p-8 shadow-md">
      {/* Background architectural grid highlight */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-amber-500/5 rounded-full blur-3xl -z-10 pointer-events-none" />

      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
        <div className="max-w-2xl">
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-slate-800/80 border border-slate-700/80 text-[11px] font-mono text-amber-400 mb-4">
            <Activity className="w-3.5 h-3.5 text-amber-400 animate-pulse" />
            <span>AWS Telemetry Correlator Active</span>
          </div>

          <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-slate-100 font-sans">
            Know your infrastructure impact before you deploy.
          </h1>

          <p className="mt-2.5 text-sm md:text-base text-slate-400 leading-relaxed max-w-xl">
            Analyze code changes against AWS infrastructure, telemetry and historical deployments.
            Prevent downstream latency degradation and unexpected cloud billing surges.
          </p>

          <div className="mt-6 flex flex-wrap items-center gap-3">
            <Button
              variant="aws"
              size="md"
              icon={<Sparkles className="w-4 h-4" />}
              onClick={onAnalyzeClick}
              className="font-semibold shadow-lg shadow-orange-950/40"
            >
              Analyze Pull Request
            </Button>

            <a
              href="#analyses-table"
              className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-medium text-slate-300 hover:text-white bg-slate-800/60 hover:bg-slate-800 border border-slate-700/70 rounded-md transition"
            >
              <span>View Recent PR Analyses</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </a>
          </div>
        </div>

        {/* Real-time telemetry snapshot badge card */}
        <div className="bg-slate-950/90 border border-slate-800 rounded-lg p-4 font-mono text-xs max-w-sm shrink-0">
          <div className="flex items-center justify-between text-slate-400 pb-2 border-b border-slate-800/80 mb-2.5">
            <span className="flex items-center gap-1.5 text-slate-300 text-[11px]">
              <Terminal className="w-3.5 h-3.5 text-amber-400" />
              <span>infrashift-daemon</span>
            </span>
            <span className="text-[10px] text-emerald-400">AWS SDK v3 · Connected</span>
          </div>

          <div className="space-y-1.5 text-[11px] text-slate-300">
            <div className="flex justify-between">
              <span className="text-slate-500">Repository AST:</span>
              <span className="text-slate-300">Synchronized</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">CloudWatch Baseline:</span>
              <span className="text-slate-300">14-day P95 window</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Predicted Blast Radius:</span>
              <span className="text-amber-400 font-semibold">Service-level</span>
            </div>
            <div className="flex justify-between pt-1 border-t border-slate-800/60 text-slate-400">
              <span className="text-slate-500">Top Monitored Service:</span>
              <span className="text-sky-400">Amazon DynamoDB</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
