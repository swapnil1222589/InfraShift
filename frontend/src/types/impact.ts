export type ImpactLevel = 'none' | 'low' | 'moderate' | 'high' | 'critical';
export type NodeType = 'pr' | 'code' | 'service' | 'lambda' | 'dynamodb' | 'sqs' | 'apigateway' | 's3' | 'rds' | 'cloudwatch';

export interface ImpactNode {
  id: string;
  label: string;
  type: NodeType;
  awsService: string;
  region?: string;
  status: 'healthy' | 'at_risk' | 'modified' | 'degraded';
  impactLevel: ImpactLevel;
  metrics?: {
    currentUtilization: string;
    expectedImpact: string;
    throughputOrConcurrency?: string;
  };
  evidenceSummary?: string;
  tags?: Record<string, string>;
}

export interface ImpactEdge {
  id: string;
  source: string;
  target: string;
  relation: string; // e.g. "modifies", "executes", "queries", "emits_to"
  animated?: boolean;
}

export interface ImpactGraphData {
  analysisId: string;
  nodes: ImpactNode[];
  edges: ImpactEdge[];
}
