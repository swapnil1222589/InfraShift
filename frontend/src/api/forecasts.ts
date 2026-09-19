import { Forecast } from '../types/forecast';
import { mockForecastPR248 } from '../mock/forecasts';
import { USE_MOCK_DATA, simulateNetworkDelay, apiClient } from './client';

export async function getForecastByAnalysisId(analysisId: string): Promise<Forecast | null> {
  if (USE_MOCK_DATA) {
    await simulateNetworkDelay(160);
    return { ...mockForecastPR248, analysisId };
  }
  return apiClient<Forecast>(`/analyses/${analysisId}/forecast`);
}
