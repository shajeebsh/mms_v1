import os
import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ["127.0.0.1", "localhost"]),
    CSRF_TRUSTED_ORIGINS=(list, []),
)

# Read environment variables from .env file if it exists
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
SECRET_KEY = env("DJANGO_SECRET_KEY", default="replace-me-for-production-dev-only")

# DEBUG should be False in production
DEBUG = env("DEBUG")

# ALLOWED_HOSTS
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

# CSRF Trusted Origins for Cloud Run URL
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS")

# Base URL for Wagtail admin (used in notification emails)
WAGTAILADMIN_BASE_URL = env("WAGTAILADMIN_BASE_URL", default="http://127.0.0.1:8000")

# Site name for Wagtail admin
WAGTAIL_SITE_NAME = "MMS Site"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "modelcluster",
    "taggit",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "wagtail_modeladmin",
    "wagtail.contrib.settings",
    "home",
    "membership",
    "finance",
    "education",
    "assets",
    "operations",
    "hr",
    "committee",
    "accounting",
    "billing",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # For static files
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

ROOT_URLCONF = "mms_site.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "mms_site.wsgi.application"

# Database
# Use DATABASE_URL environment variable (e.g. postgres://user:password@host:port/dbname)
# Default to local sqlite for development

DATABASES = {
    # Ensure DATABASE_URL is set in .env to a PostgreSQL connection
    # e.g., postgres://user:password@localhost:5432/mms_v1
    "local-dev": env.db("DATABASE_URL"), 
    "remote-dev1": env.db(
        "REMOTE_DEV1_URL",
        default="postgresql://neondb_owner:npg_8armhCE2voTt@ep-lively-sound-ahzl5trp-pooler.c-3.us-east-1.aws.neon.tech/mmsv1db?sslmode=require&channel_binding=require"
    ),
    # MySQL database configuration
    # e.g., mysql://user:password@localhost:3306/mms_v1
    "mysql-dev": env.db("MYSQL_DB_URL", default=""),
}

# Set default database based on environment variable (default to local-dev)
selected_db = env("SELECTED_DATABASE", default="local-dev")
DATABASES["default"] = DATABASES.get(selected_db, DATABASES["local-dev"])

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Use a simple staticfiles storage locally (WhiteNoise in production)
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

LOGIN_URL = "/cms/login/"
LOGIN_REDIRECT_URL = "/cms/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Wagtail reference indexing can cause crashes in some environments with django-tasks
WAGTAIL_ENABLE_UPDATE_REFERENCE_INDEX = False

# django-tasks configuration to avoid hangs with Wagtail signal handlers
DJANGO_TASKS = {
    "default": {
        "BACKEND": "django_tasks.backends.dummy.DummyBackend",
    }
}
