"""Risk calculation module."""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Set

from app.schemas.analysis import RiskFactor, RiskLevel

logger = logging.getLogger(__name__)


@dataclass
class RiskMetrics:
    """Risk metrics for a change."""
    total_files: int = 0
    direct_files: int = 0
    indirect_files: int = 0
    test_coverage: float = 0.0
    complexity_increase: int = 0
    breaking_changes: int = 0
    external_dependencies: int = 0
    entry_points_affected: int = 0


class RiskCalculator:
    """Calculate risk scores for code changes."""
    
    # Risk weights
    WEIGHTS = {
        'files_affected': 10,
        'test_coverage': 20,
        'complexity': 15,
        'breaking_changes': 25,
        'dependencies': 10,
        'entry_points': 20,
    }
    
    def __init__(self):
        """Initialize risk calculator."""
        pass
    
    def calculate_risk_score(
        self,
        metrics: RiskMetrics,
        affected_files: List[str],
    ) -> tuple[int, RiskLevel, List[RiskFactor]]:
        """Calculate overall risk score.
        
        Args:
            metrics: Risk metrics
            affected_files: List of affected file paths
            
        Returns:
            Tuple of (score, level, factors)
        """
        score = 0
        factors = []
        
        # Files affected score (0-30)
        if metrics.total_files > 20:
            file_score = 30
            factors.append(RiskFactor(
                name="Large Number of Files",
                level=RiskLevel.HIGH,
                likelihood="high",
                impact="high",
                description=f"{metrics.total_files} files will be modified, increasing chance of errors",
                mitigation="Break change into smaller PRs, implement incrementally",
            ))
        elif metrics.total_files > 10:
            file_score = 20
            factors.append(RiskFactor(
                name="Moderate Number of Files",
                level=RiskLevel.MEDIUM,
                likelihood="medium",
                impact="medium",
                description=f"{metrics.total_files} files affected",
                mitigation="Ensure comprehensive test coverage",
            ))
        elif metrics.total_files > 5:
            file_score = 10
            factors.append(RiskFactor(
                name="Small Number of Files",
                level=RiskLevel.LOW,
                likelihood="low",
                impact="low",
                description=f"{metrics.total_files} files affected",
                mitigation="Standard code review process",
            ))
        else:
            file_score = 5
        
        score += file_score
        
        # Test coverage score (0-20)
        if metrics.test_coverage < 50:
            coverage_score = 20
            factors.append(RiskFactor(
                name="Low Test Coverage",
                level=RiskLevel.HIGH,
                likelihood="high",
                impact="high",
                description=f"Only {metrics.test_coverage:.1f}% test coverage in affected areas",
                mitigation="Add tests before making changes",
            ))
        elif metrics.test_coverage < 70:
            coverage_score = 10
            factors.append(RiskFactor(
                name="Moderate Test Coverage",
                level=RiskLevel.MEDIUM,
                likelihood="medium",
                impact="medium",
                description=f"{metrics.test_coverage:.1f}% test coverage",
                mitigation="Add tests for modified functionality",
            ))
        else:
            coverage_score = 5
        
        score += coverage_score
        
        # Complexity score (0-15)
        if metrics.complexity_increase > 10:
            complexity_score = 15
            factors.append(RiskFactor(
                name="High Complexity Increase",
                level=RiskLevel.HIGH,
                likelihood="high",
                impact="medium",
                description=f"Complexity increases by {metrics.complexity_increase}",
                mitigation="Refactor to reduce complexity",
            ))
        elif metrics.complexity_increase > 5:
            complexity_score = 8
        else:
            complexity_score = 2
        
        score += complexity_score
        
        # Breaking changes score (0-25)
        if metrics.breaking_changes > 3:
            breaking_score = 25
            factors.append(RiskFactor(
                name="Multiple Breaking Changes",
                level=RiskLevel.CRITICAL,
                likelihood="high",
                impact="critical",
                description=f"{metrics.breaking_changes} breaking changes detected",
                mitigation="Implement backward compatibility layer, deprecate gradually",
            ))
        elif metrics.breaking_changes > 0:
            breaking_score = 15 * metrics.breaking_changes
            factors.append(RiskFactor(
                name="Breaking Changes",
                level=RiskLevel.HIGH,
                likelihood="high",
                impact="high",
                description=f"{metrics.breaking_changes} breaking change(s)",
                mitigation="Document migration path, update API contracts",
            ))
        else:
            breaking_score = 0
        
        score += breaking_score
        
        # Dependencies score (0-10)
        if metrics.external_dependencies > 5:
            dep_score = 10
            factors.append(RiskFactor(
                name="Many External Dependencies",
                level=RiskLevel.MEDIUM,
                likelihood="medium",
                impact="medium",
                description=f"{metrics.external_dependencies} external dependencies affected",
                mitigation="Verify compatibility with external services",
            ))
        elif metrics.external_dependencies > 2:
            dep_score = 5
        else:
            dep_score = 0
        
        score += dep_score
        
        # Entry points score (0-20)
        if metrics.entry_points_affected > 3:
            entry_score = 20
            factors.append(RiskFactor(
                name="Critical Entry Points",
                level=RiskLevel.CRITICAL,
                likelihood="high",
                impact="critical",
                description=f"{metrics.entry_points_affected} entry points affected",
                mitigation="Thorough integration testing required",
            ))
        elif metrics.entry_points_affected > 1:
            entry_score = 10
            factors.append(RiskFactor(
                name="Entry Points Affected",
                level=RiskLevel.HIGH,
                likelihood="high",
                impact="high",
                description=f"{metrics.entry_points_affected} entry points affected",
                mitigation="Test all affected entry points",
            ))
        elif metrics.entry_points_affected == 1:
            entry_score = 5
        else:
            entry_score = 0
        
        score += entry_score
        
        # Determine risk level
        if score >= 80:
            level = RiskLevel.CRITICAL
        elif score >= 60:
            level = RiskLevel.HIGH
        elif score >= 40:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW
        
        # Ensure at least one factor exists
        if not factors:
            factors.append(RiskFactor(
                name="Low Risk",
                level=RiskLevel.LOW,
                likelihood="low",
                impact="low",
                description="Change appears to be low risk based on metrics",
                mitigation="Standard code review and testing",
            ))
        
        return min(score, 100), level, factors
    
    def calculate_file_risk(self, file_path: str, is_tested: bool) -> Dict[str, any]:
        """Calculate risk for a specific file.
        
        Args:
            file_path: Path to the file
            is_tested: Whether file has tests
            
        Returns:
            Risk assessment for the file
        """
        risk_score = 0
        risk_factors = []
        
        # Check for critical files
        critical_patterns = [
            'main.py', 'app.py', 'server.py', 'index.js', 'index.ts',
            'config.py', 'settings.py', 'database.py', 'auth.py',
        ]
        
        if any(pattern in file_path for pattern in critical_patterns):
            risk_score += 30
            risk_factors.append("Critical system file")
        
        # Check for core business logic
        if any(pattern in file_path for pattern in ['core/', 'domain/', 'business/']):
            risk_score += 20
            risk_factors.append("Core business logic")
        
        # Test coverage
        if not is_tested:
            risk_score += 25
            risk_factors.append("No test coverage")
        
        # Determine level
        if risk_score >= 60:
            level = RiskLevel.HIGH
        elif risk_score >= 40:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW
        
        return {
            'file_path': file_path,
            'risk_score': min(risk_score, 100),
            'risk_level': level,
            'factors': risk_factors,
        }
    
    def generate_mitigation_plan(
        self,
        factors: List[RiskFactor],
        affected_files: List[str],
    ) -> List[str]:
        """Generate mitigation plan based on risk factors.
        
        Args:
            factors: List of risk factors
            affected_files: List of affected files
            
        Returns:
            List of mitigation steps
        """
        steps = []
        
        # Always include basic steps
        steps.append("1. Review all affected files manually")
        steps.append("2. Run existing test suite to establish baseline")
        
        # Add factor-specific mitigations
        high_risk_factors = [f for f in factors if f.level in (RiskLevel.HIGH, RiskLevel.CRITICAL)]
        if high_risk_factors:
            steps.append("3. Conduct thorough code review with senior developers")
            steps.append("4. Create comprehensive test plan")
        
        # Check for breaking changes
        breaking_factors = [f for f in factors if "breaking" in f.name.lower()]
        if breaking_factors:
            steps.append("5. Document all breaking changes")
            steps.append("6. Create migration guide for consumers")
            steps.append("7. Consider backward compatibility layer")
        
        # Check for low test coverage
        coverage_factors = [f for f in factors if "coverage" in f.name.lower()]
        if coverage_factors:
            steps.append("8. Add unit tests for modified functionality")
            steps.append("9. Add integration tests for affected workflows")
        
        # Check for entry points
        entry_factors = [f for f in factors if "entry" in f.name.lower()]
        if entry_factors:
            steps.append("10. Test all affected entry points manually")
            steps.append("11. Verify error handling at entry points")
        
        # Deployment steps
        steps.append(f"12. Deploy to staging environment first")
        steps.append(f"13. Monitor metrics after deployment")
        
        return steps


# Singleton instance
risk_calculator = RiskCalculator()
