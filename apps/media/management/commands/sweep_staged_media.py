from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.media.models import AssetState, MediaAsset
from apps.media.services import request_deletion


class Command(BaseCommand):
    help = "Queue interrupted uploads older than one hour for private storage cleanup."

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(hours=1)
        abandoned = list(
            MediaAsset.objects.filter(
                state=AssetState.STAGING,
                updated_at__lt=cutoff,
            )
            .select_related("owner")
            .order_by("updated_at")[:50]
        )
        queued = sum(
            request_deletion(asset.pk, asset.owner, abandoned_before=cutoff)
            for asset in abandoned
        )
        self.stdout.write(f"Queued {queued} interrupted uploads for cleanup.")
