import React from 'react';
import { TimelineStep } from '../../types/analysis';
import { CheckCircle2, Clock, ArrowRight, AlertTriangle } from 'lucide-react';

interface TimelineProps {
  steps: TimelineStep[];
}

export const Timeline: React.FC<TimelineProps> = ({ steps }) => {
  return (
    <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 font-semibold">
            AUTOMATED ANALYSIS PIPELINE
          </span>
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
        </div>
        <span className="text-[10px] font-mono text-slate-500">Total duration: 6,722ms</span>
      </div>

      <div className="flex overflow-x-auto pb-2 -mb-2 gap-3 snap-x scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-transparent">
        {steps.map((step, idx) => (
          <div
            key={step.id}
            className="w-[200px] lg:flex-1 shrink-0 snap-start p-3.5 rounded-lg bg-slate-950/80 border border-slate-800 hover:border-slate-700 hover:bg-slate-900/50 transition-all flex flex-col justify-between group relative min-h-[140px]"
          >
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-mono text-amber-500/80 font-bold">
                  0{idx + 1}
                </span>
                {step.status === 'completed' ? (
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                ) : step.status === 'warning' ? (
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                ) : (
                  <Clock className="w-3.5 h-3.5 text-slate-500 animate-pulse" />
                )}
              </div>

              <h4 className="text-xs font-semibold text-slate-200 group-hover:text-amber-300 transition-colors">
                {step.name}
              </h4>
              <p className="text-[10px] text-slate-400 mt-1 leading-snug line-clamp-2">
                {step.description}
              </p>
            </div>

            <div className="mt-3 pt-2 border-t border-slate-800/60 flex items-center justify-between text-[10px] font-mono text-slate-500">
              <span>{step.durationMs ? `${step.durationMs}ms` : '—'}</span>
              <span className="text-emerald-400 font-medium">Passed</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
