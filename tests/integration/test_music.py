import os
from time import sleep

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.accounts.middleware import SESSION_GENERATION_KEY
from apps.catalogue.models import CatalogueItem, ItemKind
from apps.core.policies import Visibility
from apps.integrations.adapters import search_external
from apps.integrations.musicbrainz import enrich_music
from apps.integrations.persistence import import_candidate
from apps.libraries.models import MusicAnnotation, SaveState
from apps.libraries.services import save_item
from apps.profiles.models import PageKey
from apps.profiles.services import create_profile

RECORDING_ID = "fea6b48d-ca23-4b8c-94da-b92f318cde22"
WORK_ID = "a16a3079-29e6-434a-a6b2-8c6ebc07bb3b"
ARTIST_ID = "0f69abc4-e539-4a84-bf1c-d285c995906b"


@pytest.mark.django_db
def test_lok_023_recording_and_work_stay_distinct(client):
    def search(provider, path, *, params, headers):
        assert provider == "musicbrainz" and path == "/ws/2/recording"
        return {"recordings": [{"id": RECORDING_ID, "title": "Studio performance"}]}

    (candidate,) = search_external(
        ItemKind.MUSIC_RECORDING, "Studio performance", fetch=search
    )
    recording = import_candidate(candidate)

    def details(provider, path, *, params, headers):
        assert path.endswith(RECORDING_ID)
        return {
            "id": RECORDING_ID,
            "title": "Studio performance",
            "length": 130000,
            "artist-credit": [{"artist": {"id": ARTIST_ID, "name": "A performer"}}],
            "relations": [
                {
                    "type": "performance",
                    "work": {"id": WORK_ID, "title": "The composition"},
                },
                {
                    "url": {
                        "resource": "https://open.spotify.com/track/example?si=tracking"
                    }
                },
                {"url": {"resource": "https://example.test/download"}},
            ],
        }

    enrich_music(recording, candidate.identifier, fetch=details)
    enrich_music(recording, candidate.identifier, fetch=details)
    recording.refresh_from_db()
    assert recording.music_recording.work.item.kind == ItemKind.MUSICAL_WORK
    assert recording.credits.get().person.item.title == "A performer"
    assert recording.music_links.get().url == "https://open.spotify.com/track/example"
    response = client.get(reverse("catalogue:detail", args=[recording.public_id]))
    assert b"The composition" in response.content and b"2:10" in response.content
    assert b"example.test/download" not in response.content


@pytest.mark.django_db
def test_lok_023_music_types_and_private_association(client):
    owner = get_user_model().objects.create_user(
        email="reader@example.test", username="reader", email_verified=True
    )
    create_profile(owner)
    client.force_login(owner)
    session = client.session
    session[SESSION_GENERATION_KEY] = owner.session_generation
    session.save()
    artist = CatalogueItem.objects.create(
        title="A saved artist", kind=ItemKind.MUSIC_ARTIST, is_public=True
    )
    album = CatalogueItem.objects.create(
        title="A saved album", kind=ItemKind.MUSIC_ALBUM, is_public=True
    )
    saved = save_item(owner, artist)
    save_item(owner, album)
    assert (
        client.post(
            reverse("libraries:edit", args=[saved.public_id]),
            {
                "state": SaveState.SAVED,
                "visibility": Visibility.PRIVATE,
                "music-mood": "Quiet evening",
            },
        ).status_code
        == 302
    )
    assert MusicAnnotation.objects.get(saved_item=saved).mood == "Quiet evening"
    result = client.get(
        reverse("profiles:page", args=[owner.username, PageKey.MUSIC]),
        {"music_kind": ItemKind.MUSIC_ARTIST},
    )
    assert (
        b"A saved artist" in result.content and b"A saved album" not in result.content
    )
    assert b"Quiet evening" not in result.content


@pytest.mark.django_db
@pytest.mark.skipif(
    os.environ.get("LOKAM_LIVE_TESTS") != "1", reason="Requires MusicBrainz"
)
def test_lok_023_live_musicbrainz_artist_search_and_enrichment():
    artist = next(
        match
        for match in search_external(ItemKind.MUSIC_ARTIST, "Nina Simone")
        if match.title == "Nina Simone"
    )
    item = import_candidate(artist)
    sleep(1)
    enrich_music(item, artist.identifier)
    item.refresh_from_db()
    assert item.music_artist.artist_type == "Person"
