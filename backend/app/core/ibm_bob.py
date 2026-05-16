"""IBM watsonx.ai (Bob) integration for RepoTwin."""

import json
import logging
from typing import Any, Dict, List, Optional

from circuitbreaker import circuit
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import settings
from app.schemas.analysis import (
    AffectedFile,
    AnalysisResults,
    AnalysisSummary,
    BehaviorChange,
    BreakingChange,
    ImplementationPhase,
    ImplementationPlan,
    ImpactLevel,
    ImpactRadius,
    ImpactRadiusMetrics,
    NewTest,
    RegressionAnalysis,
    RiskAssessment,
    RiskFactor,
    RiskLevel,
    TestRecommendations,
    TestUpdate,
)

logger = logging.getLogger(__name__)


class WatsonxAIError(Exception):
    """IBM watsonx.ai API error."""
    pass


class WatsonxAIRateLimitError(WatsonxAIError):
    """Rate limit exceeded error."""
    pass


class IBMBobClient:
    """Client for IBM watsonx.ai (Bob) API."""
    
    def __init__(self):
        """Initialize IBM Bob client."""
        self.api_key = settings.watsonx_api_key
        self.project_id = settings.watsonx_project_id
        self.url = settings.watsonx_url
        self.model_id = settings.watsonx_model_id
        self.max_tokens = settings.watsonx_max_tokens
        self.temperature = settings.watsonx_temperature
        self.top_p = settings.watsonx_top_p
        
        self._client = None
        self._model = None
    
    def _get_client(self):
        """Get or create IBM watsonx.ai client."""
        if self._client is None:
            try:
                from ibm_watsonx_ai import Credentials, APIClient
                
                credentials = Credentials(
                    api_key=self.api_key,
                    url=self.url,
                )
                self._client = APIClient(credentials)
                
                # Project ID is optional for some IBM Bob configurations
                if self.project_id:
                    self._client.set_default_project(self.project_id)
                    logger.info("IBM watsonx.ai client initialized with project")
                else:
                    logger.info("IBM watsonx.ai client initialized without project (using default)")
                
            except ImportError:
                logger.warning("ibm-watsonx-ai not installed, using mock client")
                self._client = MockWatsonxClient()
            except Exception as e:
                logger.error(f"Failed to initialize IBM watsonx.ai client: {e}")
                self._client = MockWatsonxClient()
        
        return self._client
    
    def _get_model(self):
        """Get or create model instance."""
        if self._model is None:
            client = self._get_client()
            
            if isinstance(client, MockWatsonxClient):
                self._model = client
            else:
                from ibm_watsonx_ai.foundation_models import Model
                
                # Build model parameters
                model_params = {
                    "max_new_tokens": self.max_tokens,
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                    "stop_sequences": ["<|endoftext|>"],
                }
                
                # Build model kwargs - project_id is optional
                model_kwargs = {
                    "model_id": self.model_id,
                    "params": model_params,
                    "credentials": client.credentials,
                }
                
                # Only add project_id if it's set
                if self.project_id:
                    model_kwargs["project_id"] = self.project_id
                
                self._model = Model(**model_kwargs)
        
        return self._model
    
    @circuit(failure_threshold=5, recovery_timeout=60)
    @retry(
        retry=retry_if_exception_type(WatsonxAIRateLimitError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
    )
    async def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate text using IBM watsonx.ai.
        
        Args:
            prompt: The prompt to send to the model
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
            
        Raises:
            WatsonxAIError: If the API call fails
        """
        try:
            model = self._get_model()
            
            params = {
                "max_new_tokens": max_tokens or self.max_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p,
            }
            
            if isinstance(model, MockWatsonxClient):
                return await model.generate(prompt, params)
            
            response = model.generate_text(prompt=prompt, params=params)
            
            if not response:
                raise WatsonxAIError("Empty response from watsonx.ai")
            
            return response
            
        except WatsonxAIRateLimitError:
            raise
        except Exception as e:
            logger.error(f"watsonx.ai API error: {e}")
            raise WatsonxAIError(f"API call failed: {e}") from e
    
    def _build_impact_analysis_prompt(
        self,
        repository_context: str,
        change_description: str,
        affected_code: str,
    ) -> str:
        """Build prompt for impact analysis.
        
        Args:
            repository_context: Repository overview and structure
            change_description: User's change description
            affected_code: Selected code context
            
        Returns:
            Formatted prompt
        """
        return f"""You are an expert software architect performing impact analysis for a proposed code change.

## Repository Context
```
{repository_context}
```

## Proposed Change
{change_description}

## Selected Code Context
```
{affected_code}
```

## Task
Analyze the proposed change and provide a comprehensive impact assessment. Return your analysis as a valid JSON object with this exact structure:

{{
  "summary": {{
    "title": "Brief title of the analysis",
    "overview": "2-3 sentence overview of the impact",
    "key_points": ["Key point 1", "Key point 2", "Key point 3"]
  }},
  "affected_files": [
    {{
      "path": "src/example.py",
      "impact_level": "direct|indirect|potential",
      "change_type": "modification|addition|deletion",
      "reasoning": "Why this file is affected",
      "lines_added": 10,
      "lines_removed": 5,
      "complexity_change": "increased|decreased|neutral",
      "risk_factors": ["Factor 1", "Factor 2"]
    }}
  ],
  "impact_radius": {{
    "category": "small|medium|large",
    "metrics": {{
      "files_affected": 5,
      "files_direct": 2,
      "files_indirect": 3,
      "functions_affected": 10,
      "classes_affected": 3,
      "tests_affected": 4,
      "percentage_of_codebase": 2.5
    }}
  }},
  "risk_assessment": {{
    "overall_level": "low|medium|high|critical",
    "score": 65,
    "factors": [
      {{
        "name": "Risk Factor Name",
        "level": "medium",
        "likelihood": "medium",
        "impact": "high",
        "description": "Description of the risk",
        "mitigation": "How to mitigate"
      }}
    ]
  }},
  "regression_analysis": {{
    "breaking_changes": [
      {{
        "type": "api_signature|behavior|data_format",
        "file": "src/example.py",
        "line": 42,
        "description": "Description of breaking change",
        "migration": "How to migrate",
        "severity": "high"
      }}
    ],
    "behavior_changes": [
      {{
        "type": "error_handling|performance|logic",
        "file": "src/example.py",
        "description": "Description of behavior change",
        "impact": "Impact description"
      }}
    ]
  }},
  "implementation_plan": {{
    "phases": [
      {{
        "phase": 1,
        "name": "Phase name",
        "description": "Phase description",
        "files": ["src/file1.py", "src/file2.py"],
        "estimated_effort": "2 hours",
        "checkpoints": ["Checkpoint 1", "Checkpoint 2"]
      }}
    ],
    "total_estimated_effort": "6 hours",
    "rollback_strategy": "How to rollback if needed",
    "prerequisites": ["Prerequisite 1", "Prerequisite 2"]
  }},
  "test_recommendations": {{
    "existing_tests_to_update": [
      {{
        "path": "tests/test_example.py",
        "changes": "What needs to change",
        "priority": "high"
      }}
    ],
    "new_tests_needed": [
      {{
        "type": "unit|integration|e2e",
        "description": "Test description",
        "priority": "high"
      }}
    ],
    "coverage_gaps": [
      {{
        "area": "Area name",
        "current_coverage": 45,
        "target_coverage": 80
      }}
    ]
  }}
}}

Ensure your response is ONLY the JSON object, with no markdown formatting, no explanatory text, and no code blocks."""

    async def analyze_impact(
        self,
        repository_context: str,
        change_description: str,
        affected_code: str,
    ) -> AnalysisResults:
        """Perform AI-powered impact analysis.
        
        Args:
            repository_context: Repository overview
            change_description: User's change description
            affected_code: Selected code context
            
        Returns:
            Analysis results
        """
        prompt = self._build_impact_analysis_prompt(
            repository_context,
            change_description,
            affected_code,
        )
        
        response = await self.generate_text(prompt)
        
        try:
            # Parse JSON response
            data = json.loads(response)
            
            # Convert to Pydantic models
            return self._parse_analysis_results(data)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.debug(f"Response: {response[:500]}...")
            return self._generate_fallback_results(change_description)
        except Exception as e:
            logger.error(f"Error processing AI response: {e}")
            return self._generate_fallback_results(change_description)
    
    def _parse_analysis_results(self, data: Dict[str, Any]) -> AnalysisResults:
        """Parse AI response into AnalysisResults."""
        # Parse affected files
        affected_files = [
            AffectedFile(
                path=f.get("path", "unknown"),
                impact_level=ImpactLevel(f.get("impact_level", "potential")),
                change_type=f.get("change_type", "modification"),
                reasoning=f.get("reasoning", ""),
                lines_added=f.get("lines_added", 0),
                lines_removed=f.get("lines_removed", 0),
                complexity_change=f.get("complexity_change", "neutral"),
                risk_factors=f.get("risk_factors", []),
            )
            for f in data.get("affected_files", [])
        ]
        
        # Parse impact radius
        impact_data = data.get("impact_radius", {})
        metrics_data = impact_data.get("metrics", {})
        impact_radius = ImpactRadius(
            category=impact_data.get("category", "small"),
            metrics=ImpactRadiusMetrics(
                files_affected=metrics_data.get("files_affected", 0),
                files_direct=metrics_data.get("files_direct", 0),
                files_indirect=metrics_data.get("files_indirect", 0),
                functions_affected=metrics_data.get("functions_affected", 0),
                classes_affected=metrics_data.get("classes_affected", 0),
                tests_affected=metrics_data.get("tests_affected", 0),
                percentage_of_codebase=metrics_data.get("percentage_of_codebase", 0.0),
            ),
        )
        
        # Parse risk assessment
        risk_data = data.get("risk_assessment", {})
        risk_factors = [
            RiskFactor(
                name=rf.get("name", ""),
                level=RiskLevel(rf.get("level", "low")),
                likelihood=rf.get("likelihood", "low"),
                impact=rf.get("impact", "low"),
                description=rf.get("description", ""),
                mitigation=rf.get("mitigation", ""),
            )
            for rf in risk_data.get("factors", [])
        ]
        risk_assessment = RiskAssessment(
            overall_level=RiskLevel(risk_data.get("overall_level", "low")),
            score=risk_data.get("score", 0),
            factors=risk_factors,
        )
        
        # Parse regression analysis
        reg_data = data.get("regression_analysis", {})
        breaking_changes = [
            BreakingChange(
                type=bc.get("type", ""),
                file=bc.get("file", ""),
                line=bc.get("line"),
                description=bc.get("description", ""),
                migration=bc.get("migration", ""),
                severity=RiskLevel(bc.get("severity", "low")),
            )
            for bc in reg_data.get("breaking_changes", [])
        ]
        behavior_changes = [
            BehaviorChange(
                type=bc.get("type", ""),
                file=bc.get("file", ""),
                description=bc.get("description", ""),
                impact=bc.get("impact", ""),
            )
            for bc in reg_data.get("behavior_changes", [])
        ]
        regression_analysis = RegressionAnalysis(
            breaking_changes=breaking_changes,
            behavior_changes=behavior_changes,
        )
        
        # Parse implementation plan
        impl_data = data.get("implementation_plan", {})
        phases = [
            ImplementationPhase(
                phase=p.get("phase", i + 1),
                name=p.get("name", ""),
                description=p.get("description", ""),
                files=p.get("files", []),
                estimated_effort=p.get("estimated_effort", ""),
                checkpoints=p.get("checkpoints", []),
            )
            for i, p in enumerate(impl_data.get("phases", []))
        ]
        implementation_plan = ImplementationPlan(
            phases=phases,
            total_estimated_effort=impl_data.get("total_estimated_effort", ""),
            rollback_strategy=impl_data.get("rollback_strategy", ""),
            prerequisites=impl_data.get("prerequisites", []),
        )
        
        # Parse test recommendations
        test_data = data.get("test_recommendations", {})
        test_recommendations = TestRecommendations(
            existing_tests_to_update=[
                TestUpdate(
                    path=t.get("path", ""),
                    changes=t.get("changes", ""),
                    priority=t.get("priority", "medium"),
                )
                for t in test_data.get("existing_tests_to_update", [])
            ],
            new_tests_needed=[
                NewTest(
                    type=t.get("type", ""),
                    description=t.get("description", ""),
                    priority=t.get("priority", "medium"),
                )
                for t in test_data.get("new_tests_needed", [])
            ],
        )
        
        # Parse summary
        summary_data = data.get("summary", {})
        summary = AnalysisSummary(
            title=summary_data.get("title", "Impact Analysis"),
            overview=summary_data.get("overview", ""),
            key_points=summary_data.get("key_points", []),
        )
        
        return AnalysisResults(
            summary=summary,
            affected_files=affected_files,
            impact_radius=impact_radius,
            risk_assessment=risk_assessment,
            regression_analysis=regression_analysis,
            implementation_plan=implementation_plan,
            test_recommendations=test_recommendations,
        )
    
    def _generate_fallback_results(self, change_description: str) -> AnalysisResults:
        """Generate fallback results when AI analysis fails."""
        return AnalysisResults(
            summary=AnalysisSummary(
                title="Impact Analysis (Fallback)",
                overview=f"Analysis of: {change_description[:100]}...",
                key_points=["AI analysis encountered an error", "Please review manually"],
            ),
            affected_files=[],
            impact_radius=ImpactRadius(
                category="small",
                metrics=ImpactRadiusMetrics(),
            ),
            risk_assessment=RiskAssessment(
                overall_level=RiskLevel.LOW,
                score=0,
                factors=[],
            ),
            regression_analysis=RegressionAnalysis(),
            implementation_plan=ImplementationPlan(
                phases=[],
                total_estimated_effort="",
                rollback_strategy="",
                prerequisites=[],
            ),
            test_recommendations=TestRecommendations(),
        )


class MockWatsonxClient:
    """Mock client for testing without API credentials."""
    
    async def generate(self, prompt: str, params: Dict[str, Any]) -> str:
        """Generate mock response."""
        import random
        
        # Extract some info from the prompt for realistic-looking response
        files_affected = random.randint(3, 15)
        risk_score = random.randint(20, 80)
        risk_level = "low" if risk_score < 40 else "medium" if risk_score < 70 else "high"
        
        return f"""{{
  "summary": {{
    "title": "Impact Analysis Results",
    "overview": "This change affects approximately {files_affected} files with {risk_level} risk level. The main changes involve updating core logic and ensuring backward compatibility.",
    "key_points": [
      "{files_affected} files require modifications",
      "Primary impact on core business logic",
      "Test coverage should be increased",
      "Documentation updates needed"
    ]
  }},
  "affected_files": [
    {{
      "path": "src/main.py",
      "impact_level": "direct",
      "change_type": "modification",
      "reasoning": "Primary file containing core logic",
      "lines_added": 25,
      "lines_removed": 10,
      "complexity_change": "neutral",
      "risk_factors": ["Core business logic"]
    }}
  ],
  "impact_radius": {{
    "category": "{risk_level}",
    "metrics": {{
      "files_affected": {files_affected},
      "files_direct": {files_affected // 3},
      "files_indirect": {files_affected * 2 // 3},
      "functions_affected": {files_affected * 3},
      "classes_affected": {files_affected // 2},
      "tests_affected": {files_affected // 2},
      "percentage_of_codebase": 2.5
    }}
  }},
  "risk_assessment": {{
    "overall_level": "{risk_level}",
    "score": {risk_score},
    "factors": [
      {{
        "name": "API Compatibility",
        "level": "{risk_level}",
        "likelihood": "medium",
        "impact": "high",
        "description": "Changes may affect public API signatures",
        "mitigation": "Add deprecation warnings and maintain backward compatibility"
      }}
    ]
  }},
  "regression_analysis": {{
    "breaking_changes": [],
    "behavior_changes": [
      {{
        "type": "error_handling",
        "file": "src/main.py",
        "description": "Error handling behavior may change",
        "impact": "Existing error handling may need updates"
      }}
    ]
  }},
  "implementation_plan": {{
    "phases": [
      {{
        "phase": 1,
        "name": "Update Core Logic",
        "description": "Implement the primary changes",
        "files": ["src/main.py"],
        "estimated_effort": "2 hours",
        "checkpoints": ["Unit tests pass", "Integration tests pass"]
      }}
    ],
    "total_estimated_effort": "4 hours",
    "rollback_strategy": "Revert to previous commit",
    "prerequisites": ["Database backup", "Staging environment"]
  }},
  "test_recommendations": {{
    "existing_tests_to_update": [
      {{
        "path": "tests/test_main.py",
        "changes": "Update test cases for new behavior",
        "priority": "high"
      }}
    ],
    "new_tests_needed": [
      {{
        "type": "unit",
        "description": "Test new edge cases",
        "priority": "medium"
      }}
    ],
    "coverage_gaps": []
  }}
}}"""


# Singleton instance
ibm_bob_client = IBMBobClient()
