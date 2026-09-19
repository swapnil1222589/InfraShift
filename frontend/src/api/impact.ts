import { ImpactGraphData } from '../types/impact';
import { mockImpactPR248 } from '../mock/impact';
import { USE_MOCK_DATA, simulateNetworkDelay, apiClient } from './client';

export async function getImpactGraphByAnalysisId(analysisId: string): Promise<ImpactGraphData | null> {
  if (USE_MOCK_DATA) {
    await simulateNetworkDelay(200);
    return { ...mockImpactPR248, analysisId };
  }
  return apiClient<ImpactGraphData>(`/analyses/${analysisId}/impact`);
}
