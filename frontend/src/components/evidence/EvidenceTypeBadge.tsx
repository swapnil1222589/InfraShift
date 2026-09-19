import React from 'react';
import { EvidenceCategory } from '../../types';
import { Database, Lightbulb, TrendingUp } from 'lucide-react';

interface EvidenceTypeBadgeProps {
  category: EvidenceCategory;
}

export const EvidenceTypeBadge: React.FC<EvidenceTypeBadgeProps> = ({ category }) => {
  const getBadgeStyle = () => {
    switch (category) {
      case 'historical_observation':
        return {
          bg: 'bg-indigo-500/10',
          text: 'text-indigo-400',
          border: 'border-indigo-500/20',
          icon: <Database className="w-3.5 h-3.5" />,
          label: 'HISTORICAL OBSERVATION',
        };
      case 'prediction':
        return {
          bg: 'bg-teal-500/10',
          text: 'text-teal-400',
          border: 'border-teal-500/20',
          icon: <TrendingUp className="w-3.5 h-3.5" />,
          label: 'PREDICTION',
        };
      case 'inference':
        return {
          bg: 'bg-amber-500/10',
          text: 'text-amber-400',
          border: 'border-amber-500/20',
          icon: <Lightbulb className="w-3.5 h-3.5" />,
          label: 'INFERENCE',
        };
    }
  };

  const style = getBadgeStyle();

  return (
    <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-semibold uppercase tracking-wide border ${style.bg} ${style.text} ${style.border}`}>
      {style.icon}
      {style.label}
    </div>
  );
};
