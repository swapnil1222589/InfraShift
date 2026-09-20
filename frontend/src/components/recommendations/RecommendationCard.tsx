import React, { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Card } from '../common/Card';
import { Recommendation, RecommendationStatus } from '../../types';
import { AlertCircle, ArrowRight, Box, Shield, CheckCircle2, Clock } from 'lucide-react';

interface RecommendationCardProps {
  rec: Recommendation;
}

import { useToast } from '../../contexts/ToastContext';

export const RecommendationCard: React.FC<RecommendationCardProps> = ({ rec }) => {
  const { id } = useParams<{ id: string }>();
  const [status, setStatus] = useState<RecommendationStatus>(rec.status);
  const [reviewedAt, setReviewedAt] = useState<string | undefined>(rec.reviewedAt);
  const { addToast } = useToast();

  const getPriorityStyle = () => {
    switch (rec.priority) {
      case 'HIGH':
        return 'text-rose-400 bg-rose-500/10 border-rose-500/20';
      case 'MEDIUM':
        return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
      case 'LOW':
        return 'text-sky-400 bg-sky-500/10 border-sky-500/20';
    }
  };

  const handleMarkReview = () => {
    if (status === 'Open') {
      setStatus('Under Review');
      setReviewedAt(new Date().toISOString());
      addToast('Recommendation marked for review', 'info');
    } else if (status === 'Under Review') {
      setStatus('Completed');
      addToast('Recommendation marked as completed', 'success');
    }
  };

  return (
    <Card className={`flex flex-col gap-4 border-l-4 ${rec.priority === 'HIGH' ? 'border-l-rose-500' : rec.priority === 'MEDIUM' ? 'border-l-amber-500' : 'border-l-sky-500'}`}>
      <div className="flex justify-between items-start">
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-2">
            <span className={`px-2 py-0.5 rounded border text-xs font-bold tracking-wider ${getPriorityStyle()}`}>
              {rec.priority} PRIORITY
            </span>
            {status !== 'Open' && (
              <span className={`flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded border ${status === 'Completed' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20'}`}>
                {status === 'Completed' ? <CheckCircle2 className="w-3 h-3" /> : <Clock className="w-3 h-3" />}
                {status}
              </span>
            )}
          </div>
          <h3 className="text-lg font-semibold text-slate-100">{rec.recommendation}</h3>
        </div>
      </div>

      <div className="bg-slate-800/30 rounded border border-slate-700/50 p-4 space-y-3 mt-1">
        <div>
          <span className="block text-xs font-semibold uppercase text-slate-500 mb-1">Reason</span>
          <p className="text-sm text-slate-300">{rec.reason}</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2 border-t border-slate-700/50">
          <div>
            <span className="block text-xs font-semibold uppercase text-slate-500 mb-1 flex items-center gap-1">
              <Box className="w-3 h-3" /> Affected Resource
            </span>
            <p className="text-sm font-medium text-slate-200">{rec.affectedResource}</p>
          </div>
          <div>
            <span className="block text-xs font-semibold uppercase text-slate-500 mb-1 flex items-center gap-1">
              <Shield className="w-3 h-3" /> Suggested Validation
            </span>
            <p className="text-sm font-medium text-slate-200">{rec.suggestedValidation}</p>
          </div>
        </div>
        
        <div className="pt-2 border-t border-slate-700/50">
          <span className="block text-xs font-semibold uppercase text-slate-500 mb-1">Evidence</span>
          <p className="text-sm text-indigo-300">{rec.evidence}</p>
        </div>
      </div>

      <div className="flex items-center justify-between mt-2">
        <div className="text-xs text-slate-500 flex items-center gap-2">
          {reviewedAt && (
            <span>Timestamp: {new Date(reviewedAt).toLocaleString()}</span>
          )}
        </div>
        <div className="flex items-center gap-3">
          <Link 
            to={`/analyses/${id}/evidence`}
            className="text-sm font-medium text-slate-400 hover:text-slate-300 transition-colors"
          >
            View Evidence
          </Link>
          <button 
            onClick={handleMarkReview}
            disabled={status === 'Completed'}
            className={`px-4 py-1.5 rounded text-sm font-medium transition-colors ${
              status === 'Completed' 
                ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700' 
                : 'bg-indigo-600 hover:bg-indigo-500 text-white'
            }`}
          >
            {status === 'Open' ? 'Mark for Review' : status === 'Under Review' ? 'Mark Completed' : 'Completed'}
          </button>
        </div>
      </div>
    </Card>
  );
};
