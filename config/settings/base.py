"""Shared environment-driven settings."""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parents[2]


def required_setting(name):
    value = os.environ.get(name)
    if not value:
        raise ImproperlyConfigured(f"{name} must be set.")
    return value


SECRET_KEY = os.environ.get("LOKAM_SECRET_KEY", "")
ALLOWED_HOSTS = []
DEBUG = False
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.accounts",
    "apps.jobs",
    "apps.profiles",
    "apps.catalogue",
    "apps.integrations",
    "apps.libraries",
    "apps.media",
]
LOKAM_JOB_HANDLERS = {
    "account-mail": "apps.accounts.services.send_account_mail",
    "process-media": "apps.media.services.process_media",
    "delete-media": "apps.media.services.delete_media",
    "enrich-book": "apps.integrations.book_editions.fetch_editions_job",
}
AUTH_USER_MODEL = "accounts.User"
AUTHENTICATION_BACKENDS = ["apps.accounts.backends.VerifiedEmailBackend"]
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 12},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
]
LOGIN_URL = "accounts:login"
LOKAM_PUBLIC_ORIGIN = os.environ.get(
    "LOKAM_PUBLIC_ORIGIN", "http://127.0.0.1:8000"
).rstrip("/")
SECURE_REFERRER_POLICY = "no-referrer"
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.accounts.middleware.enforce_session_generation",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("LOKAM_DB_NAME", "lokam"),
        "USER": os.environ.get("LOKAM_DB_USER", "lokam"),
        "PASSWORD": os.environ.get("LOKAM_DB_PASSWORD", ""),
        "HOST": os.environ.get("LOKAM_DB_HOST", "127.0.0.1"),
        "PORT": os.environ.get("LOKAM_DB_PORT", "5432"),
        "OPTIONS": {"connect_timeout": 5},
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LANGUAGE_CODE = "en"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    "private": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {"location": BASE_DIR / "media"},
    },
}
LOKAM_MEDIA_UPLOAD_BYTES = 8 * 1024 * 1024
LOKAM_MEDIA_USER_BYTES = 100 * 1024 * 1024
FILE_UPLOAD_HANDLERS = [
    "apps.media.uploads.LimitFileUploadHandler",
    "django.core.files.uploadhandler.MemoryFileUploadHandler",
    "django.core.files.uploadhandler.TemporaryFileUploadHandler",
]
DATA_UPLOAD_MAX_NUMBER_FILES = 8
