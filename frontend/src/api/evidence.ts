import { EvidenceReport } from '../types';
import { mockEvidenceReports } from '../mock/evidence';
import { USE_MOCK_DATA, simulateNetworkDelay, apiClient } from './client';

export async function getEvidenceByAnalysisId(analysisId: string): Promise<EvidenceReport | null> {
  if (USE_MOCK_DATA) {
    await simulateNetworkDelay(180);
    return mockEvidenceReports[analysisId] || mockEvidenceReports['analysis-pr-249']; // fallback to insufficient
  }
  return apiClient<EvidenceReport>(`/analyses/${analysisId}/evidence`);
}
