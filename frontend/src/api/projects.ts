import { Project, Environment } from '../types/project';
import { mockProjects, mockEnvironments } from '../mock/projects';
import { USE_MOCK_DATA, simulateNetworkDelay, apiClient } from './client';

export async function getProjects(): Promise<Project[]> {
  if (USE_MOCK_DATA) {
    await simulateNetworkDelay();
    return [...mockProjects];
  }
  return apiClient<Project[]>('/projects');
}

export async function getProjectById(id: string): Promise<Project | null> {
  if (USE_MOCK_DATA) {
    await simulateNetworkDelay();
    const proj = mockProjects.find((p) => p.id === id);
    return proj ? { ...proj } : null;
  }
  return apiClient<Project>(`/projects/${id}`);
}

export async function createProject(projectData: Partial<Project>): Promise<Project> {
  if (USE_MOCK_DATA) {
    await simulateNetworkDelay(350);
    const newProject: Project = {
      id: `proj-${Date.now().toString(36)}`,
      name: projectData.name || 'new-service',
      repository: projectData.repository || 'org/repo',
      defaultBranch: projectData.defaultBranch || 'main',
      environments: projectData.environments || ['production', 'staging'],
      awsAccount: projectData.awsAccount || '000000000000 (us-east-1)',
      region: projectData.region || 'us-east-1',
      status: 'active',
      lastAnalysisAt: new Date().toISOString(),
    };
    mockProjects.unshift(newProject);
    return newProject;
  }
  return apiClient<Project>('/projects', {
    method: 'POST',
    body: JSON.stringify(projectData),
  });
}

export async function getEnvironments(): Promise<Environment[]> {
  if (USE_MOCK_DATA) {
    await simulateNetworkDelay(120);
    return [...mockEnvironments];
  }
  return apiClient<Environment[]>('/environments');
}
