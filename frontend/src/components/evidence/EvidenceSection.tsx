import React from 'react';
import { EvidenceReport } from '../../types';
import { EvidenceSummary } from './EvidenceSummary';
import { HistoricalComparisonCard } from './HistoricalComparisonCard';
import { TelemetryChart } from './TelemetryChart';
import { AssumptionCard } from './AssumptionCard';
import { EvidenceTypeBadge } from './EvidenceTypeBadge';
import { ConfidencePanel } from './ConfidencePanel';
import { InsufficientEvidence } from './InsufficientEvidence';

interface EvidenceSectionProps {
  evidence: EvidenceReport;
}

export const EvidenceSection: React.FC<EvidenceSectionProps> = ({ evidence }) => {
  if (evidence.status === 'Insufficient') {
    return <InsufficientEvidence assumptions={evidence.assumptions} />;
  }

  // Separate evidence items by category for the three clearly separated sections
  const historicalItems = evidence.items.filter(i => i.category === 'historical_observation');
  const predictionItems = evidence.items.filter(i => i.category === 'prediction');
  const inferenceItems = evidence.items.filter(i => i.category === 'inference');

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      
      {/* Evidence Summary Cards */}
      <EvidenceSummary report={evidence} />

      {/* Historical Comparisons */}
      <div className="space-y-4">
        <h3 className="text-xl font-bold text-slate-100">Historical Comparisons</h3>
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
          {evidence.historicalComparisons.map((comparison) => (
            <HistoricalComparisonCard key={comparison.id} comparison={comparison} />
          ))}
        </div>
      </div>

      {/* Telemetry Evidence */}
      <div className="space-y-4">
        <h3 className="text-xl font-bold text-slate-100">Telemetry Signals</h3>
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          {evidence.telemetrySignals.map((signal) => (
            <TelemetryChart key={signal.id} signal={signal} />
          ))}
        </div>
      </div>

      {/* Assumptions */}
      <div className="space-y-4">
        <AssumptionCard assumptions={evidence.assumptions} />
      </div>

      {/* Prediction / Observation / Inference Separated Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="flex flex-col gap-3 p-4 bg-slate-800/30 rounded-lg border border-slate-700/50">
          <EvidenceTypeBadge category="historical_observation" />
          <div className="space-y-2 mt-2">
            {historicalItems.map(item => (
              <p key={item.id} className="text-sm text-slate-300 leading-relaxed">
                "{item.text}"
              </p>
            ))}
          </div>
        </div>

        <div className="flex flex-col gap-3 p-4 bg-slate-800/30 rounded-lg border border-slate-700/50">
          <EvidenceTypeBadge category="prediction" />
          <div className="space-y-2 mt-2">
            {predictionItems.map(item => (
              <p key={item.id} className="text-sm text-slate-300 leading-relaxed">
                "{item.text}"
              </p>
            ))}
          </div>
        </div>

        <div className="flex flex-col gap-3 p-4 bg-slate-800/30 rounded-lg border border-slate-700/50">
          <EvidenceTypeBadge category="inference" />
          <div className="space-y-2 mt-2">
            {inferenceItems.map(item => (
              <p key={item.id} className="text-sm text-slate-300 leading-relaxed">
                "{item.text}"
              </p>
            ))}
          </div>
        </div>
      </div>

      {/* Confidence Panel */}
      <div className="space-y-4 max-w-3xl">
        <ConfidencePanel confidence={evidence.confidence} />
      </div>

    </div>
  );
};
