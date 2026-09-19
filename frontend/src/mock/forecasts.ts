import { Forecast } from '../types/forecast';

export const mockForecastPR248: Forecast = {
  id: 'forecast-pr-248',
  analysisId: 'analysis-pr-248',
  generatedAt: '2026-09-19T14:30:11Z',
  cost: {
    currentMonthlyBaselineUsd: 340.0,
    projectedMonthlyMinUsd: 382.0,
    projectedMonthlyMaxUsd: 391.0,
    percentageChangeMin: 8.0,
    percentageChangeMax: 21.0,
    confidence: 82,
    currency: 'USD',
    driverBreakdown: [
      {
        awsService: 'Amazon DynamoDB',
        resource: 'OrdersTable (GlobalSecondaryIndex: CustomerDateIdx)',
        estimatedDeltaUsd: 32.5,
        description: 'New projection fields require additional read capacity units (RCU) during composite key query evaluations.',
      },
      {
        awsService: 'AWS Lambda',
        resource: 'processOrderFunction (Memory: 1024MB)',
        estimatedDeltaUsd: 11.2,
        description: 'Slightly higher compute duration while unpacking enriched payload attributes in worker thread.',
      },
      {
        awsService: 'Amazon CloudWatch',
        resource: 'Custom Metrics & Log Group /aws/lambda/processOrder',
        estimatedDeltaUsd: 3.1,
        description: 'Additional structured JSON log telemetry for order validation tracing.',
      },
    ],
  },
  performance: {
    latency: {
      p50CurrentMs: 185,
      p50ProjectedMs: 198,
      p90CurrentMs: 340,
      p90ProjectedMs: 382,
      p99CurrentMs: 620,
      p99ProjectedMs: 708,
      confidence: 84,
    },
    invocationVolumeDeltaPct: 2.1,
    resourceUtilizationDeltaPct: 28.4,
    throttlingRiskPct: 18.5,
    confidence: 82,
  },
};
