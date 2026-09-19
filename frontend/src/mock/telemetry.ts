import { TelemetrySignal } from '../types';

export const mockTelemetrySignals: TelemetrySignal[] = [
  {
    id: 'ts-1',
    metricName: 'Request Volume',
    timeRange: 'Last 14 days',
    description: 'Overall request volume has remained stable, providing a solid baseline for comparison.',
    data: [
      { time: '10:00', baseline: 120, observed: 125, current: 122 },
      { time: '11:00', baseline: 130, observed: 132, current: 128 },
      { time: '12:00', baseline: 180, observed: 185, current: 182 },
      { time: '13:00', baseline: 140, observed: 144, current: 141 },
      { time: '14:00', baseline: 135, observed: 138, current: 136 },
      { time: '15:00', baseline: 150, observed: 155, current: 151 },
    ],
  },
  {
    id: 'ts-2',
    metricName: 'Latency',
    timeRange: 'Last 14 days',
    description: 'Average latency spikes by 7-10% during similar database optimizations.',
    data: [
      { time: '10:00', baseline: 45, observed: 48, current: 46 },
      { time: '11:00', baseline: 48, observed: 52, current: 49 },
      { time: '12:00', baseline: 65, observed: 72, current: 67 },
      { time: '13:00', baseline: 50, observed: 55, current: 52 },
      { time: '14:00', baseline: 47, observed: 51, current: 48 },
      { time: '15:00', baseline: 55, observed: 61, current: 57 },
    ],
  },
  {
    id: 'ts-3',
    metricName: 'Lambda Duration',
    timeRange: 'Last 14 days',
    description: 'Lambda execution duration consistently increases when processing heavier DynamoDB payloads.',
    data: [
      { time: '10:00', baseline: 110, observed: 118, current: 112 },
      { time: '11:00', baseline: 115, observed: 124, current: 117 },
      { time: '12:00', baseline: 145, observed: 158, current: 148 },
      { time: '13:00', baseline: 120, observed: 129, current: 122 },
      { time: '14:00', baseline: 118, observed: 126, current: 120 },
      { time: '15:00', baseline: 130, observed: 142, current: 132 },
    ],
  },
  {
    id: 'ts-4',
    metricName: 'DynamoDB Read Activity',
    timeRange: 'Last 14 days',
    description: 'DynamoDB read activity has increased during previous comparable deployments by 8-13%.',
    data: [
      { time: '10:00', baseline: 400, observed: 440, current: 405 },
      { time: '11:00', baseline: 420, observed: 465, current: 425 },
      { time: '12:00', baseline: 600, observed: 670, current: 610 },
      { time: '13:00', baseline: 450, observed: 495, current: 455 },
      { time: '14:00', baseline: 430, observed: 475, current: 435 },
      { time: '15:00', baseline: 500, observed: 555, current: 505 },
    ],
  },
];
