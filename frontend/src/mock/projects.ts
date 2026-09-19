import { Project, Environment } from '../types/project';

export const mockProjects: Project[] = [
  {
    id: 'proj-checkout-core',
    name: 'checkout-service',
    repository: 'aws-samples/serverless-checkout-api',
    defaultBranch: 'main',
    environments: ['production', 'staging', 'development'],
    awsAccount: '124982148192 (us-east-1)',
    region: 'us-east-1',
    status: 'active',
    lastAnalysisAt: '2026-09-19T14:32:00Z',
  },
  {
    id: 'proj-inventory-hub',
    name: 'inventory-pipeline',
    repository: 'acme-corp/inventory-stream-worker',
    defaultBranch: 'main',
    environments: ['production', 'staging'],
    awsAccount: '992019481231 (us-west-2)',
    region: 'us-west-2',
    status: 'active',
    lastAnalysisAt: '2026-09-18T09:15:00Z',
  },
  {
    id: 'proj-auth-identity',
    name: 'auth-gateway',
    repository: 'acme-corp/cognito-custom-authorizer',
    defaultBranch: 'master',
    environments: ['production', 'staging', 'development'],
    awsAccount: '448102948110 (eu-west-1)',
    region: 'eu-west-1',
    status: 'active',
    lastAnalysisAt: '2026-09-17T21:40:00Z',
  },
];

export const mockEnvironments: Environment[] = [
  {
    id: 'env-prod',
    name: 'Production (us-east-1)',
    stage: 'production',
    region: 'us-east-1',
    awsAccountId: '124982148192',
  },
  {
    id: 'env-stage',
    name: 'Staging (us-east-1)',
    stage: 'staging',
    region: 'us-east-1',
    awsAccountId: '871928371900',
  },
  {
    id: 'env-dev',
    name: 'Dev-Sandbox (us-west-2)',
    stage: 'development',
    region: 'us-west-2',
    awsAccountId: '312891723812',
  },
];
