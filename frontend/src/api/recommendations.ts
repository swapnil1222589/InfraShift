import { Recommendation, DeploymentDecision } from '../types';
import { mockRecommendations } from '../mock/recommendations';
import { USE_MOCK_DATA, simulateNetworkDelay, apiClient } from './client';

export async function getRecommendationsByAnalysisId(analysisId: string): Promise<Recommendation[]> {
  if (USE_MOCK_DATA) {
    await simulateNetworkDelay(160);
    return [...mockRecommendations];
  }
  return apiClient<Recommendation[]>(`/analyses/${analysisId}/recommendations`);
}

const mockDecision: DeploymentDecision = {
  analysisId: 'analysis-pr-248',
  riskSummary: 'Low Risk',
  evidenceAvailabilityScore: 91,
  confidenceScore: 82,
  recommendationCount: 3,
  decisionStatus: 'pending'
};

export async function getDeploymentDecision(analysisId: string): Promise<DeploymentDecision> {
  if (USE_MOCK_DATA) {
    await simulateNetworkDelay(140);
    return { ...mockDecision, analysisId };
  }
  return apiClient<DeploymentDecision>(`/analyses/${analysisId}/decision`);
}

export async function submitDeploymentDecision(
  analysisId: string,
  decision: 'approved_controlled_test' | 'review_requested',
  note?: string
): Promise<DeploymentDecision> {
  if (USE_MOCK_DATA) {
    await simulateNetworkDelay(250);
    mockDecision.decisionStatus = decision;
    mockDecision.decisionNote = note;
    mockDecision.decidedAt = new Date().toISOString();
    mockDecision.decidedBy = 'Lead DevOps Engineer';
    return { ...mockDecision };
  }
  return apiClient<DeploymentDecision>(`/analyses/${analysisId}/decision`, {
    method: 'POST',
    body: JSON.stringify({ decision, note }),
  });
}
