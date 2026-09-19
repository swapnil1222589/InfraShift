import React from 'react';
import { AnalysisHistoryItem } from '../../types';
import { X, GitCommit, GitPullRequest, ArrowRight, Activity, Target } from 'lucide-react';
import { Link } from 'react-router-dom';

interface HistoryDetailsDrawerProps {
  item: AnalysisHistoryItem | null;
  onClose: () => void;
}

export const HistoryDetailsDrawer: React.FC<HistoryDetailsDrawerProps> = ({ item, onClose }) => {
  if (!item) return null;

  return (
    <div className="w-full lg:w-96 shrink-0 bg-slate-900 border-l border-slate-800 h-full flex flex-col fixed lg:relative right-0 top-0 bottom-0 z-50">
      <div className="flex items-center justify-between p-4 border-b border-slate-800 bg-slate-950">
        <h3 className="text-sm font-bold text-slate-100 font-sans tracking-tight">Analysis Details</h3>
        <button 
          onClick={onClose}
          className="p-1.5 rounded hover:bg-slate-800 text-slate-400 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-5 space-y-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <GitPullRequest className="w-4 h-4 text-amber-400" />
            <span className="font-mono font-bold text-amber-400 text-sm">PR #{item.prNumber}</span>
          </div>
          <h4 className="text-slate-200 font-medium leading-snug">{item.prTitle}</h4>
          
          <div className="flex items-center gap-2 mt-3 text-xs font-mono text-slate-400">
            <GitCommit className="w-3.5 h-3.5 text-slate-500" />
            <span className="px-1.5 py-0.5 bg-slate-800 rounded">{item.commitHash}</span>
            <span>in</span>
            <span className="font-semibold text-indigo-400">{item.repository}</span>
          </div>
        </div>

        <div className="space-y-3 pt-4 border-t border-slate-800">
          <div>
            <span className="text-[10px] font-mono uppercase text-slate-500 block mb-1">Changed Component</span>
            <p className="text-sm text-slate-300">{item.changedComponent}</p>
          </div>
          <div>
            <span className="text-[10px] font-mono uppercase text-slate-500 block mb-1">Affected Resources</span>
            <p className="text-sm text-slate-300">{item.affectedResourcesCount} AWS resources</p>
          </div>
          <div>
            <span className="text-[10px] font-mono uppercase text-slate-500 block mb-1">Required Safeguards</span>
            <p className="text-sm text-slate-300">{item.recommendationsCount} recommendations</p>
          </div>
        </div>

        <div className="space-y-3 pt-4 border-t border-slate-800">
          <div className="flex items-center gap-3">
            <Activity className="w-5 h-5 text-slate-500" />
            <div>
              <span className="text-[10px] font-mono uppercase text-slate-500 block">Cost Forecast</span>
              <span className="text-sm font-bold font-mono text-orange-400">
                {item.costImpactRange.min === item.costImpactRange.max 
                    ? `+${item.costImpactRange.min}%`
                    : `+${item.costImpactRange.min}% to +${item.costImpactRange.max}%`}
              </span>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <Target className="w-5 h-5 text-slate-500" />
            <div>
              <span className="text-[10px] font-mono uppercase text-slate-500 block">Performance Forecast</span>
              <span className="text-sm font-bold font-mono text-sky-400">
                {item.performanceImpactRange.min === item.performanceImpactRange.max 
                    ? `${item.performanceImpactRange.min > 0 ? '+' : ''}${item.performanceImpactRange.min}%`
                    : `${item.performanceImpactRange.min > 0 ? '+' : ''}${item.performanceImpactRange.min}% to ${item.performanceImpactRange.max > 0 ? '+' : ''}${item.performanceImpactRange.max}%`}
              </span>
            </div>
          </div>
        </div>

      </div>

      <div className="p-4 border-t border-slate-800 bg-slate-950 flex flex-col gap-3">
        <Link 
          to={`/analyses/${item.id}`}
          className="w-full flex items-center justify-center gap-2 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm transition-colors"
        >
          Open Analysis
          <ArrowRight className="w-4 h-4" />
        </Link>
        
        <Link 
          to={`/analyses/${item.id}/outcome`}
          className="w-full flex items-center justify-center gap-2 py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium text-sm transition-colors border border-slate-700"
        >
          View Outcome
        </Link>
      </div>
    </div>
  );
};
