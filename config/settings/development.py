"""Loopback-oriented local defaults."""

from .base import *  # noqa: F403
from .base import required_setting

SECRET_KEY = required_setting("LOKAM_SECRET_KEY")
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
