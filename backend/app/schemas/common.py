"""Pydantic schemas for request/response validation."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CommonBaseModel(BaseModel):
    """Base model with common configuration."""
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


# ============== Common Schemas ==============

class PaginationParams(BaseModel):
    """Pagination parameters."""
    limit: int = Field(default=20, ge=1, le=100)
    cursor: Optional[str] = None


class PaginationInfo(BaseModel):
    """Pagination metadata."""
    has_more: bool
    next_cursor: Optional[str] = None
    total_count: Optional[int] = None


class PaginatedResponse(BaseModel):
    """Base paginated response."""
    data: List[Any]
    pagination: PaginationInfo


class ErrorDetail(BaseModel):
    """Error detail item."""
    field: Optional[str] = None
    message: str


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: Dict[str, Any]


# ============== Repository Schemas ==============

class RepositoryProvider(str, Enum):
    """Git provider types."""
    GITHUB = "github"
    GITLAB = "gitlab"
    BITBUCKET = "bitbucket"


class RepositoryStatus(str, Enum):
    """Repository status."""
    PENDING = "pending"
    PROCESSING = "processing"
    ACTIVE = "active"
    ERROR = "error"
    SYNCING = "syncing"


class RepositoryStats(BaseModel):
    """Repository statistics."""
    files_count: int = 0
    lines_of_code: int = 0
    functions_count: int = 0
    classes_count: int = 0
    dependencies_count: int = 0
    dev_dependencies_count: int = 0


class RepositoryBase(CommonBaseModel):
    """Base repository schema."""
    name: str
    full_name: str
    provider: RepositoryProvider
    url: str
    default_branch: str = "main"
    description: Optional[str] = None
    private: bool = False
    language: Optional[str] = None
    languages: Dict[str, int] = Field(default_factory=dict)


class RepositoryCreate(CommonBaseModel):
    """Repository creation request."""
    url: str = Field(..., min_length=10, description="Repository URL")
    provider: RepositoryProvider
    credentials: Optional[Dict[str, Any]] = None


class RepositoryResponse(RepositoryBase):
    """Repository response."""
    id: str
    stats: RepositoryStats = Field(default_factory=RepositoryStats)
    status: RepositoryStatus
    ingestion_progress: int = 0
    last_synced_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class RepositoryListResponse(PaginatedResponse):
    """Repository list response."""
    data: List[RepositoryResponse]


class FileInfo(CommonBaseModel):
    """File information."""
    name: str
    path: str
    type: str  # file, directory
    size: Optional[int] = None
    language: Optional[str] = None
    children_count: Optional[int] = None


class FileTreeResponse(CommonBaseModel):
    """File tree response."""
    path: str
    files: List[FileInfo]


class FileContentResponse(CommonBaseModel):
    """File content response."""
    path: str
    name: str
    size: int
    language: Optional[str] = None
    content: str
    encoding: str = "utf-8"
    line_count: int
    last_modified: Optional[datetime] = None


# ============== Analysis Schemas ==============

class ChangeType(str, Enum):
    """Type of code change."""
    FEATURE = "feature"
    BUGFIX = "bugfix"
    REFACTOR = "refactor"
    PERFORMANCE = "performance"
    SECURITY = "security"


class AnalysisStatus(str, Enum):
    """Analysis status."""
    QUEUED = "queued"
    VALIDATING = "validating"
    PARSING = "parsing"
    BUILDING_CONTEXT = "building_context"
    ANALYZING_DEPENDENCIES = "analyzing_dependencies"
    AI_ANALYSIS = "ai_analysis"
    PROCESSING_RESULTS = "processing_results"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RiskLevel(str, Enum):
    """Risk assessment level."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ImpactLevel(str, Enum):
    """Impact level for files."""
    DIRECT = "direct"
    INDIRECT = "indirect"
    POTENTIAL = "potential"


class FileContext(CommonBaseModel):
    """File context selection."""
    path: str
    line_start: Optional[int] = None
    line_end: Optional[int] = None


class FunctionContext(CommonBaseModel):
    """Function context selection."""
    file_path: str
    name: str


class AnalysisContext(CommonBaseModel):
    """Analysis context selection."""
    files: List[FileContext] = Field(default_factory=list)
    functions: List[FunctionContext] = Field(default_factory=list)


class AnalysisOptions(CommonBaseModel):
    """Analysis options."""
    include_tests: bool = True
    include_implementation_plan: bool = True
    priority: str = "normal"


class AnalysisCreate(CommonBaseModel):
    """Analysis creation request."""
    repository_id: str
    description: str = Field(..., min_length=50, description="Change description (min 50 chars)")
    change_type: ChangeType
    context: AnalysisContext = Field(default_factory=AnalysisContext)
    options: AnalysisOptions = Field(default_factory=AnalysisOptions)
    
    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        if len(v.strip()) < 50:
            raise ValueError("Description must be at least 50 characters")
        return v.strip()


class AnalysisSummary(CommonBaseModel):
    """Analysis summary."""
    title: str
    overview: str
    key_points: List[str]


class AffectedFile(CommonBaseModel):
    """Affected file in analysis."""
    path: str
    impact_level: ImpactLevel
    change_type: str  # modification, addition, deletion
    reasoning: str
    lines_added: int = 0
    lines_removed: int = 0
    complexity_change: str = "neutral"  # increased, decreased, neutral
    risk_factors: List[str] = Field(default_factory=list)


class ImpactRadiusMetrics(BaseModel):
    """Impact radius metrics."""
    files_affected: int = 0
    files_direct: int = 0
    files_indirect: int = 0
    functions_affected: int = 0
    classes_affected: int = 0
    tests_affected: int = 0
    percentage_of_codebase: float = 0.0


class ImpactRadius(BaseModel):
    """Impact radius information."""
    category: str  # small, medium, large
    metrics: ImpactRadiusMetrics
    visualization_url: Optional[str] = None


class RiskFactor(BaseModel):
    """Risk factor detail."""
    name: str
    level: RiskLevel
    likelihood: str  # low, medium, high
    impact: str  # low, medium, high
    description: str
    mitigation: str


class RiskAssessment(BaseModel):
    """Risk assessment results."""
    overall_level: RiskLevel
    score: int = Field(..., ge=0, le=100)
    factors: List[RiskFactor]


class BreakingChange(BaseModel):
    """Breaking change information."""
    type: str
    file: str
    line: Optional[int] = None
    description: str
    migration: str
    severity: RiskLevel


class BehaviorChange(BaseModel):
    """Behavior change information."""
    type: str
    file: str
    description: str
    impact: str


class RegressionAnalysis(BaseModel):
    """Regression analysis results."""
    breaking_changes: List[BreakingChange] = Field(default_factory=list)
    behavior_changes: List[BehaviorChange] = Field(default_factory=list)
    deprecated_usage: List[Dict[str, Any]] = Field(default_factory=list)
    data_format_changes: List[Dict[str, Any]] = Field(default_factory=list)


class ImplementationPhase(BaseModel):
    """Implementation plan phase."""
    phase: int
    name: str
    description: str
    files: List[str]
    estimated_effort: str
    checkpoints: List[str]


class ImplementationPlan(BaseModel):
    """Safe implementation plan."""
    phases: List[ImplementationPhase]
    total_estimated_effort: str
    rollback_strategy: str
    prerequisites: List[str]


class TestUpdate(BaseModel):
    """Test update recommendation."""
    path: str
    changes: str
    priority: str


class NewTest(BaseModel):
    """New test recommendation."""
    type: str
    description: str
    priority: str


class CoverageGap(BaseModel):
    """Test coverage gap."""
    area: str
    current_coverage: int
    target_coverage: int


class TestRecommendations(BaseModel):
    """Test recommendations."""
    existing_tests_to_update: List[TestUpdate] = Field(default_factory=list)
    new_tests_needed: List[NewTest] = Field(default_factory=list)
    coverage_gaps: List[CoverageGap] = Field(default_factory=list)


class AnalysisResults(BaseModel):
    """Complete analysis results."""
    summary: AnalysisSummary
    affected_files: List[AffectedFile]
    impact_radius: ImpactRadius
    risk_assessment: RiskAssessment
    regression_analysis: RegressionAnalysis
    implementation_plan: ImplementationPlan
    test_recommendations: TestRecommendations


class AnalysisContextInfo(BaseModel):
    """Analysis context information."""
    files_selected: int
    functions_selected: int
    total_context_size: int


class AnalysisResponse(CommonBaseModel):
    """Analysis response."""
    id: str
    repository_id: str
    repository_name: Optional[str] = None
    description: str
    change_type: ChangeType
    status: AnalysisStatus
    progress: int = 0
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    context: AnalysisContextInfo
    results: Optional[AnalysisResults] = None
    risk_level: Optional[RiskLevel] = None
    impact_radius_category: Optional[str] = None
    files_affected_count: int = 0
    functions_affected_count: int = 0
    error_message: Optional[str] = None
    websocket_url: Optional[str] = None


class AnalysisListItem(CommonBaseModel):
    """Analysis list item."""
    id: str
    repository_id: str
    repository_name: str
    description: str
    change_type: ChangeType
    status: AnalysisStatus
    risk_level: Optional[RiskLevel]
    impact_radius: ImpactRadius
    progress: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None


class AnalysisListResponse(PaginatedResponse):
    """Analysis list response."""
    data: List[AnalysisListItem]


class AnalysisStepInfo(BaseModel):
    """Analysis step information."""
    name: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class AnalysisProgressResponse(CommonBaseModel):
    """Analysis progress response."""
    analysis_id: str
    status: AnalysisStatus
    progress: int
    current_step: str
    steps: List[AnalysisStepInfo]
    estimated_completion: Optional[datetime] = None


class AnalysisQueueResponse(CommonBaseModel):
    """Analysis queue response."""
    id: str
    repository_id: str
    status: AnalysisStatus
    queue_position: int
    estimated_wait_seconds: int
    created_at: datetime
    websocket_url: str


# ============== Dependency Graph Schemas ==============

class GraphNodeType(str, Enum):
    """Graph node types."""
    FILE = "file"
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    VARIABLE = "variable"


class GraphNode(BaseModel):
    """Dependency graph node."""
    id: str
    type: GraphNodeType
    name: str
    path: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    file_id: Optional[str] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None


class GraphEdgeType(str, Enum):
    """Graph edge types."""
    IMPORTS = "imports"
    CALLS = "calls"
    INHERITS = "inherits"
    CONTAINS = "contains"
    REFERENCES = "references"


class GraphEdge(BaseModel):
    """Dependency graph edge."""
    source: str
    target: str
    type: GraphEdgeType
    metadata: Optional[Dict[str, Any]] = None


class GraphStats(BaseModel):
    """Dependency graph statistics."""
    total_nodes: int
    total_edges: int
    files_count: int
    functions_count: int
    classes_count: int


class DependencyGraphResponse(CommonBaseModel):
    """Dependency graph response."""
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    stats: GraphStats


# ============== Search Schemas ==============

class SearchResultType(str, Enum):
    """Search result types."""
    FILE = "file"
    FUNCTION = "function"
    CLASS = "class"
    VARIABLE = "variable"


class SearchResult(BaseModel):
    """Search result item."""
    type: SearchResultType
    name: str
    file_path: str
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    language: Optional[str] = None
    context: Optional[str] = None
    score: float


class SearchResponse(CommonBaseModel):
    """Search response."""
    query: str
    total_results: int
    results: List[SearchResult]


# ============== Export Schemas ==============

class ExportFormat(str, Enum):
    """Export formats."""
    PDF = "pdf"
    MARKDOWN = "markdown"
    JSON = "json"


class ExportOptions(BaseModel):
    """Export options."""
    include_summary: bool = True
    include_affected_files: bool = True
    include_impact_radius: bool = True
    include_risk_assessment: bool = True
    include_regression_analysis: bool = True
    include_implementation_plan: bool = True
    include_tests: bool = True
    title: Optional[str] = None


class ExportRequest(CommonBaseModel):
    """Export request."""
    format: ExportFormat
    options: ExportOptions = Field(default_factory=ExportOptions)


class ExportResponse(CommonBaseModel):
    """Export response."""
    export_id: str
    status: str
    format: ExportFormat
    estimated_completion: Optional[datetime] = None


class ExportStatusResponse(CommonBaseModel):
    """Export status response."""
    id: str
    analysis_id: str
    format: ExportFormat
    status: str
    download_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    file_size: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


# ============== Health Schemas ==============

class HealthStatus(BaseModel):
    """Health check status."""
    status: str  # healthy, degraded, unhealthy
    timestamp: datetime
    version: str
    checks: Dict[str, Any]


# ============== WebSocket Schemas ==============

class WebSocketMessage(BaseModel):
    """WebSocket message."""
    type: str
    channel: Optional[str] = None
    data: Dict[str, Any]


class ProgressUpdate(BaseModel):
    """Progress update message."""
    analysis_id: str
    progress: int
    current_step: str
    message: Optional[str] = None
    timestamp: datetime


class AnalysisComplete(BaseModel):
    """Analysis complete message."""
    analysis_id: str
    status: str
    risk_level: Optional[RiskLevel] = None
    files_affected: int
    duration_seconds: float
    result_url: str
    timestamp: datetime
