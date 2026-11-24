from django.db import models
from django.utils import timezone


class ProviderSyncState(models.Model):
    provider = models.CharField(max_length=16, primary_key=True)
    next_request_at = models.DateTimeField(default=timezone.now)
    blocked_until = models.DateTimeField(null=True, blank=True)
    consecutive_failures = models.PositiveSmallIntegerField(default=0)
