/**
 * Unified Shadow PR Type Definitions
 * 
 * This is the canonical Shadow PR schema for RepoTwin.
 * Both frontend and backend should align with these types.
 * 
 * Built with IBM Bob IDE
 */

// ============================================================================
// Core Shadow PR Types
// ============================================================================

export interface ShadowPR {
  id: string;
  repository: RepositoryInfo;
  changeRequest: ChangeRequest;
  analysis: AnalysisMetadata;
  summary: ShadowPRSummary;
  affectedFiles: AffectedFile[];
  blastRadiusMap: BlastRadiusMap;
  riskScore: RiskScore;
  regressionPack: RegressionPack;
  implementationContract: ImplementationContract;
  prBrief: PRBrief;
}

// ============================================================================
// Repository Information
// ============================================================================

export interface RepositoryInfo {
  name: string;
  url?: string;
  branch?: string;
  commit?: string;
  language: string;
  framework?: string;
  totalFiles?: number;
  totalLines?: number;
}

// ============================================================================
// Change Request
// ============================================================================

export interface ChangeRequest {
  text: string;
  submittedAt: string;
  submittedBy?: string;
  category?: ChangeCategory;
}

export enum ChangeCategory {
  FEATURE = "feature",
  BUGFIX = "bugfix",
  REFACTOR = "refactor",
  PERFORMANCE = "performance",
  SECURITY = "security",
  DOCUMENTATION = "documentation",
}

// ============================================================================
// Analysis Metadata
// ============================================================================

export interface AnalysisMetadata {
  analysisId: string;
  startedAt: string;
  completedAt: string;
  duration: number; // milliseconds
  provider: AnalysisProvider;
  enhancedByLLM: boolean;
  version: string;
}

export enum AnalysisProvider {
  WATSONX = "watsonx",
  HEURISTIC = "heuristic",
  SAMPLE = "sample",
}

// ============================================================================
// Shadow PR Summary
// ============================================================================

export interface ShadowPRSummary {
  title: string;
  overview: string;
  keyPoints: string[];
}

// ============================================================================
// Affected Files
// ============================================================================

export interface AffectedFile {
  path: string;
  impactLevel: ImpactLevel;
  changeType: ChangeType;
  reasoning: string;
  linesAdded: number;
  linesRemoved: number;
  complexityChange: ComplexityChange;
  riskFactors: string[];
}

export enum ImpactLevel {
  DIRECT = "direct",
  INDIRECT = "indirect",
  POTENTIAL = "potential",
}

export enum ChangeType {
  ADDITION = "addition",
  MODIFICATION = "modification",
  DELETION = "deletion",
  RENAME = "rename",
}

export enum ComplexityChange {
  NEW = "new",
  INCREASED = "increased",
  DECREASED = "decreased",
  NEUTRAL = "neutral",
}

// ============================================================================
// Blast Radius Map
// ============================================================================

export interface BlastRadiusMap {
  category: BlastRadiusCategory;
  metrics: BlastRadiusMetrics;
  visualization?: BlastRadiusVisualization;
}

export enum BlastRadiusCategory {
  LOW = "low",
  MEDIUM = "medium",
  MEDIUM_HIGH = "medium-high",
  HIGH = "high",
  CRITICAL = "critical",
}

export interface BlastRadiusMetrics {
  filesAffected: number;
  filesDirect: number;
  filesIndirect: number;
  functionsAffected: number;
  classesAffected: number;
  testsAffected: number;
  percentageOfCodebase: number;
}

export interface BlastRadiusVisualization {
  nodes: BlastRadiusNode[];
  edges: BlastRadiusEdge[];
}

export interface BlastRadiusNode {
  id: string;
  label: string;
  type: "file" | "module" | "package";
  impactLevel: ImpactLevel;
}

export interface BlastRadiusEdge {
  source: string;
  target: string;
  type: "depends_on" | "imports" | "calls";
}

// ============================================================================
// Risk Score
// ============================================================================

export interface RiskScore {
  overallLevel: RiskLevel;
  score: number; // 0-100
  factors: RiskFactor[];
}

export enum RiskLevel {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  CRITICAL = "critical",
}

export interface RiskFactor {
  name: string;
  level: RiskLevel;
  likelihood: Likelihood;
  impact: Impact;
  description: string;
  mitigation: string;
}

export enum Likelihood {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  CERTAIN = "certain",
}

export enum Impact {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  CRITICAL = "critical",
}

// ============================================================================
// Regression Pack
// ============================================================================

export interface RegressionPack {
  breakingChanges: BreakingChange[];
  behaviorChanges: BehaviorChange[];
}

export interface BreakingChange {
  type: BreakingChangeType;
  file: string;
  line?: number;
  description: string;
  migration: string;
  severity: RiskLevel;
}

export enum BreakingChangeType {
  API_SIGNATURE = "api_signature",
  DATABASE_SCHEMA = "database_schema",
  RESPONSE_FORMAT = "response_format",
  CONFIGURATION = "configuration",
  DEPENDENCY = "dependency",
}

export interface BehaviorChange {
  type: BehaviorChangeType;
  file: string;
  description: string;
  impact: string;
}

export enum BehaviorChangeType {
  BUSINESS_LOGIC = "business_logic",
  TIMING = "timing",
  INVENTORY_MANAGEMENT = "inventory_management",
  NOTIFICATION_TRIGGERS = "notification_triggers",
  CACHING = "caching",
  VALIDATION = "validation",
}

// ============================================================================
// Implementation Contract
// ============================================================================

export interface ImplementationContract {
  phases: ImplementationPhase[];
  totalEstimatedEffort: string;
  rollbackStrategy: string;
  prerequisites: string[];
}

export interface ImplementationPhase {
  phase: number;
  name: string;
  description: string;
  files: string[];
  estimatedEffort: string;
  checkpoints: string[];
}

// ============================================================================
// PR Brief
// ============================================================================

export interface PRBrief {
  title: string;
  description: string;
  summary: string;
  impactSummary: string;
  riskSummary: string;
  testingSummary: string;
  reviewGuidance: string;
  markdown: string; // Full markdown PR description
}

// ============================================================================
// Test Recommendations
// ============================================================================

export interface TestRecommendations {
  existingTestsToUpdate: ExistingTestUpdate[];
  newTestsNeeded: NewTest[];
  coverageGaps: CoverageGap[];
}

export interface ExistingTestUpdate {
  path: string;
  changes: string;
  priority: Priority;
}

export interface NewTest {
  type: TestType;
  description: string;
  priority: Priority;
}

export enum TestType {
  UNIT = "unit",
  INTEGRATION = "integration",
  E2E = "e2e",
  LOAD = "load",
  SECURITY = "security",
}

export enum Priority {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  CRITICAL = "critical",
}

export interface CoverageGap {
  area: string;
  currentCoverage: number;
  targetCoverage: number;
}

// ============================================================================
// API Response Types (Backend Compatibility)
// ============================================================================

/**
 * Current backend response format
 * This should eventually be replaced with ShadowPR
 */
export interface AnalysisResults {
  summary: {
    title: string;
    overview: string;
    key_points: string[];
  };
  affected_files: Array<{
    path: string;
    impact_level: string;
    change_type: string;
    reasoning: string;
    lines_added: number;
    lines_removed: number;
    complexity_change: string;
    risk_factors: string[];
  }>;
  impact_radius: {
    category: string;
    metrics: {
      files_affected: number;
      files_direct: number;
      files_indirect: number;
      functions_affected: number;
      classes_affected: number;
      tests_affected: number;
      percentage_of_codebase: number;
    };
  };
  risk_assessment: {
    overall_level: string;
    score: number;
    factors: Array<{
      name: string;
      level: string;
      likelihood: string;
      impact: string;
      description: string;
      mitigation: string;
    }>;
  };
  regression_analysis: {
    breaking_changes: Array<{
      type: string;
      file: string;
      line?: number;
      description: string;
      migration: string;
      severity: string;
    }>;
    behavior_changes: Array<{
      type: string;
      file: string;
      description: string;
      impact: string;
    }>;
  };
  implementation_plan: {
    phases: Array<{
      phase: number;
      name: string;
      description: string;
      files: string[];
      estimated_effort: string;
      checkpoints: string[];
    }>;
    total_estimated_effort: string;
    rollback_strategy: string;
    prerequisites: string[];
  };
  test_recommendations: {
    existing_tests_to_update: Array<{
      path: string;
      changes: string;
      priority: string;
    }>;
    new_tests_needed: Array<{
      type: string;
      description: string;
      priority: string;
    }>;
    coverage_gaps: Array<{
      area: string;
      current_coverage: number;
      target_coverage: number;
    }>;
  };
  provider: string;
  enhanced_by_llm: boolean;
}

// ============================================================================
// Utility Types
// ============================================================================

export type ShadowPRStatus = "pending" | "analyzing" | "completed" | "failed";

export interface ShadowPRProgress {
  status: ShadowPRStatus;
  progress: number; // 0-100
  message: string;
  currentPhase?: string;
}

// ============================================================================
// Type Guards
// ============================================================================

export function isShadowPR(obj: any): obj is ShadowPR {
  return (
    obj &&
    typeof obj === "object" &&
    "id" in obj &&
    "repository" in obj &&
    "changeRequest" in obj &&
    "summary" in obj &&
    "affectedFiles" in obj
  );
}

export function isAnalysisResults(obj: any): obj is AnalysisResults {
  return (
    obj &&
    typeof obj === "object" &&
    "summary" in obj &&
    "affected_files" in obj &&
    "impact_radius" in obj
  );
}

// ============================================================================
// Converters (Backend Format → Shadow PR Format)
// ============================================================================

export function convertAnalysisResultsToShadowPR(
  results: AnalysisResults,
  analysisId: string,
  repositoryName: string,
  changeRequestText: string
): ShadowPR {
  return {
    id: `shadow-pr-${analysisId}`,
    repository: {
      name: repositoryName,
      language: "unknown",
    },
    changeRequest: {
      text: changeRequestText,
      submittedAt: new Date().toISOString(),
    },
    analysis: {
      analysisId,
      startedAt: new Date().toISOString(),
      completedAt: new Date().toISOString(),
      duration: 0,
      provider: results.provider as AnalysisProvider,
      enhancedByLLM: results.enhanced_by_llm,
      version: "1.0.0",
    },
    summary: {
      title: results.summary.title,
      overview: results.summary.overview,
      keyPoints: results.summary.key_points,
    },
    affectedFiles: results.affected_files.map((file) => ({
      path: file.path,
      impactLevel: file.impact_level as ImpactLevel,
      changeType: file.change_type as ChangeType,
      reasoning: file.reasoning,
      linesAdded: file.lines_added,
      linesRemoved: file.lines_removed,
      complexityChange: file.complexity_change as ComplexityChange,
      riskFactors: file.risk_factors,
    })),
    blastRadiusMap: {
      category: results.impact_radius.category as BlastRadiusCategory,
      metrics: {
        filesAffected: results.impact_radius.metrics.files_affected,
        filesDirect: results.impact_radius.metrics.files_direct,
        filesIndirect: results.impact_radius.metrics.files_indirect,
        functionsAffected: results.impact_radius.metrics.functions_affected,
        classesAffected: results.impact_radius.metrics.classes_affected,
        testsAffected: results.impact_radius.metrics.tests_affected,
        percentageOfCodebase: results.impact_radius.metrics.percentage_of_codebase,
      },
    },
    riskScore: {
      overallLevel: results.risk_assessment.overall_level as RiskLevel,
      score: results.risk_assessment.score,
      factors: results.risk_assessment.factors.map((factor) => ({
        name: factor.name,
        level: factor.level as RiskLevel,
        likelihood: factor.likelihood as Likelihood,
        impact: factor.impact as Impact,
        description: factor.description,
        mitigation: factor.mitigation,
      })),
    },
    regressionPack: {
      breakingChanges: results.regression_analysis.breaking_changes.map((change) => ({
        type: change.type as BreakingChangeType,
        file: change.file,
        line: change.line,
        description: change.description,
        migration: change.migration,
        severity: change.severity as RiskLevel,
      })),
      behaviorChanges: results.regression_analysis.behavior_changes.map((change) => ({
        type: change.type as BehaviorChangeType,
        file: change.file,
        description: change.description,
        impact: change.impact,
      })),
    },
    implementationContract: {
      phases: results.implementation_plan.phases.map((phase) => ({
        phase: phase.phase,
        name: phase.name,
        description: phase.description,
        files: phase.files,
        estimatedEffort: phase.estimated_effort,
        checkpoints: phase.checkpoints,
      })),
      totalEstimatedEffort: results.implementation_plan.total_estimated_effort,
      rollbackStrategy: results.implementation_plan.rollback_strategy,
      prerequisites: results.implementation_plan.prerequisites,
    },
    prBrief: {
      title: results.summary.title,
      description: results.summary.overview,
      summary: results.summary.overview,
      impactSummary: `${results.impact_radius.metrics.files_affected} files affected`,
      riskSummary: `Risk Level: ${results.risk_assessment.overall_level.toUpperCase()}`,
      testingSummary: `${results.test_recommendations.new_tests_needed.length} new tests needed`,
      reviewGuidance: "Review implementation plan and risk factors carefully",
      markdown: generatePRMarkdown(results),
    },
  };
}

function generatePRMarkdown(results: AnalysisResults): string {
  return `# ${results.summary.title}

## Overview
${results.summary.overview}

## Key Points
${results.summary.key_points.map((point) => `- ${point}`).join("\n")}

## Impact Metrics
- Files Affected: ${results.impact_radius.metrics.files_affected}
- Risk Score: ${results.risk_assessment.score}/100
- Risk Level: ${results.risk_assessment.overall_level.toUpperCase()}
- Implementation Effort: ${results.implementation_plan.total_estimated_effort}

## Risk Factors
${results.risk_assessment.factors.map((factor) => `- **${factor.name}** (${factor.level}): ${factor.description}`).join("\n")}

---
Generated by RepoTwin - Built with IBM Bob IDE
`;
}

// ============================================================================
// Export All
// ============================================================================

export default ShadowPR;

// Made with Bob
