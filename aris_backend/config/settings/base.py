from decouple import config
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Security
SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1").split(",")

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "apps.results",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Media files
MEDIA_ROOT = os.path.join(BASE_DIR, config("UPLOAD_DIR", default="uploads"))
MEDIA_URL = "/media/"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# REST Framework
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 100,
    # Disable CSRF for API - we use JWT for authentication
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
}

# JWT Authentication Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': config("ACCESS_TOKEN_LIFETIME", cast=int, default=60),  # minutes
    'REFRESH_TOKEN_LIFETIME': config("REFRESH_TOKEN_LIFETIME", cast=int, default=1440),  # minutes (1 day)
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# CORS (CORS Headers for Vite Frontend)
# Get from environment OR use sensible defaults
_env_cors = config("CORS_ALLOWED_ORIGINS", default="").strip()

if _env_cors and _env_cors != "":
    # Use environment variable if provided
    CORS_ALLOWED_ORIGINS = [origin.strip() for origin in _env_cors.split(",") if origin.strip()]
    print(f"CORS ORIGINS from ENV: {CORS_ALLOWED_ORIGINS}")
else:
    # Use safe defaults if not in environment
    CORS_ALLOWED_ORIGINS = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
        "https://spucresultanalysisdashboard.onrender.com",
        "https://spucresultanalysisdashboard.vercel.app",
    ]
    print(f"CORS ORIGINS from DEFAULTS: {CORS_ALLOWED_ORIGINS}")

# CORS regex for wildcard domains (Vercel preview deployments)
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.vercel\.app$",
    r"^https://.*\.vercelapp\.com$",
    r"^http://localhost",
    r"^http://127\.0\.0\.1",
]

# Production CORS settings
CORS_ALLOW_CREDENTIALS = True  # Allow cookies/auth headers
CORS_MAX_AGE = 3600  # Cache preflight for 1 hour
CORS_EXPOSE_HEADERS = [
    "Content-Type",
    "X-File-Size",
    "X-Response-Time-Ms",
    "X-CSRFToken",
]
CORS_ALLOW_HEADERS = [
    "Accept",
    "Accept-Language",
    "Content-Type",
    "Authorization",
    "X-Requested-With",
    "X-CSRFToken",
]
# For development: allow all origins
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True

# CSRF Trust
_default_csrf = [
    "https://spucresultanalysisdashboard.vercel.app",
    "https://spucresultanalysisdashboard.onrender.com",
    "http://localhost:5173",
    "http://localhost:8000",
]

_env_csrf = config("CSRF_TRUSTED_ORIGINS", default="")
if _env_csrf:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in _env_csrf.split(",")]
else:
    CSRF_TRUSTED_ORIGINS = _default_csrf

# File upload
MAX_FILE_SIZE = config("MAX_FILE_SIZE", cast=int, default=5242880)
DATA_UPLOAD_MAX_MEMORY_SIZE = MAX_FILE_SIZE
FILE_UPLOAD_MAX_MEMORY_SIZE = MAX_FILE_SIZE
