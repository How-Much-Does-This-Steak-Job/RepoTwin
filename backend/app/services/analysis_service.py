"""Analysis service for RepoTwin backend."""

import json
import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from app.redis import get_store
from app.schemas.analysis import (
    Analysis,
    AnalysisCreate,
    AnalysisList,
    AnalysisProgress,
    AnalysisResults,
    AnalysisStatus,
)
from app.services.demo_service import demo_service

logger = logging.getLogger(__name__)


class AnalysisService:
    """Service for managing code change analysis jobs."""
    
    # Redis key patterns
    ANALYSIS_KEY_PREFIX = "analysis"
    ANALYSIS_LIST_KEY = "analyses:list"
    TTL_SECONDS = 3600  # 1 hour TTL for analysis data
    
    def __init__(self):
        """Initialize analysis service."""
        self._store = None
    
    async def _get_store(self):
        """Get store instance (lazy initialization)."""
        if self._store is None:
            self._store = await get_store()
        return self._store
    
    def _get_analysis_key(self, analysis_id: UUID) -> str:
        """Generate Redis key for analysis data."""
        return f"{self.ANALYSIS_KEY_PREFIX}:{str(analysis_id)}:data"
    
    def _get_progress_key(self, analysis_id: UUID) -> str:
        """Generate Redis key for analysis progress."""
        return f"{self.ANALYSIS_KEY_PREFIX}:{str(analysis_id)}:progress"
    
    def _get_result_key(self, analysis_id: UUID) -> str:
        """Generate Redis key for analysis results."""
        return f"{self.ANALYSIS_KEY_PREFIX}:{str(analysis_id)}:result"
    
    async def create_analysis(self, data: AnalysisCreate) -> Analysis:
        """Create a new analysis job.
        
        Args:
            data: Analysis creation data
            
        Returns:
            Created Analysis object
        """
        store = await self._get_store()
        
        # Generate UUID4 for analysis ID
        analysis_id = uuid4()
        now = datetime.utcnow()
        
        # Create analysis object
        analysis = Analysis(
            id=analysis_id,
            repo_id=data.repo_id,
            change_description=data.change_description,
            target_branch=data.target_branch,
            status=AnalysisStatus.PENDING,
            progress_percent=0,
            current_step="Initializing",
            created_at=now,
            updated_at=now,
        )
        
        # Store in Redis
        analysis_key = self._get_analysis_key(analysis_id)
        await store.set(
            analysis_key,
            analysis.json(),
            ttl=self.TTL_SECONDS
        )
        
        # Initialize progress
        progress_key = self._get_progress_key(analysis_id)
        progress_data = {
            "analysis_id": str(analysis_id),
            "status": AnalysisStatus.PENDING.value,
            "progress_percent": 0,
            "current_step": "Initializing",
            "message": "Analysis created, waiting to start...",
            "estimated_time_remaining": None
        }
        await store.set(
            progress_key,
            json.dumps(progress_data),
            ttl=self.TTL_SECONDS
        )
        
        logger.info(f"Created analysis {analysis_id} for repo {data.repo_id}")
        return analysis
    
    async def get_analysis(self, analysis_id: UUID) -> Optional[Analysis]:
        """Get analysis by ID.
        
        Args:
            analysis_id: Analysis UUID
            
        Returns:
            Analysis object if found, None otherwise
        """
        store = await self._get_store()
        
        analysis_key = self._get_analysis_key(analysis_id)
        data = await store.get(analysis_key)
        
        if data is None:
            return None
        
        try:
            analysis_dict = json.loads(data)
            return Analysis(**analysis_dict)
        except Exception as e:
            logger.error(f"Failed to parse analysis {analysis_id}: {e}")
            return None
    
    async def list_analyses(
        self,
        repo_id: Optional[UUID] = None,
        status: Optional[AnalysisStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> AnalysisList:
        """List analyses with optional filtering.
        
        Args:
            repo_id: Filter by repository ID
            status: Filter by status
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            AnalysisList with items and pagination info
        """
        store = await self._get_store()
        
        # Get all analysis keys
        pattern = f"{self.ANALYSIS_KEY_PREFIX}:*:data"
        keys = await store.keys(pattern)
        
        analyses = []
        for key in keys:
            try:
                data = await store.get(key)
                if data:
                    analysis_dict = json.loads(data)
                    
                    # Apply filters
                    if repo_id and analysis_dict.get("repo_id") != str(repo_id):
                        continue
                    if status and analysis_dict.get("status") != status.value:
                        continue
                    
                    analyses.append(Analysis(**analysis_dict))
            except Exception as e:
                logger.error(f"Failed to parse analysis from key {key}: {e}")
                continue
        
        # Sort by created_at descending
        analyses.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply pagination
        total = len(analyses)
        paginated = analyses[skip:skip + limit]
        
        return AnalysisList(
            items=paginated,
            total=total,
            skip=skip,
            limit=limit
        )
    
    async def get_analysis_progress(self, analysis_id: UUID) -> Optional[AnalysisProgress]:
        """Get analysis progress.
        
        Args:
            analysis_id: Analysis UUID
            
        Returns:
            AnalysisProgress if found, None otherwise
        """
        store = await self._get_store()
        
        # First check if analysis exists
        analysis = await self.get_analysis(analysis_id)
        if analysis is None:
            return None
        
        # Get progress data
        progress_key = self._get_progress_key(analysis_id)
        data = await store.get(progress_key)
        
        if data:
            try:
                progress_dict = json.loads(data)
                return AnalysisProgress(**progress_dict)
            except Exception as e:
                logger.error(f"Failed to parse progress for {analysis_id}: {e}")
        
        # Return default progress based on analysis status
        return AnalysisProgress(
            analysis_id=analysis_id,
            status=analysis.status.value,
            progress_percent=analysis.progress_percent,
            current_step=analysis.current_step or "Unknown",
            message="Progress information unavailable",
            estimated_time_remaining=None
        )
    
    async def get_analysis_results(self, analysis_id: UUID) -> Optional[AnalysisResults]:
        """Get analysis results (only if completed).
        
        Args:
            analysis_id: Analysis UUID
            
        Returns:
            AnalysisResults if completed, None otherwise
        """
        store = await self._get_store()
        
        # Check analysis status first
        analysis = await self.get_analysis(analysis_id)
        if analysis is None:
            return None
        
        if analysis.status != AnalysisStatus.COMPLETED:
            logger.warning(f"Analysis {analysis_id} not completed (status: {analysis.status})")
            return None
        
        # Get results from Redis
        result_key = self._get_result_key(analysis_id)
        data = await store.get(result_key)
        
        if data is None:
            logger.warning(f"No results found for completed analysis {analysis_id}")
            return None
        
        try:
            result_dict = json.loads(data)
            return AnalysisResults(**result_dict)
        except Exception as e:
            logger.error(f"Failed to parse results for {analysis_id}: {e}")
            return None
    
    async def delete_analysis(self, analysis_id: UUID) -> bool:
        """Delete analysis and associated data.
        
        Args:
            analysis_id: Analysis UUID
            
        Returns:
            True if deleted, False if not found
        """
        store = await self._get_store()
        
        # Check if exists
        if not await store.exists(self._get_analysis_key(analysis_id)):
            return False
        
        # Delete all associated keys
        await store.delete(self._get_analysis_key(analysis_id))
        await store.delete(self._get_progress_key(analysis_id))
        await store.delete(self._get_result_key(analysis_id))
        
        logger.info(f"Deleted analysis {analysis_id}")
        return True
    
    async def run_analysis(
        self,
        analysis_id: UUID,
        mode: str = "demo"
    ) -> None:
        """Execute analysis in background (public method for background tasks).
        
        This is the public entry point for running analysis jobs.
        
        Args:
            analysis_id: Analysis UUID
            mode: "demo" or "live" mode
        """
        await self._execute_analysis(analysis_id, mode)
    
    async def _execute_analysis(
        self,
        analysis_id: UUID,
        mode: str = "live"
    ) -> None:
        """Execute analysis in background (internal implementation).
        
        This method simulates the analysis execution with progress updates.
        In production, this would integrate with IBM Bob for actual analysis.
        
        Args:
            analysis_id: Analysis UUID
            mode: "live" or "demo" mode
        """
        store = await self._get_store()
        
        try:
            # Update status to running
            analysis = await self.get_analysis(analysis_id)
            if analysis is None:
                logger.error(f"Analysis {analysis_id} not found for execution")
                return
            
            analysis.status = AnalysisStatus.RUNNING
            analysis.started_at = datetime.utcnow()
            analysis.updated_at = datetime.utcnow()
            analysis.current_step = "Analyzing repository"
            
            await store.set(
                self._get_analysis_key(analysis_id),
                analysis.json(),
                ttl=self.TTL_SECONDS
            )
            
            # Simulate progress
            if mode == "demo":
                # Use demo service for progress simulation
                async for update in demo_service.simulate_progress():
                    progress_percent = update["progress_percent"]
                    message = update["message"]
                    
                    # Update progress in Redis
                    progress_data = {
                        "analysis_id": str(analysis_id),
                        "status": AnalysisStatus.RUNNING.value,
                        "progress_percent": progress_percent,
                        "current_step": message,
                        "message": message,
                        "estimated_time_remaining": (100 - progress_percent) * 2  # Rough estimate
                    }
                    await store.set(
                        self._get_progress_key(analysis_id),
                        json.dumps(progress_data),
                        ttl=self.TTL_SECONDS
                    )
                    
                    # Update analysis object
                    analysis.progress_percent = progress_percent
                    analysis.current_step = message
                    analysis.updated_at = datetime.utcnow()
                    await store.set(
                        self._get_analysis_key(analysis_id),
                        analysis.json(),
                        ttl=self.TTL_SECONDS
                    )
                
                # Get demo results
                results = await demo_service.get_demo_result()
            else:
                # Live mode - would integrate with actual analysis engine
                # For now, simulate similar progress
                progress_stages = [
                    (10, "Cloning repository..."),
                    (25, "Parsing code structure..."),
                    (45, "Analyzing dependencies..."),
                    (65, "Calculating impact radius..."),
                    (85, "Generating recommendations..."),
                ]
                
                for progress_percent, message in progress_stages:
                    await self._update_progress(analysis_id, progress_percent, message)
                
                # TODO: Implement actual live analysis
                results = await demo_service.get_demo_result()
            
            # Mark as completed
            analysis.status = AnalysisStatus.COMPLETED
            analysis.progress_percent = 100
            analysis.current_step = "Analysis complete"
            analysis.completed_at = datetime.utcnow()
            analysis.updated_at = datetime.utcnow()
            
            await store.set(
                self._get_analysis_key(analysis_id),
                analysis.json(),
                ttl=self.TTL_SECONDS
            )
            
            # Store results
            await store.set(
                self._get_result_key(analysis_id),
                results.json(),
                ttl=self.TTL_SECONDS
            )
            
            # Update final progress
            final_progress = {
                "analysis_id": str(analysis_id),
                "status": AnalysisStatus.COMPLETED.value,
                "progress_percent": 100,
                "current_step": "Analysis complete",
                "message": "Analysis completed successfully",
                "estimated_time_remaining": 0
            }
            await store.set(
                self._get_progress_key(analysis_id),
                json.dumps(final_progress),
                ttl=self.TTL_SECONDS
            )
            
            logger.info(f"Analysis {analysis_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Analysis {analysis_id} failed: {e}")
            
            # Mark as failed
            try:
                analysis = await self.get_analysis(analysis_id)
                if analysis:
                    analysis.status = AnalysisStatus.FAILED
                    analysis.error_message = str(e)
                    analysis.updated_at = datetime.utcnow()
                    await store.set(
                        self._get_analysis_key(analysis_id),
                        analysis.json(),
                        ttl=self.TTL_SECONDS
                    )
                
                # Update progress with error
                error_progress = {
                    "analysis_id": str(analysis_id),
                    "status": AnalysisStatus.FAILED.value,
                    "progress_percent": analysis.progress_percent if analysis else 0,
                    "current_step": "Analysis failed",
                    "message": f"Error: {str(e)}",
                    "estimated_time_remaining": None
                }
                await store.set(
                    self._get_progress_key(analysis_id),
                    json.dumps(error_progress),
                    ttl=self.TTL_SECONDS
                )
            except Exception as inner_e:
                logger.error(f"Failed to update analysis failure status: {inner_e}")
    
    async def _update_progress(
        self,
        analysis_id: UUID,
        progress_percent: int,
        message: str
    ) -> None:
        """Update analysis progress.
        
        Args:
            analysis_id: Analysis UUID
            progress_percent: Current progress (0-100)
            message: Progress message
        """
        import asyncio
        
        store = await self._get_store()
        
        progress_data = {
            "analysis_id": str(analysis_id),
            "status": AnalysisStatus.RUNNING.value,
            "progress_percent": progress_percent,
            "current_step": message,
            "message": message,
            "estimated_time_remaining": (100 - progress_percent) * 3
        }
        
        await store.set(
            self._get_progress_key(analysis_id),
            json.dumps(progress_data),
            ttl=self.TTL_SECONDS
        )
        
        # Update analysis object
        analysis = await self.get_analysis(analysis_id)
        if analysis:
            analysis.progress_percent = progress_percent
            analysis.current_step = message
            analysis.updated_at = datetime.utcnow()
            await store.set(
                self._get_analysis_key(analysis_id),
                analysis.json(),
                ttl=self.TTL_SECONDS
            )
        
        # Simulate processing time
        await asyncio.sleep(0.5)


# Global analysis service instance
analysis_service = AnalysisService()
