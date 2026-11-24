"""Fail closed when production configuration is incomplete."""

from urllib.parse import urlsplit

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403
from .base import DATABASES, required_setting

SECRET_KEY = required_setting("LOKAM_SECRET_KEY")
ALLOWED_HOSTS = [
    host.strip()
    for host in required_setting("LOKAM_ALLOWED_HOSTS").split(",")
    if host.strip()
]
if not ALLOWED_HOSTS or any(
    "*" in host or host.startswith(".") for host in ALLOWED_HOSTS
):
    raise ImproperlyConfigured("LOKAM_ALLOWED_HOSTS must contain explicit hostnames.")

DATABASES["default"] = {
    **DATABASES["default"],
    "HOST": required_setting("LOKAM_DB_HOST"),
    "NAME": required_setting("LOKAM_DB_NAME"),
    "USER": required_setting("LOKAM_DB_USER"),
    "PASSWORD": required_setting("LOKAM_DB_PASSWORD"),
    "OPTIONS": {"connect_timeout": 5, "sslmode": "verify-full"},
}

LOKAM_PUBLIC_ORIGIN = required_setting("LOKAM_PUBLIC_ORIGIN").rstrip("/")
origin = urlsplit(LOKAM_PUBLIC_ORIGIN)
if (
    origin.scheme != "https"
    or origin.hostname not in ALLOWED_HOSTS
    or origin.username
    or origin.path
    or origin.query
    or origin.fragment
):
    raise ImproperlyConfigured("LOKAM_PUBLIC_ORIGIN must be an allowed HTTPS origin.")

SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31_536_000
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
