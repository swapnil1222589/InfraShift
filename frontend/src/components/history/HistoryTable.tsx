import React from 'react';
import { Card } from '../common/Card';
import { AnalysisHistoryItem } from '../../types';
import { ConfidenceMeter } from '../common/ConfidenceMeter';

interface HistoryTableProps {
  items: AnalysisHistoryItem[];
  onRowClick: (item: AnalysisHistoryItem) => void;
  selectedItemId: string | null;
}

export const HistoryTable: React.FC<HistoryTableProps> = ({ items, onRowClick, selectedItemId }) => {
  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'CRITICAL': return 'text-rose-400 bg-rose-500/10 border-rose-500/20';
      case 'HIGH': return 'text-orange-400 bg-orange-500/10 border-orange-500/20';
      case 'MEDIUM': return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
      case 'LOW': return 'text-sky-400 bg-sky-500/10 border-sky-500/20';
      default: return 'text-slate-400 bg-slate-800 border-slate-700';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Completed': return 'text-emerald-400';
      case 'Running': return 'text-indigo-400';
      case 'Failed': return 'text-rose-400';
      case 'Pending': return 'text-amber-400';
      default: return 'text-slate-400';
    }
  };

  return (
    <Card noPadding>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-900/80 text-[10px] font-mono uppercase text-slate-400 border-b border-slate-800">
            <tr>
              <th className="py-3 px-4">PR</th>
              <th className="py-3 px-4">Repository</th>
              <th className="py-3 px-4">Changed Component</th>
              <th className="py-3 px-4">Analysis Date</th>
              <th className="py-3 px-4">Cost Impact</th>
              <th className="py-3 px-4">Performance Impact</th>
              <th className="py-3 px-4">Confidence</th>
              <th className="py-3 px-4">Outcome</th>
              <th className="py-3 px-4">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-sans">
            {items.map((item) => (
              <tr 
                key={item.id} 
                onClick={() => onRowClick(item)}
                className={`transition cursor-pointer ${
                  selectedItemId === item.id 
                    ? 'bg-slate-800/80 border-l-2 border-l-indigo-500' 
                    : 'hover:bg-slate-800/40 border-l-2 border-l-transparent'
                }`}
              >
                <td className="py-3.5 px-4 font-mono font-bold text-amber-400">
                  #{item.prNumber}
                </td>
                <td className="py-3.5 px-4 font-mono text-[11px] text-slate-300 truncate max-w-[120px]">
                  {item.repository}
                </td>
                <td className="py-3.5 px-4 text-[11px] text-slate-400 truncate max-w-[150px]">
                  {item.changedComponent}
                </td>
                <td className="py-3.5 px-4 font-mono text-[11px] text-slate-500">
                  {new Date(item.createdAt).toLocaleDateString()}
                </td>
                <td className="py-3.5 px-4 font-mono text-[11px] text-orange-400">
                  {item.costImpactRange.min === item.costImpactRange.max 
                    ? `+${item.costImpactRange.min}%`
                    : `+${item.costImpactRange.min}%–${item.costImpactRange.max}%`}
                </td>
                <td className="py-3.5 px-4 font-mono text-[11px] text-sky-400">
                  {item.performanceImpactRange.min === item.performanceImpactRange.max 
                    ? `${item.performanceImpactRange.min > 0 ? '+' : ''}${item.performanceImpactRange.min}%`
                    : `${item.performanceImpactRange.min > 0 ? '+' : ''}${item.performanceImpactRange.min}%–${item.performanceImpactRange.max}%`}
                </td>
                <td className="py-3.5 px-4">
                  <ConfidenceMeter score={item.confidence} size="sm" showLabel={true} />
                </td>
                <td className="py-3.5 px-4">
                  <span className={`px-2 py-0.5 rounded border text-[10px] font-bold uppercase ${
                    item.outcomeStatus === 'Validated' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                    item.outcomeStatus === 'Not Validated' ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' :
                    'bg-slate-800 text-slate-400 border-slate-700'
                  }`}>
                    {item.outcomeStatus}
                  </span>
                </td>
                <td className="py-3.5 px-4">
                  <span className={`font-semibold ${getStatusColor(item.workflowStatus)}`}>
                    {item.workflowStatus}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
};
