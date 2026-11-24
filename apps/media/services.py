from hashlib import sha256
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import storages
from django.db import transaction
from django.db.models import Sum

from apps.catalogue.models import SourceProvider
from apps.jobs.services import active_lease, enqueue

from .images import OUTPUT_BYTES, VARIANT_WIDTHS, InvalidImage, encode_variants
from .models import AssetState, CatalogueImage, MediaAsset


def private_storage():
    return storages["private"]


def _write(key, file):
    stored = private_storage().save(key, file)
    if stored != key:
        private_storage().delete(stored)
        raise OSError("Storage did not preserve the assigned object key.")


@transaction.atomic
def _reserve_upload(owner, description, size):
    get_user_model().objects.select_for_update().get(pk=owner.pk)
    used = MediaAsset.objects.filter(owner=owner).aggregate(
        total=Sum("reserved_bytes", default=0)
    )["total"]
    reservation = size + len(VARIANT_WIDTHS) * OUTPUT_BYTES
    if used + reservation > settings.LOKAM_MEDIA_USER_BYTES:
        raise ValidationError("This upload would exceed your image storage quota.")
    asset = MediaAsset(
        owner=owner,
        description=description,
        reserved_bytes=reservation,
        input_bytes=size,
    )
    asset.input_key = f"quarantine/{asset.public_id.hex}.bin"
    asset.save()
    return asset


def stage_upload(owner, upload, description):
    if not 0 < upload.size <= settings.LOKAM_MEDIA_UPLOAD_BYTES:
        raise ValidationError("Choose an image no larger than 8 MB.")
    asset = _reserve_upload(owner, description, upload.size)
    try:
        _write(asset.input_key, upload)
    except OSError as error:
        request_deletion(asset.pk, owner)
        raise ValidationError(
            "The image could not be uploaded. Try again later."
        ) from error
    with transaction.atomic():
        queued = MediaAsset.objects.filter(
            pk=asset.pk, state=AssetState.STAGING
        ).update(state=AssetState.QUEUED)
        if queued:
            enqueue("process-media", asset.pk, f"process-media:{asset.pk}", owner=owner)
    if not queued:
        private_storage().delete(asset.input_key)
        raise ValidationError("The upload expired. Try again.")
    asset.state = AssetState.QUEUED
    return asset


@transaction.atomic
def request_deletion(asset_id, owner, *, abandoned_before=None):
    assets = MediaAsset.objects.select_for_update().filter(pk=asset_id, owner=owner)
    if abandoned_before is not None:
        assets = assets.filter(
            state=AssetState.STAGING, updated_at__lt=abandoned_before
        )
    asset = assets.first()
    if asset is None:
        return False
    asset.state = AssetState.DELETING
    asset.save(update_fields=["state", "updated_at"])
    enqueue("delete-media", asset.pk, f"delete-media:{asset.pk}", owner=owner)
    return True


def _leased_asset(job):
    return MediaAsset.objects.filter(pk=job.object_id, owner_id=job.owner_id)


@transaction.atomic
def _register_variants(job, keys):
    asset = (
        _leased_asset(job).select_for_update().filter(state=AssetState.QUEUED).first()
    )
    if (
        asset is None
        or not active_lease(job.pk, job.lease_token).select_for_update().first()
    ):
        return False
    asset.pending_keys = sorted(set(asset.pending_keys) | set(keys))
    asset.save(update_fields=["pending_keys", "updated_at"])
    return True


@transaction.atomic
def _finish_processing(job, checksum, variants):
    asset = (
        _leased_asset(job).select_for_update().filter(state=AssetState.QUEUED).first()
    )
    if (
        asset is None
        or not active_lease(job.pk, job.lease_token).select_for_update().first()
    ):
        return False
    asset.state = AssetState.READY if variants else AssetState.FAILED
    asset.variants = variants
    asset.checksum = checksum
    asset.save(update_fields=["state", "variants", "checksum", "updated_at"])
    return True


def process_media(job):
    asset = _leased_asset(job).first()
    if asset is None:
        return
    if asset.state == AssetState.QUEUED:
        with private_storage().open(asset.input_key) as original:
            data = original.read(settings.LOKAM_MEDIA_UPLOAD_BYTES + 1)
        try:
            if len(data) != asset.input_bytes:
                raise InvalidImage("Upload size does not match.")
            renditions = encode_variants(data)
        except InvalidImage:
            _finish_processing(job, "", {})
        else:
            prefix = f"assets/{asset.public_id.hex}/{job.lease_token.hex}"
            keys = {name: f"{prefix}/{name}.webp" for name in renditions}
            if not _register_variants(job, keys.values()):
                return
            variants = {}
            for name, (body, width, height) in renditions.items():
                if not active_lease(job.pk, job.lease_token).exists():
                    break
                _write(keys[name], ContentFile(body))
                variants[name] = {
                    "key": keys[name],
                    "size": len(body),
                    "width": width,
                    "height": height,
                }
            if len(variants) != len(renditions) or not _finish_processing(
                job, sha256(data).hexdigest(), variants
            ):
                for variant in variants.values():
                    private_storage().delete(variant["key"])
                return
    _prune_inputs(job)


@transaction.atomic
def _prune_inputs(job):
    asset = (
        _leased_asset(job)
        .select_for_update()
        .filter(state__in=[AssetState.READY, AssetState.FAILED])
        .first()
    )
    if (
        asset is None
        or not active_lease(job.pk, job.lease_token).select_for_update().first()
    ):
        return
    keep = {variant["key"] for variant in asset.variants.values()}
    remove = set(asset.pending_keys) - keep
    if asset.input_key:
        remove.add(asset.input_key)
    for key in remove:
        private_storage().delete(key)
    asset.pending_keys = []
    asset.input_key = ""
    asset.reserved_bytes = sum(variant["size"] for variant in asset.variants.values())
    asset.save(
        update_fields=["pending_keys", "input_key", "reserved_bytes", "updated_at"]
    )


@transaction.atomic
def delete_media(job):
    asset = (
        _leased_asset(job).select_for_update().filter(state=AssetState.DELETING).first()
    )
    if (
        asset is None
        or not active_lease(job.pk, job.lease_token).select_for_update().first()
    ):
        return
    keys = set(asset.pending_keys) | {
        variant["key"] for variant in asset.variants.values()
    }
    if asset.input_key:
        keys.add(asset.input_key)
    for key in keys:
        private_storage().delete(key)
    asset.delete()


def record_catalogue_image(source, *, url, licence, credit, description):
    try:
        parts = urlsplit(url)
    except ValueError as error:
        raise ValidationError("Use a valid HTTPS image URL.") from error
    allowed = {
        SourceProvider.WIKIMEDIA: {"upload.wikimedia.org", "thumb.wikimedia.org"},
        SourceProvider.OPEN_LIBRARY: {"covers.openlibrary.org"},
    }
    if (
        parts.scheme != "https"
        or parts.hostname not in allowed.get(source.provider, ())
        or parts.username
        or parts.password
        or parts.query
        or not all([licence, credit, description])
        or "image" not in source.fields
        or not source.show_credit
        or source.item.owner_id
    ):
        raise ValidationError(
            "Record a permitted image host, source, licence, credit and description."
        )
    image, _ = CatalogueImage.objects.get_or_create(
        source=source,
        url=url,
        defaults={
            "licence": licence,
            "credit": credit,
            "description": description,
            "can_display": True,
        },
    )
    return image
