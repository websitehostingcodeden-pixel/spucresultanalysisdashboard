from .base import *
import os

DEBUG = False

ALLOWED_HOSTS = [
    'spucresultanalysisdashboard.onrender.com',
    'localhost',
    '127.0.0.1',
]

extra_hosts = os.getenv('EXTRA_ALLOWED_HOSTS', '')
if extra_hosts:
    ALLOWED_HOSTS.extend([h.strip() for h in extra_hosts.split(',') if h.strip()])

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
