/**
 * InfraShift API Client
 * Configured for seamless transition between local Mock Data (hackathon/offline demo mode)
 * and production FastAPI / AWS API Gateway endpoints.
 */

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://api.infrashift.internal/v1';
export const USE_MOCK_DATA = import.meta.env.VITE_USE_MOCK_DATA !== 'false'; // Defaults to true for hackathon frontend

export interface ApiResponse<T> {
  data: T | null;
  error: string | null;
  status: number;
}

// Simulated network delay for realistic developer SaaS feel
export async function simulateNetworkDelay(ms = 220): Promise<void> {
  if (USE_MOCK_DATA) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

export async function apiClient<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  if (USE_MOCK_DATA) {
    throw new Error(`Mock mode active. Use mock service layer for endpoint: ${endpoint}`);
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`API Error [${response.status}]: ${errorBody || response.statusText}`);
  }

  return response.json();
}
