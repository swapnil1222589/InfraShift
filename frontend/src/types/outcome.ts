export interface ForecastVsActualPoint {
  timestamp: string;
  metric: string;
  baseline: number;
  forecastMin: number;
  forecastMax: number;
  actual: number;
  unit: string;
}

export interface DeploymentOutcome {
  id: string;
  analysisId: string;
  prNumber: number;
  deployedAt: string;
  environment: string;
  forecastCostRange: {
    minPct: number;
    maxPct: number;
    minUsd: number;
    maxUsd: number;
  };
  actualCost: {
    deltaPct: number;
    deltaUsd: number;
  };
  forecastLatencyRange: {
    minPct: number;
    maxPct: number;
    p99MinMs: number;
    p99MaxMs: number;
  };
  actualLatency: {
    deltaPct: number;
    p99Ms: number;
  };
  costForecastErrorPct: number;
  latencyForecastErrorPct: number;
  lambdaDurationErrorPct: number;
  dynamoDbReadErrorPct: number;
  
  forecastLambdaDurationRange: {
    minPct: number;
    maxPct: number;
  };
  actualLambdaDurationPct: number;
  
  forecastDynamoDbRange: {
    minPct: number;
    maxPct: number;
  };
  actualDynamoDbPct: number;

  deploymentResult: 'healthy' | 'stabilized' | 'investigating' | 'breached_threshold' | 'Successful';
  validationStatus: 'verified' | 'monitoring' | 'discrepancy_flagged' | 'Validated';
  
  validationTimeline: {
    analysisCreated: string;
    forecastGenerated: string;
    controlledDeployment: string;
    telemetryCollected: string;
    forecastCompared: string;
    outcomeValidated: string;
  };
  
  validationEvidence: {
    cloudWatchMetrics: string;
    deploymentTelemetry: string;
    comparisonWindow: string;
    baselineWindow: string;
    historicalComparison: string;
  };

  chartData: ForecastVsActualPoint[];
  postMortemNotes?: string;
}
