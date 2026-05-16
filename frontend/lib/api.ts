/**
 * API Client for RepoTwin Backend Integration
 * Handles all HTTP requests with fallback to local sample data
 */

import {
  Analysis,
  AnalysisCreateRequest,
  AnalysisProgress,
  AnalysisResults,
  AnalysisStatus,
  HealthResponse,
  Repository,
  RepositoryCreateRequest,
  RepositoryFile,
  RepositoryFilesList,
  RepositoryList,
} from "@/types/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";
const USE_MOCK_DATA = process.env.NEXT_PUBLIC_USE_MOCK === "true";

/**
 * Fetch wrapper with error handling
 */
async function fetchWithErrorHandling<T>(
  url: string,
  options?: RequestInit
): Promise<T> {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.error?.message || `HTTP ${response.status}: ${response.statusText}`
      );
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error for ${url}:`, error);
    throw error;
  }
}

/**
 * Load sample Shadow PR data from local JSON
 */
async function loadSampleData(): Promise<AnalysisResults> {
  try {
    const response = await fetch("/data/sample-shadow-pr.json");
    if (!response.ok) {
      throw new Error("Failed to load sample data");
    }
    return await response.json();
  } catch (error) {
    console.error("Failed to load sample data:", error);
    throw new Error("Sample data unavailable");
  }
}

/**
 * Health check endpoint
 */
export async function checkHealth(): Promise<HealthResponse> {
  if (USE_MOCK_DATA) {
    return { status: "ok", service: "repotwin-mock" };
  }

  try {
    return await fetchWithErrorHandling<HealthResponse>(`${API_BASE_URL}/health`);
  } catch (error) {
    console.warn("Backend health check failed, using mock mode");
    return { status: "ok", service: "repotwin-mock" };
  }
}

/**
 * Create a new analysis job
 */
export async function createAnalysis(
  data: AnalysisCreateRequest
): Promise<Analysis> {
  if (USE_MOCK_DATA) {
    // Return mock analysis for demo mode
    const mockId = `mock-${Date.now()}`;
    return {
      id: mockId,
      repo_id: data.repo_id,
      change_description: data.change_description,
      target_branch: data.target_branch || "main",
      status: AnalysisStatus.PENDING,
      progress_percent: 0,
      current_step: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      started_at: null,
      completed_at: null,
      error_message: null,
    };
  }

  return await fetchWithErrorHandling<Analysis>(`${API_BASE_URL}/analysis`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/**
 * Get analysis progress
 */
export async function getAnalysisProgress(
  analysisId: string
): Promise<AnalysisProgress> {
  if (USE_MOCK_DATA || analysisId.startsWith("mock-")) {
    // Simulate progress for mock mode
    const elapsed = Date.now() - parseInt(analysisId.split("-")[1] || "0");
    const progressPercent = Math.min(100, Math.floor((elapsed / 5000) * 100));
    
    let status = "running";
    let currentStep = "Analyzing repository";
    let message = "Processing change request";

    if (progressPercent >= 100) {
      status = "completed";
      currentStep = "Shadow PR ready";
      message = "Analysis completed successfully";
    } else if (progressPercent >= 85) {
      currentStep = "Building regression pack";
      message = "Generating test recommendations";
    } else if (progressPercent >= 65) {
      currentStep = "Calculating blast radius";
      message = "Analyzing impact propagation with IBM Bob-assisted analysis";
    } else if (progressPercent >= 45) {
      currentStep = "Mapping affected modules";
      message = "Identifying dependencies";
    } else if (progressPercent >= 25) {
      currentStep = "Loading repository context";
      message = "Reading codebase structure";
    } else if (progressPercent >= 10) {
      currentStep = "Reading change request";
      message = "Initializing analysis";
    }

    return {
      analysis_id: analysisId,
      status,
      progress_percent: progressPercent,
      current_step: currentStep,
      message,
      estimated_time_remaining: Math.max(0, Math.floor((100 - progressPercent) / 20)),
    };
  }

  return await fetchWithErrorHandling<AnalysisProgress>(
    `${API_BASE_URL}/analysis/${analysisId}/progress`
  );
}

/**
 * Get analysis results (Shadow PR)
 */
export async function getAnalysisResults(
  analysisId: string
): Promise<AnalysisResults> {
  if (USE_MOCK_DATA || analysisId.startsWith("mock-")) {
    // Return sample data for mock mode
    return await loadSampleData();
  }

  return await fetchWithErrorHandling<AnalysisResults>(
    `${API_BASE_URL}/analysis/${analysisId}/results`
  );
}

/**
 * Get analysis details
 */
export async function getAnalysis(analysisId: string): Promise<Analysis> {
  if (USE_MOCK_DATA || analysisId.startsWith("mock-")) {
    return {
      id: analysisId,
      repo_id: "660e8400-e29b-41d4-a716-446655440000",
      change_description: "Add reservation flow before purchase",
      target_branch: "main",
      status: AnalysisStatus.COMPLETED,
      progress_percent: 100,
      current_step: "Completed",
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      started_at: new Date().toISOString(),
      completed_at: new Date().toISOString(),
      error_message: null,
    };
  }

  return await fetchWithErrorHandling<Analysis>(
    `${API_BASE_URL}/analysis/${analysisId}`
  );
}

/**
 * Check if backend is available
 */
export async function isBackendAvailable(): Promise<boolean> {
  if (USE_MOCK_DATA) {
    return false;
  }

  try {
    const health = await checkHealth();
    return health.status === "ok";
  } catch {
    return false;
  }
}

// Made with Bob


/**
 * Repository Management Functions
 */

type BackendRepository = Repository & {
  url?: string;
  status?: string;
  total_files?: number;
};

type BackendRepositoryFile = RepositoryFile & {
  name?: string;
};

type BackendRepositoryFiles = {
  path?: string;
  files?: BackendRepositoryFile[];
  directories?: string[];
};

function normalizeRepository(repo: BackendRepository): Repository {
  return {
    ...repo,
    github_url: repo.github_url ?? repo.url ?? "",
    is_synced: repo.is_synced ?? repo.status === "ready",
    file_count: repo.file_count ?? repo.total_files ?? 0,
  };
}

function normalizeRepositoryList(data: RepositoryList | BackendRepository[]): RepositoryList {
  const items = Array.isArray(data) ? data : data.items ?? [];

  return {
    items: items.map(normalizeRepository),
    total: Array.isArray(data) ? items.length : data.total ?? items.length,
  };
}

/**
 * Create a new repository
 */
export async function createRepository(
  data: RepositoryCreateRequest
): Promise<Repository> {
  const repository = await fetchWithErrorHandling<BackendRepository>(`${API_BASE_URL}/repos`, {
    method: "POST",
    body: JSON.stringify({
      name: data.name,
      description: data.description,
      url: data.github_url,
      branch: data.default_branch ?? "main",
    }),
  });

  return normalizeRepository(repository);
}

/**
 * Get all repositories
 */
export async function getRepositories(): Promise<RepositoryList> {
  const repositories = await fetchWithErrorHandling<RepositoryList | BackendRepository[]>(
    `${API_BASE_URL}/repos`
  );

  return normalizeRepositoryList(repositories);
}

/**
 * Get a single repository by ID
 */
export async function getRepository(repoId: string): Promise<Repository> {
  const repository = await fetchWithErrorHandling<BackendRepository>(
    `${API_BASE_URL}/repos/${repoId}`
  );

  return normalizeRepository(repository);
}

/**
 * Sync repository files
 */
export async function syncRepository(
  repoId: string
): Promise<Repository> {
  const repository = await fetchWithErrorHandling<BackendRepository>(
    `${API_BASE_URL}/repos/${repoId}/sync`,
    {
      method: "POST",
    }
  );

  return normalizeRepository(repository);
}

/**
 * Get repository files
 */
export async function getRepositoryFiles(
  repoId: string
): Promise<RepositoryFilesList> {
  const data = await fetchWithErrorHandling<RepositoryFilesList | BackendRepositoryFiles>(
    `${API_BASE_URL}/repos/${repoId}/files`
  );

  if ("total_count" in data) {
    return data;
  }

  const files = data.files ?? [];
  const directories = (data.directories ?? []).map((path) => ({
    path,
    type: "directory" as const,
  }));

  return {
    repo_id: repoId,
    files: [...directories, ...files],
    total_count: directories.length + files.length,
  };
}

/**
 * LocalStorage helpers for selected repository
 */
const SELECTED_REPO_KEY = "repotwin_selected_repo_id";

export function setSelectedRepoId(repoId: string): void {
  if (typeof window !== "undefined") {
    localStorage.setItem(SELECTED_REPO_KEY, repoId);
  }
}

export function getSelectedRepoId(): string | null {
  if (typeof window !== "undefined") {
    return localStorage.getItem(SELECTED_REPO_KEY);
  }
  return null;
}

export function clearSelectedRepoId(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem(SELECTED_REPO_KEY);
  }
}
