export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';
export type AnalysisStatus = 'completed' | 'analyzing' | 'flagged' | 'failed' | 'queued';
export type BlastRadius = 'isolated' | 'service-level' | 'multi-service' | 'cross-account';

export interface TimelineStep {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'warning';
  completedAt?: string;
  durationMs?: number;
}

export interface ChangedFile {
  path: string;
  status: 'modified' | 'added' | 'deleted';
  additions: number;
  deletions: number;
  functions: string[];
}

export interface ChangeSummary {
  changedFiles: ChangedFile[];
  changedFunctionsCount: number;
  changeType: 'Database Query Pattern' | 'Lambda Memory/Runtime' | 'API Gateway Handler' | 'SQS Batch Processing' | 'DynamoDB Index Usage';
  blastRadius: BlastRadius;
  primaryAffectedService: string;
  totalAdditions: number;
  totalDeletions: number;
}

export interface Analysis {
  id: string;
  projectId: string;
  prNumber: number;
  prTitle: string;
  repository: string;
  branch: string;
  targetBranch: string;
  commitSha: string;
  author: {
    name: string;
    avatarUrl?: string;
    username: string;
  };
  status: AnalysisStatus;
  risk: RiskLevel;
  costImpact: string;
  performanceImpact: string;
  confidence: number; // 0 to 100
  changedComponent: string;
  createdAt: string;
  updatedAt: string;
  summary?: ChangeSummary;
  timeline?: TimelineStep[];
}
