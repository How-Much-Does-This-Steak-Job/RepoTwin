"""Custom exceptions for RepoTwin backend.

This module defines the error hierarchy for the RepoTwin analysis system,
providing specific exception types for different failure scenarios.
"""


class AnalysisError(Exception):
    """Base exception for all analysis-related errors.
    
    This is the root exception class for all RepoTwin analysis errors.
    All other analysis exceptions inherit from this class.
    
    Attributes:
        message: Human-readable error message
        details: Optional dictionary with additional error context
    """
    
    def __init__(self, message: str, details: dict | None = None):
        """Initialize the exception.
        
        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error context
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class AnalysisNotFoundError(AnalysisError):
    """Exception raised when an analysis is not found.
    
    This exception is raised when attempting to access an analysis
    that does not exist in the database or cache.
    
    Example:
        >>> raise AnalysisNotFoundError(
        ...     "Analysis not found",
        ...     {"analysis_id": "abc123"}
        ... )
    """
    
    def __init__(self, message: str = "Analysis not found", details: dict | None = None):
        """Initialize the exception.
        
        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error context
        """
        super().__init__(message, details)


class AnalysisTimeoutError(AnalysisError):
    """Exception raised when an analysis operation times out.
    
    This exception is raised when an analysis operation exceeds
    the maximum allowed execution time.
    
    Example:
        >>> raise AnalysisTimeoutError(
        ...     "Analysis timed out after 300 seconds",
        ...     {"timeout_seconds": 300, "analysis_id": "abc123"}
        ... )
    """
    
    def __init__(self, message: str = "Analysis operation timed out", details: dict | None = None):
        """Initialize the exception.
        
        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error context
        """
        super().__init__(message, details)


class AnalysisValidationError(AnalysisError):
    """Exception raised when analysis input validation fails.
    
    This exception is raised when the analysis request contains
    invalid parameters or fails schema validation.
    
    Example:
        >>> raise AnalysisValidationError(
        ...     "Invalid repository URL",
        ...     {"field": "repository_url", "value": "not-a-url"}
        ... )
    """
    
    def __init__(self, message: str = "Analysis validation failed", details: dict | None = None):
        """Initialize the exception.
        
        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error context
        """
        super().__init__(message, details)
