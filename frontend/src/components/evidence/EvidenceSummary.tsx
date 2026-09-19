import React from 'react';
import { Card } from '../common/Card';
import { History, Activity, ShieldCheck, HelpCircle } from 'lucide-react';
import { EvidenceReport } from '../../types';

interface EvidenceSummaryProps {
  report: EvidenceReport;
}

export const EvidenceSummary: React.FC<EvidenceSummaryProps> = ({ report }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <Card className="flex flex-col gap-2">
        <div className="flex items-center gap-2 text-indigo-400 mb-2">
          <History className="w-5 h-5" />
          <h3 className="font-semibold text-sm uppercase tracking-wider text-slate-400">Historical Comparisons</h3>
        </div>
        <div className="text-3xl font-bold text-slate-100">{report.historicalComparisons.length}</div>
        <p className="text-xs text-slate-400">Comparable deployments found and analyzed</p>
      </Card>
      
      <Card className="flex flex-col gap-2">
        <div className="flex items-center gap-2 text-teal-400 mb-2">
          <Activity className="w-5 h-5" />
          <h3 className="font-semibold text-sm uppercase tracking-wider text-slate-400">Telemetry Signals</h3>
        </div>
        <div className="text-3xl font-bold text-slate-100">{report.telemetrySignals.length}</div>
        <p className="text-xs text-slate-400">Relevant metrics informing the forecast</p>
      </Card>
      
      <Card className="flex flex-col gap-2">
        <div className="flex items-center gap-2 text-blue-400 mb-2">
          <ShieldCheck className="w-5 h-5" />
          <h3 className="font-semibold text-sm uppercase tracking-wider text-slate-400">Evidence Coverage</h3>
        </div>
        <div className="text-3xl font-bold text-slate-100">{report.confidence.evidenceCoverage}%</div>
        <p className="text-xs text-slate-400">Percentage of forecast backed by data</p>
      </Card>
      
      <Card className="flex flex-col gap-2">
        <div className="flex items-center gap-2 text-amber-400 mb-2">
          <HelpCircle className="w-5 h-5" />
          <h3 className="font-semibold text-sm uppercase tracking-wider text-slate-400">Forecast Confidence</h3>
        </div>
        <div className="text-3xl font-bold text-slate-100">{report.confidence.overall}%</div>
        <p className="text-xs text-slate-400">Overall reliability based on available evidence</p>
      </Card>
    </div>
  );
};
