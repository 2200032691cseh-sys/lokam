import uuid

from django.conf import settings
from django.db import models

from apps.catalogue.models import CatalogueSource

from .licences import COMMONS_LICENCE_LINKS


class AssetState(models.TextChoices):
    STAGING = "staging", "Receiving upload"
    QUEUED = "queued", "Waiting for processing"
    READY = "ready", "Ready"
    FAILED = "failed", "Image could not be processed"
    DELETING = "deleting", "Deleting"


class MediaAsset(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assets"
    )
    description = models.CharField(max_length=512)
    state = models.CharField(
        max_length=10, choices=AssetState.choices, default=AssetState.STAGING
    )
    reserved_bytes = models.PositiveBigIntegerField()
    input_bytes = models.PositiveIntegerField()
    input_key = models.CharField(max_length=120)
    pending_keys = models.JSONField(default=list)
    variants = models.JSONField(default=dict)
    checksum = models.CharField(max_length=64, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.description

    class Meta:
        indexes = [
            models.Index(fields=["state", "updated_at"], name="media_state_age_idx")
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(state__in=AssetState.values),
                name="media_known_state",
            ),
        ]


class CatalogueImage(models.Model):
    source = models.ForeignKey(
        CatalogueSource, on_delete=models.CASCADE, related_name="images"
    )
    url = models.URLField(max_length=500)
    licence = models.CharField(max_length=160)
    credit = models.CharField(max_length=240)
    description = models.CharField(max_length=512)
    can_display = models.BooleanField(default=False)

    @property
    def licence_url(self):
        return COMMONS_LICENCE_LINKS.get(self.licence)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["source", "url"], name="media_unique_source_image"
            ),
        ]
