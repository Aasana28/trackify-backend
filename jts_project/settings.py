# jts_project/settings.py

from decouple import config
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ─── Security ───────────────────────────────────────────────────────────────
SECRET_KEY    = config("SECRET_KEY", default="change-this-in-production")
DEBUG         = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = ["*"]

# ─── Installed Apps ─────────────────────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",

    # Our apps
    "apps.accounts",
    "apps.applications",
    "apps.reminders",
    "apps.braindump",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",          # Must be first
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "jts_project.urls"

TEMPLATES = [{
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
}]

WSGI_APPLICATION = "jts_project.wsgi.application"

# ─── Database (PostgreSQL) ──────────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE":   "django.db.backends.postgresql",
        "NAME":     config("DB_NAME",     default="jts_db"),
        "USER":     config("DB_USER",     default="postgres"),
        "PASSWORD": config("DB_PASSWORD", default=""),
        "HOST":     config("DB_HOST",     default="localhost"),
        "PORT":     config("DB_PORT",     default="5432"),
    }
}

# ─── Auth ───────────────────────────────────────────────────────────────────
AUTH_USER_MODEL = "accounts.User"
SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# ─── REST Framework ──────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

# ─── JWT Settings ────────────────────────────────────────────────────────────
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME":  timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS":  True,
    "AUTH_HEADER_TYPES":      ("Bearer",),
}

# ─── CORS ────────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = [
    config("FRONTEND_URL", default="http://localhost:3000"),
]
CORS_ALLOW_CREDENTIALS = True

# ─── Google OAuth ─────────────────────────────────────────────────────────────
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
        "APP": {
            "client_id": config("GOOGLE_CLIENT_ID",     default=""),
            "secret":    config("GOOGLE_CLIENT_SECRET", default=""),
            "key":       ""
        }
    }
}

ACCOUNT_EMAIL_REQUIRED        = True
ACCOUNT_USERNAME_REQUIRED     = False
ACCOUNT_AUTHENTICATION_METHOD = "email"
SOCIALACCOUNT_AUTO_SIGNUP     = True

# ─── Email ───────────────────────────────────────────────────────────────────
# Set EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend in .env for production.
EMAIL_BACKEND    = config("EMAIL_BACKEND",    default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST       = config("EMAIL_HOST",       default="smtp.gmail.com")
EMAIL_PORT       = config("EMAIL_PORT",       default=587, cast=int)
EMAIL_USE_TLS    = config("EMAIL_USE_TLS",    default=True,  cast=bool)
EMAIL_HOST_USER  = config("EMAIL_HOST_USER",  default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL  = config("DEFAULT_FROM_EMAIL",  default="Trackify <noreply@trackify.app>")

FRONTEND_URL = config("FRONTEND_URL", default="http://localhost:3000")

# ─── Static files ─────────────────────────────────────────────────────────────
STATIC_URL         = "/static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LANGUAGE_CODE = "en-us"
TIME_ZONE     = "Asia/Kolkata"
USE_I18N      = True
USE_TZ        = True

# ─── Anthropic AI ───────────────────────────────────────────────────────────────
GROQ_API_KEY = config("GROQ_API_KEY", default="")
