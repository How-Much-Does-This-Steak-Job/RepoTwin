"""Analysis Pydantic schemas."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AnalysisStatus(str, Enum):
    """Analysis status enum."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RiskLevel(str, Enum):
    """Risk level enum."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ImpactLevel(str, Enum):
    """Impact level enum."""
    DIRECT = "direct"
    INDIRECT = "indirect"
    POTENTIAL = "potential"


class AnalysisCreate(BaseModel):
    """Analysis creation schema."""
    repo_id: UUID
    change_description: str = Field(..., min_length=10, max_length=5000)
    target_branch: str = Field(default="main", max_length=100)
    selected_files: Optional[List[str]] = None
    context_files: Optional[List[str]] = None


class Analysis(BaseModel):
    """Analysis response schema."""
    id: UUID
    repo_id: UUID
    change_description: str
    target_branch: str
    status: AnalysisStatus
    progress_percent: int = Field(ge=0, le=100)
    current_step: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class AnalysisProgress(BaseModel):
    """Analysis progress schema."""
    analysis_id: UUID
    status: str
    progress_percent: int
    current_step: str
    message: str
    estimated_time_remaining: Optional[int] = None


class AffectedFile(BaseModel):
    """Affected file schema."""
    path: str
    impact_level: ImpactLevel
    change_type: str
    reasoning: str
    lines_added: int = 0
    lines_removed: int = 0
    complexity_change: str = "neutral"
    risk_factors: List[str] = []


class ImpactRadiusMetrics(BaseModel):
    """Impact radius metrics schema."""
    files_affected: int = 0
    files_direct: int = 0
    files_indirect: int = 0
    functions_affected: int = 0
    classes_affected: int = 0
    tests_affected: int = 0
    percentage_of_codebase: float = 0.0


class ImpactRadius(BaseModel):
    """Impact radius schema."""
    category: str
    metrics: ImpactRadiusMetrics


class RiskFactor(BaseModel):
    """Risk factor schema."""
    name: str
    level: RiskLevel
    likelihood: str
    impact: str
    description: str
    mitigation: str


class RiskAssessment(BaseModel):
    """Risk assessment schema."""
    overall_level: RiskLevel
    score: int = Field(ge=0, le=100)
    factors: List[RiskFactor] = []


class BreakingChange(BaseModel):
    """Breaking change schema."""
    type: str
    file: str
    line: Optional[int] = None
    description: str
    migration: str
    severity: RiskLevel


class BehaviorChange(BaseModel):
    """Behavior change schema."""
    type: str
    file: str
    description: str
    impact: str


class RegressionAnalysis(BaseModel):
    """Regression analysis schema."""
    breaking_changes: List[BreakingChange] = []
    behavior_changes: List[BehaviorChange] = []


class ImplementationPhase(BaseModel):
    """Implementation phase schema."""
    phase: int
    name: str
    description: str
    files: List[str]
    estimated_effort: str
    checkpoints: List[str]


class ImplementationPlan(BaseModel):
    """Implementation plan schema."""
    phases: List[ImplementationPhase]
    total_estimated_effort: str
    rollback_strategy: str
    prerequisites: List[str]


class TestUpdate(BaseModel):
    """Test update schema."""
    path: str
    changes: str
    priority: str


class NewTest(BaseModel):
    """New test schema."""
    type: str
    description: str
    priority: str


class CoverageGap(BaseModel):
    """Coverage gap schema."""
    area: str
    current_coverage: int
    target_coverage: int


class TestRecommendations(BaseModel):
    """Test recommendations schema."""
    existing_tests_to_update: List[TestUpdate] = []
    new_tests_needed: List[NewTest] = []
    coverage_gaps: List[CoverageGap] = []


class AnalysisSummary(BaseModel):
    """Analysis summary schema."""
    title: str
    overview: str
    key_points: List[str]


class AnalysisResults(BaseModel):
    """Complete analysis results schema."""
    summary: AnalysisSummary
    affected_files: List[AffectedFile]
    impact_radius: ImpactRadius
    risk_assessment: RiskAssessment
    regression_analysis: RegressionAnalysis
    implementation_plan: ImplementationPlan
    test_recommendations: TestRecommendations
    provider: str = "heuristic"  # "watsonx" | "heuristic" | "sample"
    enhanced_by_llm: bool = False


class AnalysisList(BaseModel):
    """Analysis list response."""
    items: List[Analysis]
    total: int
    skip: int
    limit: int
