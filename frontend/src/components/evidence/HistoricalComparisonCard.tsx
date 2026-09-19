import React from 'react';
import { Card } from '../common/Card';
import { GitPullRequest, ArrowRight, Calendar, Box } from 'lucide-react';
import { HistoricalComparison } from '../../types';

interface HistoricalComparisonCardProps {
  comparison: HistoricalComparison;
}

export const HistoricalComparisonCard: React.FC<HistoricalComparisonCardProps> = ({ comparison }) => {
  return (
    <Card className="flex flex-col gap-4 border-l-4 border-l-indigo-500">
      <div className="flex justify-between items-start">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <GitPullRequest className="w-4 h-4 text-indigo-400" />
            <span className="font-mono text-sm text-indigo-400">PR #{comparison.prNumber}</span>
          </div>
          <h4 className="text-base font-medium text-slate-100">{comparison.title}</h4>
        </div>
        <div className="flex flex-col items-end">
          <span className="text-2xl font-bold text-slate-100">{comparison.similarity}%</span>
          <span className="text-xs text-slate-400">Similarity</span>
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4 bg-slate-800/50 p-3 rounded border border-slate-700/50">
        <div>
          <span className="block text-xs text-slate-400 mb-1">Cost Change</span>
          <span className="text-sm font-medium text-rose-400">{comparison.costChange}</span>
        </div>
        <div>
          <span className="block text-xs text-slate-400 mb-1">Latency Change</span>
          <span className="text-sm font-medium text-rose-400">{comparison.latencyChange}</span>
        </div>
      </div>

      <div className="flex items-center justify-between text-sm mt-2">
        <div className="flex items-center gap-4 text-slate-400">
          <div className="flex items-center gap-1">
            <Calendar className="w-4 h-4" />
            {comparison.date}
          </div>
          <div className="flex items-center gap-1">
            <Box className="w-4 h-4" />
            {comparison.affectedResource}
          </div>
        </div>
        <button className="flex items-center gap-1 text-indigo-400 hover:text-indigo-300 text-sm font-medium transition-colors">
          View Details
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </Card>
  );
};
