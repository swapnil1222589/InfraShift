import { Analysis } from '../types/analysis';
import { mockAnalyses } from '../mock/analyses';
import { USE_MOCK_DATA, simulateNetworkDelay, apiClient } from './client';

export async function getAnalyses(projectId?: string): Promise<Analysis[]> {
  if (USE_MOCK_DATA) {
    await simulateNetworkDelay();
    if (!projectId) return [...mockAnalyses];
    return mockAnalyses.filter((a) => a.projectId === projectId);
  }
  const query = projectId ? `?projectId=${encodeURIComponent(projectId)}` : '';
  return apiClient<Analysis[]>(`/analyses${query}`);
}

export async function getAnalysisById(id: string): Promise<Analysis | null> {
  if (USE_MOCK_DATA) {
    await simulateNetworkDelay(180);
    const analysis = mockAnalyses.find((a) => a.id === id || String(a.prNumber) === id);
    return analysis ? { ...analysis } : null;
  }
  return apiClient<Analysis>(`/analyses/${id}`);
}

export async function triggerPRAnalysis(projectId: string, prNumber: number, repository: string): Promise<Analysis> {
  if (USE_MOCK_DATA) {
    await simulateNetworkDelay(600);
    const existing = mockAnalyses.find((a) => a.prNumber === prNumber);
    if (existing) return existing;

    const newAnalysis: Analysis = {
      id: `analysis-pr-${prNumber}`,
      projectId,
      prNumber,
      prTitle: `PR #${prNumber}: Infrastructure resource mutation`,
      repository,
      branch: 'feature/cloud-res-update',
      targetBranch: 'main',
      commitSha: '8d39f1c',
      author: {
        name: 'Cloud Engineer',
        username: 'devops-lead',
      },
      status: 'completed',
      risk: 'medium',
      costImpact: '+$14 – $22/mo (+4%)',
      performanceImpact: '+12ms p99 latency',
      confidence: 86,
      changedComponent: 'Lambda Environment & VPC Subnet',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    mockAnalyses.unshift(newAnalysis);
    return newAnalysis;
  }

  return apiClient<Analysis>(`/projects/${projectId}/analyses`, {
    method: 'POST',
    body: JSON.stringify({ prNumber, repository }),
  });
}

export async function getProjectHistory(projectId: string): Promise<Analysis[]> {
  if (USE_MOCK_DATA) {
    await simulateNetworkDelay();
    return mockAnalyses.filter((a) => !projectId || a.projectId === projectId);
  }
  return apiClient<Analysis[]>(`/projects/${projectId}/history`);
}
