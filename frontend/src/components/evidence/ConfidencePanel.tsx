import React from 'react';
import { Card } from '../common/Card';
import { ConfidenceScore } from '../../types';
import { HelpCircle } from 'lucide-react';

interface ConfidencePanelProps {
  confidence: ConfidenceScore;
}

export const ConfidencePanel: React.FC<ConfidencePanelProps> = ({ confidence }) => {
  const getBarColor = (val: number) => {
    if (val >= 80) return 'bg-teal-500';
    if (val >= 60) return 'bg-indigo-500';
    if (val >= 40) return 'bg-amber-500';
    return 'bg-rose-500';
  };

  const MetricBar = ({ label, value }: { label: string; value: number }) => (
    <div className="flex flex-col gap-1.5 mb-4">
      <div className="flex justify-between items-center text-sm">
        <span className="text-slate-300">{label}</span>
        <span className="font-semibold text-slate-100">{value}%</span>
      </div>
      <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
        <div 
          className={`h-full rounded-full ${getBarColor(value)} transition-all duration-1000`} 
          style={{ width: `${value}%` }} 
        />
      </div>
    </div>
  );

  return (
    <Card className="flex flex-col gap-6">
      <div className="flex justify-between items-start border-b border-slate-700/50 pb-4">
        <div>
          <h3 className="text-lg font-semibold text-slate-100 mb-1">Forecast Confidence</h3>
          <p className="text-sm text-slate-400 max-w-sm">
            Confidence reflects the availability and consistency of supporting evidence. It does not represent certainty.
          </p>
        </div>
        <div className="flex items-center justify-center w-20 h-20 rounded-full border-4 border-slate-700 relative">
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-2xl font-bold text-slate-100">{confidence.overall}%</span>
          </div>
          {/* Note: SVG circle could be used for actual progress ring, keeping simple for now */}
        </div>
      </div>

      <div className="pt-2">
        <MetricBar label="Evidence Coverage" value={confidence.evidenceCoverage} />
        <MetricBar label="Historical Similarity" value={confidence.historicalSimilarity} />
        <MetricBar label="Telemetry Availability" value={confidence.telemetryAvailability} />
        <MetricBar label="Model/Forecast Support" value={confidence.modelSupport} />
      </div>
      
      <div className="flex items-start gap-2 bg-slate-800/50 p-3 rounded text-sm text-slate-400">
        <HelpCircle className="w-5 h-5 text-slate-500 shrink-0 mt-0.5" />
        <p>
          Forecasts with confidence below 60% should be heavily supplemented with manual review or controlled load testing prior to full deployment.
        </p>
      </div>
    </Card>
  );
};
