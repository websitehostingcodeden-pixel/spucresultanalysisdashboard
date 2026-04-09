"""
API Utilities: Performance tracking, error handling, and decorators
"""

import time
from functools import wraps
from datetime import datetime
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status


class APIError(Exception):
    """Base API error with code and details"""
    
    def __init__(self, message, code="UNKNOWN_ERROR", status_code=status.HTTP_400_BAD_REQUEST, details=None):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class INVALID_FILE(APIError):
    def __init__(self, details=None):
        super().__init__(
            message="File is invalid or corrupted",
            code="INVALID_FILE",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class MISSING_SHEET(APIError):
    def __init__(self, sheet_name, details=None):
        super().__init__(
            message=f"Required sheet '{sheet_name}' not found in Excel file",
            code="MISSING_SHEET",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class ANALYTICS_NOT_FOUND(APIError):
    def __init__(self, upload_id, details=None):
        super().__init__(
            message=f"Analytics snapshot not found for upload {upload_id}",
            code="ANALYTICS_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )


class EXPORT_FAILED(APIError):
    def __init__(self, reason, details=None):
        super().__init__(
            message=f"Excel export failed: {reason}",
            code="EXPORT_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class UPLOAD_NOT_FOUND(APIError):
    def __init__(self, upload_id, details=None):
        super().__init__(
            message=f"Upload {upload_id} not found",
            code="UPLOAD_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )


def track_performance(view_func):
    """
    Decorator to track API response time and log performance metrics
    
    Adds to response:
    - response_time_ms: milliseconds taken
    - tracked_at: timestamp
    """
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        # Call the view
        response = view_func(*args, **kwargs)
        
        # Calculate performance
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        # Inject performance data into response
        if isinstance(response, Response) and isinstance(response.data, dict):
            response.data["_performance"] = {
                "response_time_ms": elapsed_ms,
                "tracked_at": datetime.now().isoformat()
            }
        
        return response
    
    return wrapper


def get_version_info(upload_log=None, analytics_snapshot=None):
    """
    Build standard version info for responses
    
    Returns dict with:
    - data_version: e.g., "v1.0"  
    - processing_version: e.g., "cleaner_v1"
    - analytics_version: e.g., "analytics_v1"
    - api_version: "1.0"
    """
    versions = {
        "api_version": "1.0"
    }
    
    if upload_log:
        versions["data_version"] = upload_log.data_version or "v1.0"
        versions["processing_version"] = upload_log.processing_version or "cleaner_v1"
    
    if analytics_snapshot:
        versions["analytics_version"] = analytics_snapshot.analytics_version or "analytics_v1"
    
    return versions


def get_cache_info(was_cached, response_time_ms, snapshot=None, cached_at=None, expires_at=None):
    """
    Build standard cache info for responses
    
    Returns dict with cache metadata
    """
    cache_info = {
        "was_cached": was_cached,
        "response_time_ms": response_time_ms,
    }
    
    if snapshot:
        cache_info["snapshot_id"] = snapshot.id
    
    if cached_at:
        cache_info["cached_at"] = cached_at.isoformat() if hasattr(cached_at, 'isoformat') else str(cached_at)
    
    if expires_at:
        cache_info["expires_at"] = expires_at.isoformat() if hasattr(expires_at, 'isoformat') else str(expires_at)
    
    return cache_info


def build_error_response(error):
    """
    Convert APIError to Response object
    """
    if isinstance(error, APIError):
        return Response(
            {
                "status": "error",
                "message": error.message,
                "code": error.code,
                "details": error.details
            },
            status=error.status_code
        )
    else:
        return Response(
            {
                "status": "error",
                "message": str(error),
                "code": "INTERNAL_SERVER_ERROR",
                "details": {}
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def safe_snapshot_fetch(upload_id, scope="UPLOAD", scope_value=None):
    """
    Safely fetch an analytics snapshot
    
    Returns: (snapshot, error) tuple
    - snapshot: AnalyticsSnapshot or None
    - error: APIError or None
    """
    from apps.results.models import AnalyticsSnapshot
    
    try:
        # Build query
        query = {"upload_log_id": upload_id, "scope": scope}
        if scope_value:
            query["scope_value"] = scope_value
        
        snapshot = AnalyticsSnapshot.objects.get(**query)
        
        # Check expiration
        if snapshot.is_expired():
            return None, ANALYTICS_NOT_FOUND(upload_id, details={"reason": "Snapshot expired"})
        
        # Check validity
        if not snapshot.is_valid:
            return None, ANALYTICS_NOT_FOUND(upload_id, details={"reason": "Snapshot invalid", "errors": snapshot.validation_errors})
        
        return snapshot, None
        
    except AnalyticsSnapshot.DoesNotExist:
        return None, ANALYTICS_NOT_FOUND(upload_id)
    except Exception as e:
        return None, APIError(str(e), code="SNAPSHOT_FETCH_ERROR", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
