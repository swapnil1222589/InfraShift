import { EvidenceReport } from '../types';
import { mockHistoricalComparisons } from './historicalComparisons';
import { mockTelemetrySignals } from './telemetry';

export const mockEvidenceReports: Record<string, EvidenceReport> = {
  'analysis-pr-248': {
    analysisId: 'analysis-pr-248',
    status: 'Complete',
    historicalComparisons: mockHistoricalComparisons,
    telemetrySignals: mockTelemetrySignals,
    assumptions: {
      baselineWindow: 'Previous 14 days',
      comparisonWindow: 'Previous 7 comparable deployments',
      telemetryAvailability: '96%',
      historicalSamples: 18,
      affectedEnvironment: 'Production-like staging',
    },
    confidence: {
      overall: 82,
      evidenceCoverage: 91,
      historicalSimilarity: 78,
      telemetryAvailability: 96,
      modelSupport: 84,
    },
    items: [
      {
        id: 'ev-1',
        category: 'historical_observation',
        text: 'Comparable deployments showed an 8-13% increase in DynamoDB read activity.',
      },
      {
        id: 'ev-2',
        category: 'prediction',
        text: 'InfraShift forecasts an 8-14% increase in DynamoDB read activity.',
      },
      {
        id: 'ev-3',
        category: 'inference',
        text: 'The changed query pattern may increase database read activity.',
      },
    ],
  },
  'analysis-pr-249': {
    analysisId: 'analysis-pr-249',
    status: 'Insufficient',
    historicalComparisons: [],
    telemetrySignals: [],
    assumptions: {
      baselineWindow: 'Previous 2 days',
      comparisonWindow: 'Previous 2 comparable deployments',
      telemetryAvailability: 'Unavailable',
      historicalSamples: 2,
      affectedEnvironment: 'Dev',
    },
    confidence: {
      overall: 20,
      evidenceCoverage: 15,
      historicalSimilarity: 30,
      telemetryAvailability: 0,
      modelSupport: 25,
    },
    items: [],
  }
};
