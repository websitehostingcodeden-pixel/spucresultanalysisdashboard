"""
Custom middleware to disable CSRF for API endpoints
"""

from django.middleware.csrf import CsrfViewMiddleware as DjangoCsrfViewMiddleware


class CsrfExemptMiddleware(DjangoCsrfViewMiddleware):
    """
    Custom CSRF middleware that exempts /api/ endpoints
    since they use JWT authentication instead of session cookies
    """
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Exempt /api/ paths from CSRF - they use JWT instead
        if request.path.startswith('/api/'):
            return None
        
        # Apply CSRF for non-API paths
        return super().process_view(request, view_func, view_args, view_kwargs)
