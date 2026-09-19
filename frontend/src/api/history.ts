import { AnalysisHistoryItem, HistorySummaryData } from '../types';
import { mockHistory, mockHistorySummary } from '../mock/history';

export const getHistory = async (): Promise<{ items: AnalysisHistoryItem[]; summary: HistorySummaryData }> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        items: mockHistory,
        summary: mockHistorySummary,
      });
    }, 800);
  });
};
