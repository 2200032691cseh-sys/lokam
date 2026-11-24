import os
from io import BytesIO

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import Client
from django.urls import reverse
from PIL import Image

from apps.accounts.middleware import SESSION_GENERATION_KEY
from apps.catalogue.models import CatalogueItem, ItemKind, SourceProvider
from apps.catalogue.services import record_source
from apps.integrations.commons_images import import_commons_image
from apps.jobs.services import claim, finish
from apps.media.models import AssetState, MediaAsset
from apps.media.services import private_storage, record_catalogue_image


@pytest.fixture
def isolated_storage(settings, tmp_path):
    settings.STORAGES = {
        **settings.STORAGES,
        "private": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {"location": tmp_path},
        },
    }


def member(username):
    user = get_user_model().objects.create_user(
        email=f"{username}@example.test", username=username, email_verified=True
    )
    client = Client()
    client.force_login(user)
    session = client.session
    session[SESSION_GENERATION_KEY] = user.session_generation
    session.save()
    return client


def run_media_job():
    job = claim()
    call_command("execute_job", str(job.pk), str(job.lease_token))
    assert finish(job)


def sample_photo():
    buf = BytesIO()
    exif = Image.Exif()
    exif[270] = "Text that must not be copied."
    Image.new("RGB", (1200, 600), "navy").save(buf, "JPEG", exif=exif)
    return SimpleUploadedFile("sample.jpg", buf.getvalue(), content_type="image/jpeg")


@pytest.mark.django_db
def test_lok_018_image_is_private_sanitized_and_deletable(isolated_storage):
    owner = member("owner")
    stranger = member("stranger")
    assert (
        owner.post(
            reverse("media:index"),
            {"image": sample_photo(), "description": "Blue square"},
        ).status_code
        == 302
    )
    asset = MediaAsset.objects.get()
    input_key = asset.input_key
    url = reverse("media:image", args=[asset.public_id, "small"])
    assert owner.get(url).status_code == 404
    run_media_job()
    asset.refresh_from_db()
    assert asset.state == AssetState.READY
    assert not private_storage().exists(input_key)
    assert stranger.get(url).status_code == 404
    response = owner.get(url)
    assert response.status_code == 200
    assert "no-store" in response.headers["Cache-Control"]
    with Image.open(BytesIO(b"".join(response.streaming_content))) as image:
        assert image.size == (480, 240)
        assert not image.getexif()
    keys = [variant["key"] for variant in asset.variants.values()]
    assert (
        owner.post(reverse("media:delete", args=[asset.public_id])).status_code == 302
    )
    assert owner.get(url).status_code == 404
    run_media_job()
    assert not MediaAsset.objects.exists()
    assert not any(private_storage().exists(key) for key in keys)


@pytest.mark.django_db
def test_lok_018_invalid_file_and_quota_are_safe(isolated_storage, settings):
    owner = member("owner")
    path = reverse("media:index")
    payload = {
        "image": SimpleUploadedFile("sample.png", b"<svg></svg>"),
        "description": "Invalid example",
    }
    assert owner.post(path, payload).status_code == 302
    run_media_job()
    asset = MediaAsset.objects.get()
    assert asset.state == AssetState.FAILED and asset.reserved_bytes == 0
    settings.LOKAM_MEDIA_USER_BYTES = 100
    assert (
        b"storage quota"
        in owner.post(
            path, {"image": sample_photo(), "description": "Too large"}
        ).content
    )
    assert MediaAsset.objects.count() == 1


@pytest.mark.django_db
def test_lok_018_catalogue_artwork_requires_licence_and_allowed_host(client):
    book = CatalogueItem.objects.create(
        title="A book", kind=ItemKind.BOOK, is_public=True
    )
    source = record_source(
        book,
        provider=SourceProvider.WIKIMEDIA,
        reference="cover",
        revision="1",
        url="https://commons.wikimedia.org/wiki/File:Cover.jpg",
        fields={"image"},
        licence="CC BY 4.0",
        show_credit=True,
    )
    attributes = {
        "licence": "CC BY 4.0",
        "credit": "An artist",
        "description": "Book cover",
    }
    with pytest.raises(ValidationError):
        record_catalogue_image(
            source, url="https://example.test/private.png", **attributes
        )
    record_catalogue_image(
        source, url="https://upload.wikimedia.org/example-cover.jpg", **attributes
    )
    assert b"An artist" in client.get(reverse("catalogue:credits")).content


@pytest.mark.django_db
@pytest.mark.skipif(
    os.environ.get("LOKAM_LIVE_TESTS") != "1", reason="Requires Wikimedia Commons"
)
def test_lok_018_live_commons_lookup_preserves_attribution(client):
    person = CatalogueItem.objects.create(
        title="Jane Austen", kind=ItemKind.PERSON, is_public=True
    )
    image = import_commons_image(
        person, "File:Jane Austen.jpg", "An engraved portrait of Jane Austen"
    )
    assert image.credit and image.licence_url
    response = client.get(reverse("catalogue:detail", args=[person.public_id]))
    assert b"An engraved portrait of Jane Austen" in response.content
