import React from 'react';
import { Card } from '../common/Card';
import { HistorySummaryData } from '../../types';
import { FileText, CheckCircle2, Clock, ShieldCheck } from 'lucide-react';

interface HistorySummaryProps {
  summary: HistorySummaryData;
}

export const HistorySummary: React.FC<HistorySummaryProps> = ({ summary }) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <Card className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center shrink-0">
          <FileText className="w-6 h-6 text-slate-400" />
        </div>
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 block mb-0.5">
            Total Analyses
          </span>
          <span className="text-xl font-bold font-mono text-slate-100">{summary.totalAnalyses}</span>
        </div>
      </Card>

      <Card className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-full bg-indigo-500/10 flex items-center justify-center shrink-0">
          <CheckCircle2 className="w-6 h-6 text-indigo-400" />
        </div>
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 block mb-0.5">
            Completed
          </span>
          <span className="text-xl font-bold font-mono text-indigo-400">{summary.completed}</span>
        </div>
      </Card>

      <Card className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-full bg-amber-500/10 flex items-center justify-center shrink-0">
          <Clock className="w-6 h-6 text-amber-400" />
        </div>
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 block mb-0.5">
            Pending
          </span>
          <span className="text-xl font-bold font-mono text-amber-400">{summary.pending}</span>
        </div>
      </Card>

      <Card className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-full bg-emerald-500/10 flex items-center justify-center shrink-0">
          <ShieldCheck className="w-6 h-6 text-emerald-400" />
        </div>
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 block mb-0.5">
            Validated Outcomes
          </span>
          <span className="text-xl font-bold font-mono text-emerald-400">{summary.validatedOutcomes}</span>
        </div>
      </Card>
    </div>
  );
};
