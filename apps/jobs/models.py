import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class BackgroundJob(models.Model):
    class State(models.TextChoices):
        READY = "ready"
        RUNNING = "running"
        SUCCEEDED = "succeeded"
        FAILED = "failed"
        CANCELLED = "cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kind = models.SlugField(max_length=48)
    object_id = models.PositiveBigIntegerField()
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    dedup_key = models.CharField(max_length=160, unique=True)
    state = models.CharField(max_length=12, choices=State.choices, default=State.READY)
    available_at = models.DateTimeField(default=timezone.now)
    lease_until = models.DateTimeField(null=True)
    lease_token = models.UUIDField(null=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    max_attempts = models.PositiveSmallIntegerField(default=4)
    timeout_seconds = models.PositiveSmallIntegerField(default=20)
    error_code = models.CharField(max_length=32, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["state", "available_at", "id"], name="jobs_due_idx"),
            models.Index(fields=["state", "lease_until", "id"], name="jobs_lease_idx"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    attempts__lte=models.F("max_attempts"), max_attempts__range=(1, 8)
                ),
                name="jobs_attempt_bounds",
            ),
            models.CheckConstraint(
                condition=models.Q(timeout_seconds__range=(1, 120)),
                name="jobs_timeout_bounds",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    state="running",
                    lease_token__isnull=False,
                    lease_until__isnull=False,
                )
                | models.Q(
                    state__in=["ready", "succeeded", "failed", "cancelled"],
                    lease_token__isnull=True,
                    lease_until__isnull=True,
                ),
                name="jobs_lease_consistency",
            ),
        ]
