export interface Project {
  id: string;
  name: string;
  repository: string;
  defaultBranch: string;
  environments: string[];
  awsAccount: string;
  region: string;
  status: 'active' | 'configuring' | 'inactive';
  lastAnalysisAt?: string;
}

export interface Environment {
  id: string;
  name: string;
  stage: 'production' | 'staging' | 'development';
  region: string;
  awsAccountId: string;
}
