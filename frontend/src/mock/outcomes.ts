import { DeploymentOutcome } from '../types';

export const mockOutcomePR248: DeploymentOutcome = {
  id: 'outcome-pr-248',
  analysisId: 'analysis-pr-248',
  prNumber: 248,
  deployedAt: '2026-09-19T18:00:00Z',
  environment: 'Staging (us-east-1)',
  forecastCostRange: {
    minPct: 8.0,
    maxPct: 21.0,
    minUsd: 45.0,
    maxUsd: 51.0,
  },
  actualCost: {
    deltaPct: 11.0,
    deltaUsd: 46.62,
  },
  forecastLatencyRange: {
    minPct: 5.0,
    maxPct: 12.0,
    p99MinMs: 651,
    p99MaxMs: 708,
  },
  actualLatency: {
    deltaPct: 8.0,
    p99Ms: 672,
  },
  costForecastErrorPct: 1.2,
  latencyForecastErrorPct: 2.1,
  
  lambdaDurationErrorPct: 1.8,
  dynamoDbReadErrorPct: 2.4,
  
  forecastLambdaDurationRange: {
    minPct: 4,
    maxPct: 10,
  },
  actualLambdaDurationPct: 7,
  
  forecastDynamoDbRange: {
    minPct: 8,
    maxPct: 14,
  },
  actualDynamoDbPct: 11,

  deploymentResult: 'Successful',
  validationStatus: 'Validated',
  
  validationTimeline: {
    analysisCreated: '2026-09-17T09:00:00Z',
    forecastGenerated: '2026-09-17T09:05:00Z',
    controlledDeployment: '2026-09-18T10:00:00Z',
    telemetryCollected: '2026-09-19T10:00:00Z',
    forecastCompared: '2026-09-19T10:05:00Z',
    outcomeValidated: '2026-09-19T10:30:00Z',
  },
  
  validationEvidence: {
    cloudWatchMetrics: 'Available',
    deploymentTelemetry: 'Available',
    comparisonWindow: '24 hours',
    baselineWindow: '14 days',
    historicalComparison: 'Available',
  },

  postMortemNotes: 'Forecast aligned with observed behavior',
  chartData: [
    { timestamp: '00:00', metric: 'Cost Rate ($/hr)', baseline: 11.2, forecastMin: 12.1, forecastMax: 13.5, actual: 11.3, unit: '$/hr' },
    { timestamp: '04:00', metric: 'Cost Rate ($/hr)', baseline: 11.4, forecastMin: 12.3, forecastMax: 13.8, actual: 11.4, unit: '$/hr' },
    { timestamp: '08:00', metric: 'Cost Rate ($/hr)', baseline: 12.8, forecastMin: 13.8, forecastMax: 15.5, actual: 12.9, unit: '$/hr' },
    { timestamp: '12:00', metric: 'Cost Rate ($/hr)', baseline: 14.2, forecastMin: 15.3, forecastMax: 17.2, actual: 14.3, unit: '$/hr' },
    { timestamp: '16:00 (Deploy)', metric: 'Cost Rate ($/hr)', baseline: 14.5, forecastMin: 15.7, forecastMax: 17.5, actual: 16.1, unit: '$/hr' },
    { timestamp: '20:00', metric: 'Cost Rate ($/hr)', baseline: 15.1, forecastMin: 16.3, forecastMax: 18.3, actual: 16.8, unit: '$/hr' },
    { timestamp: '24:00', metric: 'Cost Rate ($/hr)', baseline: 13.0, forecastMin: 14.0, forecastMax: 15.7, actual: 14.5, unit: '$/hr' },
  ],
};
