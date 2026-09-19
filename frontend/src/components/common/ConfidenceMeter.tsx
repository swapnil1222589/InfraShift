import React from 'react';
import { HelpCircle } from 'lucide-react';

interface ConfidenceMeterProps {
  score: number; // 0 to 100
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
  tooltipText?: string;
}

export const ConfidenceMeter: React.FC<ConfidenceMeterProps> = ({
  score,
  showLabel = true,
  size = 'md',
  tooltipText = 'Calculated from historical PR similarity, CloudWatch metric granularity, and AST diff stability.',
}) => {
  const getColor = (val: number) => {
    if (val >= 85) return 'text-emerald-400 bg-emerald-500';
    if (val >= 70) return 'text-amber-400 bg-amber-500';
    return 'text-rose-400 bg-rose-500';
  };

  const getBorder = (val: number) => {
    if (val >= 85) return 'border-emerald-800/60 bg-emerald-950/40';
    if (val >= 70) return 'border-amber-800/60 bg-amber-950/40';
    return 'border-rose-800/60 bg-rose-950/40';
  };

  const barColor = getColor(score);
  const badgeBorder = getBorder(score);

  return (
    <div className="inline-flex items-center gap-2 group relative">
      <div className={`px-2 py-0.5 rounded border text-xs font-mono font-medium flex items-center gap-1.5 ${badgeBorder}`}>
        <span className={barColor.split(' ')[0]}>{score}%</span>
        {showLabel && <span className="text-slate-400 font-sans">Confidence</span>}
        <HelpCircle className="w-3 h-3 text-slate-500 hover:text-slate-300 cursor-help" />
      </div>

      {/* Mini Progress Bar */}
      <div className="w-12 h-1.5 bg-slate-800 rounded-full overflow-hidden hidden sm:block">
        <div
          className={`h-full rounded-full ${barColor.split(' ')[1]}`}
          style={{ width: `${Math.min(100, Math.max(0, score))}%` }}
        />
      </div>

      {/* Tooltip */}
      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block z-50 w-56 p-2 text-xs bg-slate-900 border border-slate-700 text-slate-300 rounded shadow-xl pointer-events-none">
        {tooltipText}
        <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-slate-700" />
      </div>
    </div>
  );
};
