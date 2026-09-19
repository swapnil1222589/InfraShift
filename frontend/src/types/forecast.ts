export interface MetricRange {
  min: number;
  max: number;
  unit: string;
  percentageChangeMin: number;
  percentageChangeMax: number;
}

export interface CostForecast {
  currentMonthlyBaselineUsd: number;
  projectedMonthlyMinUsd: number;
  projectedMonthlyMaxUsd: number;
  percentageChangeMin: number;
  percentageChangeMax: number;
  confidence: number; // 0-100
  currency: string;
  driverBreakdown: {
    resource: string;
    awsService: string;
    estimatedDeltaUsd: number;
    description: string;
  }[];
}

export interface LatencyMetric {
  p50CurrentMs: number;
  p50ProjectedMs: number;
  p90CurrentMs: number;
  p90ProjectedMs: number;
  p99CurrentMs: number;
  p99ProjectedMs: number;
  confidence: number;
}

export interface PerformanceForecast {
  latency: LatencyMetric;
  invocationVolumeDeltaPct: number;
  resourceUtilizationDeltaPct: number;
  throttlingRiskPct: number;
  confidence: number;
}

export interface Forecast {
  id: string;
  analysisId: string;
  cost: CostForecast;
  performance: PerformanceForecast;
  generatedAt: string;
}
