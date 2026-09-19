export interface HistorySummaryData {
  totalAnalyses: number;
  completed: number;
  pending: number;
  validatedOutcomes: number;
}

export type HistoryRisk = 'HIGH' | 'MEDIUM' | 'LOW' | 'CRITICAL';
export type HistoryStatus = 'Completed' | 'Running' | 'Failed' | 'Pending';
export type HistoryOutcome = 'Validated' | 'Not Validated' | 'Awaiting Deployment';

export interface AnalysisHistoryItem {
  id: string;
  prNumber: number;
  prTitle: string;
  repository: string;
  commitHash: string;
  changedComponent: string;
  affectedResourcesCount: number;
  createdAt: string;
  costImpactRange: { min: number; max: number };
  performanceImpactRange: { min: number; max: number };
  confidence: number;
  recommendationsCount: number;
  outcomeStatus: HistoryOutcome;
  workflowStatus: HistoryStatus;
  risk: HistoryRisk;
}
