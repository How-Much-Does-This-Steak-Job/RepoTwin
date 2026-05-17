"""Analysis API endpoints."""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, WebSocket, status
from pydantic import BaseModel

from app.schemas.analysis import (
    Analysis,
    AnalysisCreate,
    AnalysisList,
    AnalysisProgress,
    AnalysisResults,
    AnalysisStatus,
)
from app.services.analysis_service import analysis_service
from app.utils.errors import AnalysisNotFoundError, AnalysisValidationError

logger = logging.getLogger(__name__)
router = APIRouter()
simple_router = APIRouter()  # Separate router for simple /analyze endpoint


class SimpleAnalyzeRequest(BaseModel):
    """Simplified analyze request for AGENTS.md compliance."""
    repositoryName: str
    changeRequest: str
    mode: str = "demo"


class SimpleAnalyzeResponse(BaseModel):
    """Simplified analyze response."""
    analysisId: str
    status: str
    message: str


@simple_router.post("/analyze", response_model=SimpleAnalyzeResponse, status_code=status.HTTP_201_CREATED)
async def simple_analyze(
    request: SimpleAnalyzeRequest,
    background_tasks: BackgroundTasks,
):
    """Simplified analyze endpoint for AGENTS.md compliance.
    
    This endpoint provides a simpler interface that matches the AGENTS.md specification:
    POST /api/analyze with { repositoryName, changeRequest, mode }
    
    Args:
        request: Simple analyze request
        background_tasks: FastAPI background tasks
        
    Returns:
        Simple response with analysisId and status
    """
    logger.info(f"Simple analyze request for repo {request.repositoryName}: {request.changeRequest}")
    
    try:
        # For demo mode, return a demo analysis ID immediately
        if request.mode == "demo":
            # Use a deterministic ID for demo mode
            demo_id = "demo-unimarket-reservations-001"
            
            return SimpleAnalyzeResponse(
                analysisId=demo_id,
                status="completed",
                message=f"Demo analysis ready for {request.repositoryName}"
            )
        
        # For live mode, create a real analysis job
        # Note: This requires a repo_id, which we don't have in the simple request
        # For now, we'll return a placeholder response
        logger.warning("Live mode not fully implemented in simple analyze endpoint")
        
        return SimpleAnalyzeResponse(
            analysisId="live-analysis-placeholder",
            status="processing",
            message="Live analysis mode requires repository connection"
        )
        
    except Exception as e:
        logger.error(f"Failed to process simple analyze request: {e}")
        raise AnalysisValidationError(f"Failed to analyze: {str(e)}")

@simple_router.get("/demo/{demo_id}/results", response_model=AnalysisResults)
async def get_demo_results(demo_id: str):
    """Get demo analysis results by demo ID.
    
    This endpoint handles demo IDs like 'demo-unimarket-reservations-001'
    returned by the simple /api/analyze endpoint in demo mode.
    
    Args:
        demo_id: Demo analysis ID (string, not UUID)
        
    Returns:
        Demo Shadow PR results from sample data
    """
    logger.info(f"Getting demo results for {demo_id}")
    
    try:
        from app.services.demo_service import demo_service
        
        # Load and return demo results
        results = await demo_service.get_demo_result()
        return results
        
    except Exception as e:
        logger.error(f"Failed to get demo results for {demo_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "DEMO_RESULTS_ERROR",
                    "message": f"Failed to load demo results: {str(e)}",
                }
            }
        )


@router.post("", response_model=Analysis, status_code=status.HTTP_201_CREATED)
async def create_analysis(
    data: AnalysisCreate,
    background_tasks: BackgroundTasks,
):
    """Create a new analysis job.
    
    Args:
        data: Analysis creation data
        background_tasks: FastAPI background tasks
        
    Returns:
        Created analysis
    """
    logger.info(f"Creating analysis for repo {data.repo_id}")
    
    try:
        # Create analysis job
        analysis = await analysis_service.create_analysis(data)
        
        # Start background analysis
        background_tasks.add_task(
            analysis_service.run_analysis,
            analysis.id,
            "live",
        )
        
        logger.info(f"Analysis {analysis.id} created and queued")
        return analysis
        
    except Exception as e:
        logger.error(f"Failed to create analysis: {e}")
        raise AnalysisValidationError(f"Failed to create analysis: {str(e)}")


@router.get("", response_model=AnalysisList)
async def list_analyses(
    repo_id: Optional[UUID] = Query(None),
    status: Optional[AnalysisStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """List analyses with optional filtering.
    
    Args:
        repo_id: Filter by repository
        status: Filter by status
        skip: Number of records to skip
        limit: Maximum number of records
        
    Returns:
        List of analyses
    """
    logger.debug(f"Listing analyses: repo_id={repo_id}, status={status}, skip={skip}, limit={limit}")
    
    try:
        analyses = await analysis_service.list_analyses(
            repo_id=repo_id,
            status=status,
            skip=skip,
            limit=limit,
        )
        
        return AnalysisList(
            items=analyses,
            total=len(analyses),
            skip=skip,
            limit=limit,
        )
        
    except Exception as e:
        logger.error(f"Failed to list analyses: {e}")
        raise AnalysisValidationError(f"Failed to list analyses: {str(e)}")


@router.get("/{analysis_id}", response_model=Analysis)
async def get_analysis(analysis_id: UUID):
    """Get analysis by ID.
    
    Args:
        analysis_id: Analysis UUID
        
    Returns:
        Analysis details
    """
    logger.debug(f"Getting analysis {analysis_id}")
    
    try:
        analysis = await analysis_service.get_analysis(analysis_id)
        
        if not analysis:
            raise AnalysisNotFoundError(f"Analysis {analysis_id} not found")
        
        return analysis
        
    except AnalysisNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to get analysis {analysis_id}: {e}")
        raise AnalysisValidationError(f"Failed to get analysis: {str(e)}")


@router.get("/{analysis_id}/progress", response_model=AnalysisProgress)
async def get_analysis_progress(analysis_id: UUID):
    """Get analysis progress.
    
    Args:
        analysis_id: Analysis UUID
        
    Returns:
        Analysis progress
    """
    logger.debug(f"Getting progress for analysis {analysis_id}")
    
    try:
        progress = await analysis_service.get_analysis_progress(analysis_id)
        
        if not progress:
            raise AnalysisNotFoundError(f"Analysis {analysis_id} not found")
        
        return progress
        
    except AnalysisNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to get progress for {analysis_id}: {e}")
        raise AnalysisValidationError(f"Failed to get progress: {str(e)}")


@router.get("/{analysis_id}/results", response_model=AnalysisResults)
async def get_analysis_results(analysis_id: UUID):
    """Get analysis results.
    
    Args:
        analysis_id: Analysis UUID
        
    Returns:
        Analysis results (Shadow PR)
        
    Raises:
        HTTPException: If analysis not found or not completed
    """
    logger.debug(f"Getting results for analysis {analysis_id}")
    
    try:
        # First check if analysis exists and is completed
        analysis = await analysis_service.get_analysis(analysis_id)
        
        if not analysis:
            raise AnalysisNotFoundError(f"Analysis {analysis_id} not found")
        
        if analysis.status != AnalysisStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "ANALYSIS_NOT_COMPLETED",
                        "message": f"Analysis is not completed yet. Current status: {analysis.status}",
                    }
                }
            )
        
        results = await analysis_service.get_analysis_results(analysis_id)
        
        if not results:
            raise AnalysisNotFoundError(f"Results for analysis {analysis_id} not found")
        
        return results
        
    except AnalysisNotFoundError:
        raise
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get results for {analysis_id}: {e}")
        raise AnalysisValidationError(f"Failed to get results: {str(e)}")


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analysis(analysis_id: UUID):
    """Delete analysis.
    
    Args:
        analysis_id: Analysis UUID
    """
    logger.info(f"Deleting analysis {analysis_id}")
    
    try:
        # Check if analysis exists
        analysis = await analysis_service.get_analysis(analysis_id)
        
        if not analysis:
            raise AnalysisNotFoundError(f"Analysis {analysis_id} not found")
        
        # Delete analysis
        await analysis_service.delete_analysis(analysis_id)
        logger.info(f"Analysis {analysis_id} deleted successfully")
        
    except AnalysisNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to delete analysis {analysis_id}: {e}")
        raise AnalysisValidationError(f"Failed to delete analysis: {str(e)}")


@router.websocket("/{analysis_id}/ws")
async def analysis_websocket(websocket: WebSocket, analysis_id: UUID):
    """WebSocket for real-time analysis updates.
    
    Args:
        websocket: WebSocket connection
        analysis_id: Analysis UUID
    """
    await websocket.accept()
    logger.info(f"WebSocket connection opened for analysis {analysis_id}")
    
    try:
        # Send initial progress
        progress = await analysis_service.get_analysis_progress(analysis_id)
        
        if progress:
            await websocket.send_json({
                "type": "progress",
                "data": progress.model_dump(),
            })
        
        # Keep connection open and poll for updates
        import asyncio
        
        while True:
            await asyncio.sleep(1)  # Poll every second
            
            try:
                # Get updated progress
                new_progress = await analysis_service.get_analysis_progress(analysis_id)
                
                if new_progress:
                    await websocket.send_json({
                        "type": "progress",
                        "data": new_progress.model_dump(),
                    })
                    
                    # Close connection if analysis is completed or failed
                    if new_progress.status in ["completed", "failed"]:
                        await websocket.send_json({
                            "type": new_progress.status,
                            "data": {"analysis_id": str(analysis_id)},
                        })
                        break
                        
            except Exception as e:
                logger.error(f"Error polling progress for {analysis_id}: {e}")
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": str(e)},
                })
                break
        
        await websocket.close()
        logger.info(f"WebSocket connection closed for analysis {analysis_id}")
        
    except Exception as e:
        logger.error(f"WebSocket error for analysis {analysis_id}: {e}")
        await websocket.close()

# Made with Bob
