export type EvidenceCategory = 'historical_observation' | 'prediction' | 'inference';

export interface HistoricalComparison {
  id: string;
  prNumber: number;
  title: string;
  date: string;
  similarity: number; // percentage
  costChange: string;
  latencyChange: string;
  affectedResource: string;
}

export interface TelemetryDataPoint {
  time: string;
  baseline: number;
  observed: number;
  current: number;
}

export interface TelemetrySignal {
  id: string;
  metricName: string;
  timeRange: string;
  description: string;
  data: TelemetryDataPoint[];
}

export interface Assumptions {
  baselineWindow: string;
  comparisonWindow: string;
  telemetryAvailability: string;
  historicalSamples: number;
  affectedEnvironment: string;
}

export interface ConfidenceScore {
  overall: number;
  evidenceCoverage: number;
  historicalSimilarity: number;
  telemetryAvailability: number;
  modelSupport: number;
}

export interface EvidenceItem {
  id: string;
  category: EvidenceCategory;
  text: string;
}

export interface EvidenceReport {
  analysisId: string;
  status: 'Complete' | 'Insufficient';
  historicalComparisons: HistoricalComparison[];
  telemetrySignals: TelemetrySignal[];
  assumptions: Assumptions;
  items: EvidenceItem[];
  confidence: ConfidenceScore;
}
