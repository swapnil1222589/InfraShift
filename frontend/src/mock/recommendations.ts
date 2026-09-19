import { Recommendation } from '../types';

export const mockRecommendations: Recommendation[] = [
  {
    id: 'rec-1',
    analysisId: 'analysis-pr-248',
    priority: 'HIGH',
    recommendation: 'Run a load test against the updated DynamoDB access pattern.',
    reason: 'Historical deployments with similar query changes increased database read activity by up to 14%.',
    affectedResource: 'DynamoDB / orders-table',
    suggestedValidation: 'Test with production-like traffic simulating peak hours.',
    evidence: '3 comparable deployments',
    status: 'Open',
  },
  {
    id: 'rec-2',
    analysisId: 'analysis-pr-248',
    priority: 'MEDIUM',
    recommendation: 'Review DynamoDB read capacity provisioning.',
    reason: 'Projected increase in read activity may lead to throttling if auto-scaling is not aggressive enough.',
    affectedResource: 'DynamoDB / orders-table',
    suggestedValidation: 'Verify auto-scaling policies and minimum capacity settings.',
    evidence: 'Telemetry forecast indicates +8% to +14% read increase',
    status: 'Under Review',
    reviewedAt: '2026-09-19T10:24:00Z',
  },
  {
    id: 'rec-3',
    analysisId: 'analysis-pr-248',
    priority: 'LOW',
    recommendation: 'Monitor API Gateway latency metrics closely post-deployment.',
    reason: 'Downstream latency impact is possible due to lambda duration increase.',
    affectedResource: 'API Gateway / checkout-api',
    suggestedValidation: 'Ensure CloudWatch alarms are configured for p95 latency.',
    evidence: 'Historical latency increased by ~7%',
    status: 'Completed',
    reviewedAt: '2026-09-18T14:10:00Z',
  },
];
