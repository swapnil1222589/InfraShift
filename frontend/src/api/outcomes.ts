import { DeploymentOutcome } from '../types/outcome';
import { mockOutcomePR248 } from '../mock/outcomes';
import { USE_MOCK_DATA, simulateNetworkDelay, apiClient } from './client';

export async function getOutcomeByAnalysisId(analysisId: string): Promise<DeploymentOutcome | null> {
  if (USE_MOCK_DATA) {
    await simulateNetworkDelay(190);
    return { ...mockOutcomePR248, analysisId };
  }
  return apiClient<DeploymentOutcome>(`/analyses/${analysisId}/outcome`);
}

export async function recordDeploymentOutcome(outcomeData: Partial<DeploymentOutcome>): Promise<DeploymentOutcome> {
  if (USE_MOCK_DATA) {
    await simulateNetworkDelay(300);
    return {
      ...mockOutcomePR248,
      ...outcomeData,
    };
  }
  return apiClient<DeploymentOutcome>(`/analyses/${outcomeData.analysisId}/outcome`, {
    method: 'POST',
    body: JSON.stringify(outcomeData),
  });
}
