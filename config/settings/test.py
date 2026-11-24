"""Test settings with isolated email and an ephemeral signing key."""

from django.core.management.utils import get_random_secret_key

from .base import *  # noqa: F403

SECRET_KEY = get_random_secret_key()
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
