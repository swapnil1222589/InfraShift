import React from 'react';
import { ShieldAlert, CheckCircle } from 'lucide-react';
import { DeploymentDecision, Recommendation } from '../../types';

interface ReviewPanelProps {
  decision: DeploymentDecision;
  recommendations: Recommendation[];
  onDecision: (d: 'approved_controlled_test' | 'review_requested') => void;
}

export const ReviewPanel: React.FC<ReviewPanelProps> = ({ decision, recommendations, onDecision }) => {
  const highPriorityCount = recommendations.filter(r => r.priority === 'HIGH').length;
  
  return (
    <div className="bg-slate-900 border-t border-slate-700/50 p-6 -mx-8 -mb-8 mt-8 sticky bottom-0 z-10 shadow-[0_-10px_40px_rgba(0,0,0,0.5)]">
      <div className="max-w-5xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
        
        <div className="flex flex-col gap-2">
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            Ready for Controlled Testing?
          </h2>
          
          <div className="flex flex-wrap items-center gap-4 text-sm font-mono mt-1">
            <div className="flex items-center gap-1.5">
              <span className="text-slate-500 uppercase tracking-wider text-[10px]">Evidence:</span>
              <span className="text-emerald-400 font-medium">Sufficient</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-slate-500 uppercase tracking-wider text-[10px]">Confidence:</span>
              <span className="text-slate-200 font-medium">{decision.confidenceScore}%</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-slate-500 uppercase tracking-wider text-[10px]">Recommendations:</span>
              <span className="text-slate-200 font-medium">{recommendations.length}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-slate-500 uppercase tracking-wider text-[10px]">High Priority:</span>
              <span className="text-rose-400 font-bold">{highPriorityCount}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <button 
            onClick={() => onDecision('review_requested')}
            className="px-5 py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium border border-slate-600 transition-colors flex items-center gap-2"
          >
            <ShieldAlert className="w-4 h-4" />
            Request Review
          </button>
          
          <button 
            onClick={() => onDecision('approved_controlled_test')}
            className="px-5 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium border border-emerald-500 transition-colors flex items-center gap-2 shadow-lg shadow-emerald-900/50"
          >
            <CheckCircle className="w-4 h-4" />
            Approve for Controlled Test
          </button>
        </div>
        
      </div>
    </div>
  );
};
