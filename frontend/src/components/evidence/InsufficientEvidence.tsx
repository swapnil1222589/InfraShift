import React from 'react';
import { AlertTriangle } from 'lucide-react';
import { Card } from '../common/Card';
import { Assumptions } from '../../types';

interface InsufficientEvidenceProps {
  assumptions: Assumptions;
}

export const InsufficientEvidence: React.FC<InsufficientEvidenceProps> = ({ assumptions }) => {
  return (
    <Card className="flex flex-col items-center justify-center py-16 px-6 text-center border-dashed border-2 border-slate-700 bg-slate-900/50">
      <div className="w-16 h-16 bg-amber-500/10 rounded-full flex items-center justify-center mb-6">
        <AlertTriangle className="w-8 h-8 text-amber-500" />
      </div>
      
      <h2 className="text-2xl font-bold text-slate-100 mb-2">Insufficient evidence</h2>
      <p className="text-slate-400 max-w-lg mx-auto mb-8">
        There is not enough verified evidence to generate a reliable forecast. InfraShift will not fabricate a forecast without sufficient historical data or telemetry signals.
      </p>

      <div className="w-full max-w-2xl bg-slate-800/80 rounded-lg p-6 border border-slate-700">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-4 border-b border-slate-700 pb-2 text-left">
          Available Information Snapshot
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
          <div>
            <span className="block text-xs text-slate-500 mb-1">Historical Data</span>
            <span className="text-sm font-medium text-amber-400">Limited</span>
          </div>
          <div>
            <span className="block text-xs text-slate-500 mb-1">Telemetry</span>
            <span className="text-sm font-medium text-rose-400">{assumptions.telemetryAvailability}</span>
          </div>
          <div>
            <span className="block text-xs text-slate-500 mb-1">Comparable Deployments</span>
            <span className="text-sm font-medium text-amber-400">{assumptions.historicalSamples}</span>
          </div>
        </div>
      </div>
      
      <div className="mt-8 text-sm text-slate-500">
        Recommendation: Deploy to a staging environment and run simulated load tests to gather preliminary telemetry.
      </div>
    </Card>
  );
};
