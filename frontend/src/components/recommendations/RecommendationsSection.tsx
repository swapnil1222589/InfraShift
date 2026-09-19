import React, { useState } from 'react';
import { Recommendation, DeploymentDecision } from '../../types';
import { RecommendationCard } from './RecommendationCard';
import { RecommendationFilters } from './RecommendationFilters';
import { ValidationChecklist } from './ValidationChecklist';
import { ReviewPanel } from './ReviewPanel';

interface RecommendationsSectionProps {
  recommendations: Recommendation[];
  decision: DeploymentDecision | null;
  onDecision: (decisionType: 'approved_controlled_test' | 'review_requested', note?: string) => Promise<void>;
}

export const RecommendationsSection: React.FC<RecommendationsSectionProps> = ({
  recommendations,
  decision,
  onDecision,
}) => {
  const [priorityFilter, setPriorityFilter] = useState('All');
  const [statusFilter, setStatusFilter] = useState('All');
  const [resourceFilter, setResourceFilter] = useState('All');

  const availableResources = Array.from(new Set(recommendations.map(r => r.affectedResource)));

  const filteredRecommendations = recommendations.filter(rec => {
    if (priorityFilter !== 'All' && rec.priority !== priorityFilter) return false;
    if (statusFilter !== 'All' && rec.status !== statusFilter) return false;
    if (resourceFilter !== 'All' && rec.affectedResource !== resourceFilter) return false;
    return true;
  });

  return (
    <div className="space-y-8 animate-in fade-in duration-300 relative">
      <RecommendationFilters
        priorityFilter={priorityFilter}
        setPriorityFilter={setPriorityFilter}
        statusFilter={statusFilter}
        setStatusFilter={setStatusFilter}
        resourceFilter={resourceFilter}
        setResourceFilter={setResourceFilter}
        availableResources={availableResources}
      />

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        <div className="xl:col-span-2 space-y-4">
          <h3 className="text-xl font-bold text-slate-100 mb-2">Required Actions</h3>
          {filteredRecommendations.length === 0 ? (
            <div className="p-8 text-center bg-slate-900/50 rounded-xl border border-slate-800 text-slate-500">
              No recommendations match the selected filters.
            </div>
          ) : (
            <div className="space-y-4">
              {filteredRecommendations.map(rec => (
                <RecommendationCard key={rec.id} rec={rec} />
              ))}
            </div>
          )}
        </div>

        <div className="space-y-6">
          <div className="sticky top-6">
            <ValidationChecklist />
          </div>
        </div>
      </div>

      {decision && (
        <ReviewPanel 
          decision={decision} 
          recommendations={recommendations} 
          onDecision={onDecision} 
        />
      )}
    </div>
  );
};
