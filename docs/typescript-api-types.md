# TypeScript API Type Definitions

## Overview

This document defines the TypeScript types that should be created in `types/api.ts` and `types/shadow-pr.ts` to ensure type safety between the RepoTwin frontend and backend.

These types mirror the Pydantic schemas in `backend/app/schemas/` and must stay synchronized.

## File: types/api.ts

```typescript
/**
 * API Type Definitions for RepoTwin
 * 
 * These types define the contract between frontend and backend.
 * They must stay in sync with backend/app/schemas/
 */

// ============================================================================
// Enums
// ============================================================================

export enum AnalysisStatus {
  PENDING = "pending",
  RUNNING = "running",
  COMPLETED = "completed",
  FAILED = "failed",
  CANCELLED = "cancelled",
}

export enum AnalysisMode {
  DEMO = "demo",
  LIVE = "live",
}

export enum RiskLevel {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  CRITICAL = "critical",
}

export enum ImpactLevel {
  DIRECT = "direct",
  INDIRECT = "indirect",
  POTENTIAL = "potential",
}

// ============================================================================
// Request Types
// ============================================================================

export interface AnalysisCreateRequest {
  repo_id: string;
  change_description: string;
  target_branch?: string;
  mode?: AnalysisMode;
  selected_files?: string[];
  context_files?: string[];
}

export interface AnalysisCancelRequest {
  reason?: string;
}

// ============================================================================
// Response Types
// ============================================================================

export interface Analysis {
  id: string;
  repo_id: string;
  change_description: string;
  target_branch: string;
  status: AnalysisStatus;
  progress_percent: number;
  current_step: string | null;
  created_at: string;
  updated_at: string;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
}

export interface AnalysisProgress {
  analysis_id: string;
  status: string;
  progress_percent: number;
  current_step: string;
  message: string;
  estimated_time_remaining?: number;
}

export interface AnalysisList {
  items: Analysis[];
  total: number;
  skip: number;
  limit: number;
}

// ============================================================================
// Error Types
// ============================================================================

export interface ApiError {
  code: string;
  message: string;
  details?: string;
}

export interface ApiErrorResponse {
  error: ApiError;
}

// ============================================================================
// Health Check Types
// ============================================================================

export interface HealthResponse {
  status: string;
  service: string;
}

export interface ReadinessResponse {
  ready: boolean;
}

export interface LivenessResponse {
  alive: boolean;
}

// ============================================================================
// WebSocket Message Types
// ============================================================================

export interface WebSocketProgressMessage {
  type: "progress";
  data: {
    analysis_id: string;
    status: string;
    progress_percent: number;
    message: string;
  };
}

export interface WebSocketCompletedMessage {
  type: "completed";
  data: {
    analysis_id: string;
    status: string;
  };
}

export interface WebSocketErrorMessage {
  type: "error";
  data: {
    analysis_id: string;
    error: string;
  };
}

export type WebSocketMessage =
  | WebSocketProgressMessage
  | WebSocketCompletedMessage
  | WebSocketErrorMessage;
```

## File: types/shadow-pr.ts

```typescript
/**
 * Shadow PR Type Definitions
 * 
 * These types define the complete Shadow PR analysis result structure.
 * They must stay in sync with backend/app/schemas/analysis.py
 */

import { RiskLevel, ImpactLevel } from "./api";

// ============================================================================
// Summary Types
// ============================================================================

export interface AnalysisSummary {
  title: string;
  overview: string;
  key_points: string[];
}

// ============================================================================
// Affected Files Types
// ============================================================================

export interface AffectedFile {
  path: string;
  impact_level: ImpactLevel;
  change_type: string;
  reasoning: string;
  lines_added: number;
  lines_removed: number;
  complexity_change: string;
  risk_factors: string[];
}

// ============================================================================
// Impact Radius Types
// ============================================================================

export interface ImpactRadiusMetrics {
  files_affected: number;
  files_direct: number;
  files_indirect: number;
  functions_affected: number;
  classes_affected: number;
  tests_affected: number;
  percentage_of_codebase: number;
}

export interface ImpactRadius {
  category: string;
  metrics: ImpactRadiusMetrics;
}

// ============================================================================
// Risk Assessment Types
// ============================================================================

export interface RiskFactor {
  name: string;
  level: RiskLevel;
  likelihood: string;
  impact: string;
  description: string;
  mitigation: string;
}

export interface RiskAssessment {
  overall_level: RiskLevel;
  score: number;
  factors: RiskFactor[];
}

// ============================================================================
// Regression Analysis Types
// ============================================================================

export interface BreakingChange {
  type: string;
  file: string;
  line?: number;
  description: string;
  migration: string;
  severity: RiskLevel;
}

export interface BehaviorChange {
  type: string;
  file: string;
  description: string;
  impact: string;
}

export interface RegressionAnalysis {
  breaking_changes: BreakingChange[];
  behavior_changes: BehaviorChange[];
}

// ============================================================================
// Implementation Plan Types
// ============================================================================

export interface ImplementationPhase {
  phase: number;
  name: string;
  description: string;
  files: string[];
  estimated_effort: string;
  checkpoints: string[];
}

export interface ImplementationPlan {
  phases: ImplementationPhase[];
  total_estimated_effort: string;
  rollback_strategy: string;
  prerequisites: string[];
}

// ============================================================================
// Test Recommendations Types
// ============================================================================

export interface TestUpdate {
  path: string;
  changes: string;
  priority: string;
}

export interface NewTest {
  type: string;
  description: string;
  priority: string;
}

export interface CoverageGap {
  area: string;
  current_coverage: number;
  target_coverage: number;
}

export interface TestRecommendations {
  existing_tests_to_update: TestUpdate[];
  new_tests_needed: NewTest[];
  coverage_gaps: CoverageGap[];
}

// ============================================================================
// Complete Analysis Results (Shadow PR)
// ============================================================================

export interface AnalysisResults {
  summary: AnalysisSummary;
  affected_files: AffectedFile[];
  impact_radius: ImpactRadius;
  risk_assessment: RiskAssessment;
  regression_analysis: RegressionAnalysis;
  implementation_plan: ImplementationPlan;
  test_recommendations: TestRecommendations;
}

// ============================================================================
// Repository Types
// ============================================================================

export interface Repository {
  id: string;
  name: string;
  url: string;
  default_branch: string;
  created_at: string;
}

export interface RepositoryList {
  items: Repository[];
  total: number;
}
```

## File: lib/api.ts (API Client)

```typescript
/**
 * API Client for RepoTwin
 * 
 * Provides typed methods for interacting with the backend API.
 */

import axios, { AxiosInstance, AxiosError } from "axios";
import {
  Analysis,
  AnalysisCreateRequest,
  AnalysisProgress,
  AnalysisResults,
  AnalysisList,
  ApiErrorResponse,
  HealthResponse,
} from "@/types/api";

export class RepoTwinApiClient {
  private client: AxiosInstance;

  constructor(baseURL: string = "http://localhost:8000/api") {
    this.client = axios.create({
      baseURL,
      headers: {
        "Content-Type": "application/json",
      },
      timeout: 30000, // 30 seconds
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<ApiErrorResponse>) => {
        if (error.response?.data?.error) {
          throw new ApiError(
            error.response.data.error.code,
            error.response.data.error.message,
            error.response.data.error.details
          );
        }
        throw error;
      }
    );
  }

  // ============================================================================
  // Health Endpoints
  // ============================================================================

  async health(): Promise<HealthResponse> {
    const response = await this.client.get<HealthResponse>("/health");
    return response.data;
  }

  // ============================================================================
  // Analysis Endpoints
  // ============================================================================

  async createAnalysis(data: AnalysisCreateRequest): Promise<Analysis> {
    const response = await this.client.post<Analysis>("/analysis", data);
    return response.data;
  }

  async listAnalyses(params?: {
    repo_id?: string;
    status?: string;
    skip?: number;
    limit?: number;
  }): Promise<AnalysisList> {
    const response = await this.client.get<AnalysisList>("/analysis", {
      params,
    });
    return response.data;
  }

  async getAnalysis(analysisId: string): Promise<Analysis> {
    const response = await this.client.get<Analysis>(
      `/analysis/${analysisId}`
    );
    return response.data;
  }

  async getAnalysisProgress(analysisId: string): Promise<AnalysisProgress> {
    const response = await this.client.get<AnalysisProgress>(
      `/analysis/${analysisId}/progress`
    );
    return response.data;
  }

  async getAnalysisResults(analysisId: string): Promise<AnalysisResults> {
    const response = await this.client.get<AnalysisResults>(
      `/analysis/${analysisId}/results`
    );
    return response.data;
  }

  async deleteAnalysis(analysisId: string): Promise<void> {
    await this.client.delete(`/analysis/${analysisId}`);
  }

  // ============================================================================
  // WebSocket Connection
  // ============================================================================

  connectWebSocket(
    analysisId: string,
    onMessage: (message: any) => void,
    onError?: (error: Event) => void,
    onClose?: (event: CloseEvent) => void
  ): WebSocket {
    const wsUrl = `ws://localhost:8000/api/analysis/${analysisId}/ws`;
    const ws = new WebSocket(wsUrl);

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      onMessage(message);
    };

    if (onError) {
      ws.onerror = onError;
    }

    if (onClose) {
      ws.onclose = onClose;
    }

    return ws;
  }
}

// ============================================================================
// Custom Error Class
// ============================================================================

export class ApiError extends Error {
  constructor(
    public code: string,
    message: string,
    public details?: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

// ============================================================================
// Default Export
// ============================================================================

export const apiClient = new RepoTwinApiClient();
```

## Usage Examples

### Creating an Analysis

```typescript
import { apiClient } from "@/lib/api";
import { AnalysisMode } from "@/types/api";

async function createDemoAnalysis() {
  try {
    const analysis = await apiClient.createAnalysis({
      repo_id: "660e8400-e29b-41d4-a716-446655440000",
      change_description: "Add reservation flow before purchase",
      mode: AnalysisMode.DEMO,
      target_branch: "main",
    });

    console.log("Analysis created:", analysis.id);
    return analysis;
  } catch (error) {
    if (error instanceof ApiError) {
      console.error(`API Error [${error.code}]: ${error.message}`);
    } else {
      console.error("Unexpected error:", error);
    }
  }
}
```

### Polling for Progress

```typescript
import { apiClient } from "@/lib/api";
import { AnalysisStatus } from "@/types/api";

async function pollAnalysisProgress(analysisId: string) {
  const pollInterval = 2000; // 2 seconds

  return new Promise((resolve, reject) => {
    const interval = setInterval(async () => {
      try {
        const progress = await apiClient.getAnalysisProgress(analysisId);

        console.log(
          `Progress: ${progress.progress_percent}% - ${progress.message}`
        );

        if (progress.status === "completed") {
          clearInterval(interval);
          const results = await apiClient.getAnalysisResults(analysisId);
          resolve(results);
        } else if (progress.status === "failed") {
          clearInterval(interval);
          reject(new Error("Analysis failed"));
        }
      } catch (error) {
        clearInterval(interval);
        reject(error);
      }
    }, pollInterval);
  });
}
```

### Using WebSocket for Real-time Updates

```typescript
import { apiClient } from "@/lib/api";
import { WebSocketMessage } from "@/types/api";

function subscribeToAnalysis(analysisId: string) {
  const ws = apiClient.connectWebSocket(
    analysisId,
    (message: WebSocketMessage) => {
      switch (message.type) {
        case "progress":
          console.log(
            `Progress: ${message.data.progress_percent}% - ${message.data.message}`
          );
          break;

        case "completed":
          console.log("Analysis completed!");
          ws.close();
          break;

        case "error":
          console.error("Analysis error:", message.data.error);
          ws.close();
          break;
      }
    },
    (error) => {
      console.error("WebSocket error:", error);
    },
    (event) => {
      console.log("WebSocket closed:", event.code);
    }
  );

  return ws;
}
```

### React Hook Example

```typescript
import { useState, useEffect } from "react";
import { apiClient } from "@/lib/api";
import { AnalysisProgress, AnalysisResults } from "@/types/api";

export function useAnalysis(analysisId: string | null) {
  const [progress, setProgress] = useState<AnalysisProgress | null>(null);
  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!analysisId) return;

    setLoading(true);

    const ws = apiClient.connectWebSocket(
      analysisId,
      (message) => {
        if (message.type === "progress") {
          setProgress(message.data);
        } else if (message.type === "completed") {
          apiClient
            .getAnalysisResults(analysisId)
            .then((data) => {
              setResults(data);
              setLoading(false);
            })
            .catch((err) => {
              setError(err);
              setLoading(false);
            });
        } else if (message.type === "error") {
          setError(new Error(message.data.error));
          setLoading(false);
        }
      },
      (err) => {
        setError(new Error("WebSocket connection failed"));
        setLoading(false);
      }
    );

    return () => {
      ws.close();
    };
  }, [analysisId]);

  return { progress, results, error, loading };
}
```

## Type Guards

```typescript
import { AnalysisStatus, RiskLevel } from "@/types/api";

export function isCompletedStatus(status: AnalysisStatus): boolean {
  return status === AnalysisStatus.COMPLETED;
}

export function isFailedStatus(status: AnalysisStatus): boolean {
  return status === AnalysisStatus.FAILED;
}

export function isHighRisk(level: RiskLevel): boolean {
  return level === RiskLevel.HIGH || level === RiskLevel.CRITICAL;
}

export function isAnalysisInProgress(status: AnalysisStatus): boolean {
  return (
    status === AnalysisStatus.PENDING || status === AnalysisStatus.RUNNING
  );
}
```

## Validation Helpers

```typescript
export function validateChangeDescription(description: string): boolean {
  return description.length >= 10 && description.length <= 5000;
}

export function validateUUID(uuid: string): boolean {
  const uuidRegex =
    /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidRegex.test(uuid);
}
```

## Implementation Checklist

When implementing these types in the frontend:

- [ ] Create `types/api.ts` with all API types
- [ ] Create `types/shadow-pr.ts` with Shadow PR types
- [ ] Create `lib/api.ts` with API client
- [ ] Add axios dependency: `pnpm add axios`
- [ ] Configure TypeScript paths in `tsconfig.json`
- [ ] Create React hooks for common operations
- [ ] Add error boundary for API errors
- [ ] Implement loading states
- [ ] Add retry logic for failed requests
- [ ] Implement WebSocket reconnection
- [ ] Add request/response logging (development only)
- [ ] Create mock data for Storybook/testing

## References

- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
- [Axios Documentation](https://axios-http.com/docs/intro)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [API Contract](./api-contract.md)
- [AGENTS.md](../AGENTS.md)