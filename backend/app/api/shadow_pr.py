"""Shadow PR API endpoints."""

import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.schemas.shadow_pr import ShadowPRPreview
from app.services.shadow_pr_service import shadow_pr_service
from app.utils.errors import AnalysisNotFoundError, AnalysisValidationError

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/{analysis_id}/shadow-pr/preview", response_model=ShadowPRPreview)
async def generate_shadow_pr_preview(analysis_id: UUID):
    """Generate Shadow PR preview from analysis results.
    
    This endpoint creates a reviewable Shadow PR package without modifying
    the repository or creating actual GitHub PRs.
    
    Args:
        analysis_id: Analysis UUID
        
    Returns:
        Shadow PR preview with branch name, PR title, body, and files to create
        
    Raises:
        HTTPException: If analysis not found or not completed
    """
    logger.info(f"Generating Shadow PR preview for analysis {analysis_id}")
    
    try:
        preview = await shadow_pr_service.generate_shadow_pr_preview(analysis_id)
        logger.info(f"Shadow PR preview generated successfully for {analysis_id}")
        return preview
        
    except ValueError as e:
        error_msg = str(e)
        
        if "not found" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "ANALYSIS_NOT_FOUND",
                        "message": error_msg,
                    }
                }
            )
        elif "not completed" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "ANALYSIS_NOT_COMPLETED",
                        "message": error_msg,
                    }
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "SHADOW_PR_GENERATION_ERROR",
                        "message": error_msg,
                    }
                }
            )
    
    except Exception as e:
        logger.error(f"Failed to generate Shadow PR preview for {analysis_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": f"Failed to generate Shadow PR preview: {str(e)}",
                }
            }
        )

# Made with Bob
