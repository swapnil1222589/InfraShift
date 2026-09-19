export type RecommendationPriority = 'HIGH' | 'MEDIUM' | 'LOW';
export type RecommendationStatus = 'Open' | 'Under Review' | 'Completed';

export interface Recommendation {
  id: string;
  analysisId: string;
  priority: RecommendationPriority;
  recommendation: string;
  reason: string;
  affectedResource: string;
  suggestedValidation: string;
  evidence: string;
  status: RecommendationStatus;
  reviewedAt?: string;
}

export interface DeploymentDecision {
  analysisId: string;
  riskSummary: string;
  evidenceAvailabilityScore: number;
  confidenceScore: number;
  recommendationCount: number;
  decisionStatus: 'pending' | 'approved_controlled_test' | 'review_requested';
  decisionNote?: string;
  decidedBy?: string;
  decidedAt?: string;
}
