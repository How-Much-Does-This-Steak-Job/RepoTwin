/**
 * API Types for RepoTwin Frontend-Backend Integration
 * Based on backend/app/schemas/analysis.py
 */

export enum AnalysisStatus {
  PENDING = "pending",
  RUNNING = "running",
  COMPLETED = "completed",
  FAILED = "failed",
  CANCELLED = "cancelled",
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

// Request Types
export interface AnalysisCreateRequest {
  repo_id: string;
  change_description: string;
  target_branch?: string;
  selected_files?: string[];
  context_files?: string[];
}

// Response Types
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

export interface AnalysisSummary {
  title: string;
  overview: string;
  key_points: string[];
}

export interface AnalysisResults {
  summary: AnalysisSummary;
  affected_files: AffectedFile[];
  impact_radius: ImpactRadius;
  risk_assessment: RiskAssessment;
  regression_analysis: RegressionAnalysis;
  implementation_plan: ImplementationPlan;
  test_recommendations: TestRecommendations;
  provider: "watsonx" | "heuristic" | "sample";
  enhanced_by_llm: boolean;
}

export interface AnalysisList {
  items: Analysis[];
  total: number;
  skip: number;
  limit: number;
}

// API Error Types
export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: string;
  };
}

// Health Check Types
export interface HealthResponse {
  status: string;
  service: string;
}

// Made with Bob
