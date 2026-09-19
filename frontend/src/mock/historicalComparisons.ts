import { HistoricalComparison } from '../types';

export const mockHistoricalComparisons: HistoricalComparison[] = [
  {
    id: 'hc-1',
    prNumber: 219,
    title: 'Optimize customer order queries',
    date: '2023-09-12',
    similarity: 86,
    costChange: '+11%',
    latencyChange: '+7%',
    affectedResource: 'DynamoDB / orders-table',
  },
  {
    id: 'hc-2',
    prNumber: 184,
    title: 'Add secondary index to orders',
    date: '2023-07-28',
    similarity: 74,
    costChange: '+8%',
    latencyChange: '+4%',
    affectedResource: 'DynamoDB / orders-table',
  },
  {
    id: 'hc-3',
    prNumber: 142,
    title: 'Batch order processing worker',
    date: '2023-05-15',
    similarity: 68,
    costChange: '+14%',
    latencyChange: '+2%',
    affectedResource: 'DynamoDB / orders-table',
  },
];
