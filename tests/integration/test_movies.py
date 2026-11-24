import os

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.accounts.middleware import SESSION_GENERATION_KEY
from apps.catalogue.models import CatalogueItem, ItemKind, SourceProvider
from apps.core.policies import Visibility
from apps.integrations.adapters import Candidate
from apps.integrations.persistence import import_candidate
from apps.integrations.screen_metadata import enrich_movie
from apps.jobs.models import BackgroundJob
from apps.libraries.models import MovieAnnotation, SaveState
from apps.libraries.services import save_item
from apps.profiles.models import PageKey
from apps.profiles.services import create_profile


def fact(value):
    return {"rank": "normal", "mainsnak": {"datavalue": {"value": value}}}


def label(value):
    return {"lastrevid": 77, "labels": {"en": {"value": value}}}


@pytest.mark.django_db
def test_lok_021_film_metadata_from_typed_and_revisioned_claims(client):
    film = import_candidate(
        Candidate(
            SourceProvider.WIKIDATA,
            "wikidata",
            "Q42",
            ItemKind.MOVIE,
            "A historical film",
            1994,
            revision="77",
        )
    )
    assert BackgroundJob.objects.filter(
        kind="enrich-screen", object_id=film.pk
    ).exists()
    enrich_movie(
        film,
        "Q42",
        fetch_entities=lambda ids: {
            "Q42": {
                "lastrevid": 77,
                "claims": {
                    "P31": [fact({"id": "Q11424"}), fact({"id": "Q93204"})],
                    "P161": [fact({"id": "Q102"})],
                    "P57": [fact({"id": "Q99"})],
                    "P495": [fact({"id": "Q30"})],
                    "P577": [fact({"precision": 11, "time": "+1994-10-01T00:00:00Z"})],
                },
            }
        },
        get_labels=lambda ids: {
            "Q102": label("The actor"),
            "Q99": label("The director"),
            "Q30": label("United States"),
        },
    )
    result = client.get(reverse("catalogue:detail", args=[film.public_id]))
    for value in (b"The actor", b"The director", b"United States", b"1 October 1994"):
        assert value in result.content
    assert film.subtype == "documentary"
    assert "credits" in film.sources.get(revision="77").fields


@pytest.mark.django_db
def test_lok_021_filters_watched_and_stores_personal_film_notes(client):
    user = get_user_model().objects.create_user(
        email="reader@example.test", username="reader", email_verified=True
    )
    create_profile(user)
    client.force_login(user)
    session = client.session
    session[SESSION_GENERATION_KEY] = user.session_generation
    session.save()
    movie = CatalogueItem.objects.create(
        title="Film in the library", kind=ItemKind.MOVIE, is_public=True
    )
    other = CatalogueItem.objects.create(
        title="Another film", kind=ItemKind.MOVIE, is_public=True
    )
    saved = save_item(user, movie)
    save_item(user, other)
    assert (
        client.post(
            reverse("libraries:edit", args=[saved.public_id]),
            {
                "state": SaveState.WATCHED,
                "visibility": Visibility.PRIVATE,
                "movie-favourite_scene": "Personal reaction",
                "movie-favourite_performance": "A named performer",
            },
        ).status_code
        == 302
    )
    assert MovieAnnotation.objects.get().favourite_scene == "Personal reaction"
    results = client.get(
        reverse("profiles:page", args=[user.username, PageKey.MOVIES]),
        {"state": SaveState.WATCHED},
    )
    assert b"Film in the library" in results.content
    assert (
        b"Another film" not in results.content
        and b"Personal reaction" not in results.content
    )


@pytest.mark.django_db
@pytest.mark.skipif(
    os.environ.get("LOKAM_LIVE_TESTS") != "1", reason="Requires Wikidata"
)
def test_lok_021_live_film_credits():
    item = CatalogueItem.objects.create(
        title="The Shawshank Redemption", kind=ItemKind.MOVIE, is_public=True
    )
    enrich_movie(item, "Q172241")
    assert item.credits.filter(person__item__title="Frank Darabont").exists()
    assert item.movie.release_date.year == 1994
