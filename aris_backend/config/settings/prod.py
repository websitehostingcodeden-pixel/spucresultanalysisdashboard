from .base import *
import os

DEBUG = False

# Add Render domain to allowed hosts
ALLOWED_HOSTS = [
    'spucresultanalysisdashboard.onrender.com',
    'localhost',
    '127.0.0.1',
]

# Allow additional hosts from environment variable
additional_hosts = os.getenv('ALLOWED_HOSTS', '')
if additional_hosts:
    ALLOWED_HOSTS.extend([host.strip() for host in additional_hosts.split(',')])

# Security settings for production
# Trust X-Forwarded-Proto header from Render's proxy
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False  # Let Render's proxy handle the redirect

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
}
