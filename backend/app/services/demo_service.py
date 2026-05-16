"""Demo service for RepoTwin backend."""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, AsyncGenerator, Callable, Dict, Optional

from app.schemas.analysis import AnalysisResults

logger = logging.getLogger(__name__)


class DemoService:
    """Service for handling demo scenarios with sample data."""
    
    def __init__(self):
        """Initialize demo service."""
        self._demo_data: Optional[Dict[str, Any]] = None
        # Check both mounted volume path and local development path
        self._possible_paths = [
            Path("/data/sample-shadow-pr.json"),  # Docker mounted volume
            Path(__file__).parent.parent.parent.parent / "data" / "sample-shadow-pr.json",  # Local dev
        ]
    
    def _find_sample_data_path(self) -> Optional[Path]:
        """Find the sample data file path.
        
        Returns:
            Path to sample data file if found, None otherwise
        """
        for path in self._possible_paths:
            if path.exists():
                logger.debug(f"Found sample data at: {path}")
                return path
        return None
    
    async def load_demo_scenario(
        self,
        repo_name: str,
        change_description: str
    ) -> Dict[str, Any]:
        """Load demo scenario data from sample file.
        
        Args:
            repo_name: Repository name (e.g., "UniMarket")
            change_description: Change request description
            
        Returns:
            Demo scenario data dictionary
        """
        try:
            sample_path = self._find_sample_data_path()
            
            if sample_path is None:
                logger.error(f"Sample data file not found in any location: {self._possible_paths}")
                return self._create_fallback_demo(repo_name, change_description)
            
            with open(sample_path, "r", encoding="utf-8") as f:
                self._demo_data = json.load(f)
            
            logger.info(f"Loaded demo scenario for {repo_name}: {change_description}")
            return {
                "repository_name": repo_name,
                "change_description": change_description,
                "data": self._demo_data,
                "mode": "demo"
            }
            
        except Exception as e:
            logger.error(f"Failed to load demo scenario: {e}")
            return self._create_fallback_demo(repo_name, change_description)
    
    def _create_fallback_demo(
        self,
        repo_name: str,
        change_description: str
    ) -> Dict[str, Any]:
        """Create fallback demo data if sample file is unavailable.
        
        Args:
            repo_name: Repository name
            change_description: Change description
            
        Returns:
            Minimal demo data
        """
        return {
            "repository_name": repo_name,
            "change_description": change_description,
            "data": {
                "summary": {
                    "title": f"Impact Analysis: {change_description[:50]}...",
                    "overview": f"Analysis of changes to {repo_name}",
                    "key_points": ["Demo mode - sample data unavailable"]
                },
                "affected_files": [],
                "impact_radius": {
                    "category": "medium",
                    "metrics": {
                        "files_affected": 0,
                        "files_direct": 0,
                        "files_indirect": 0,
                        "functions_affected": 0,
                        "classes_affected": 0,
                        "tests_affected": 0,
                        "percentage_of_codebase": 0.0
                    }
                },
                "risk_assessment": {
                    "overall_level": "medium",
                    "score": 50,
                    "factors": []
                },
                "regression_analysis": {
                    "breaking_changes": [],
                    "behavior_changes": []
                },
                "implementation_plan": {
                    "phases": [],
                    "total_estimated_effort": "Unknown",
                    "rollback_strategy": "N/A",
                    "prerequisites": []
                },
                "test_recommendations": {
                    "existing_tests_to_update": [],
                    "new_tests_needed": [],
                    "coverage_gaps": []
                }
            },
            "mode": "demo"
        }
    
    async def get_demo_result(self) -> AnalysisResults:
        """Get demo analysis results from sample data.
        
        Returns:
            AnalysisResults parsed from sample data
        """
        if self._demo_data is None:
            # Load default demo if not already loaded
            await self.load_demo_scenario("UniMarket", "Add reservation flow before purchase.")
        
        data = self._demo_data or {}
        
        # Parse the sample data into AnalysisResults schema
        return AnalysisResults(
            summary=data.get("summary", {
                "title": "Demo Analysis",
                "overview": "Sample analysis results",
                "key_points": []
            }),
            affected_files=data.get("affected_files", []),
            impact_radius=data.get("impact_radius", {
                "category": "medium",
                "metrics": {
                    "files_affected": 0,
                    "files_direct": 0,
                    "files_indirect": 0,
                    "functions_affected": 0,
                    "classes_affected": 0,
                    "tests_affected": 0,
                    "percentage_of_codebase": 0.0
                }
            }),
            risk_assessment=data.get("risk_assessment", {
                "overall_level": "medium",
                "score": 50,
                "factors": []
            }),
            regression_analysis=data.get("regression_analysis", {
                "breaking_changes": [],
                "behavior_changes": []
            }),
            implementation_plan=data.get("implementation_plan", {
                "phases": [],
                "total_estimated_effort": "Unknown",
                "rollback_strategy": "N/A",
                "prerequisites": []
            }),
            test_recommendations=data.get("test_recommendations", {
                "existing_tests_to_update": [],
                "new_tests_needed": [],
                "coverage_gaps": []
            }),
            provider="sample",
            enhanced_by_llm=False,
        )
    
    async def simulate_progress(
        self,
        callback: Optional[Callable[[int, str], None]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Simulate analysis progress updates.
        
        Yields progress updates from 0% to 100% at predefined stages.
        Progress stages: 0%, 10%, 25%, 45%, 65%, 85%, 95%, 100%
        
        Args:
            callback: Optional callback function(progress_percent, message)
            
        Yields:
            Dict with progress_percent and message
        """
        progress_stages = [
            (0, "Initializing analysis..."),
            (10, "Loading repository context..."),
            (25, "Parsing affected files with IBM Bob-assisted analysis..."),
            (45, "Calculating blast radius and impact metrics..."),
            (65, "Analyzing risks and regressions..."),
            (85, "Generating implementation plan and test recommendations..."),
            (95, "Finalizing Shadow PR brief..."),
            (100, "Analysis complete")
        ]
        
        for progress_percent, message in progress_stages:
            update = {
                "progress_percent": progress_percent,
                "message": message
            }
            
            # Call callback if provided
            if callback:
                callback(progress_percent, message)
            
            yield update
            
            # Wait 0.5 seconds between updates (except after final update)
            if progress_percent < 100:
                await asyncio.sleep(0.5)


# Global demo service instance
demo_service = DemoService()
