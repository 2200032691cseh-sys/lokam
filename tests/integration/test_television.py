import os

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.accounts.middleware import SESSION_GENERATION_KEY
from apps.catalogue.identifiers import Namespace
from apps.catalogue.models import CatalogueItem, ItemKind, TVEpisode
from apps.core.policies import Visibility
from apps.integrations.tvmaze import enrich_season, enrich_show
from apps.libraries.models import SaveState, TVAnnotation
from apps.libraries.services import save_item


def _entity(ids):
    return {
        "Q1079": {
            "claims": {
                "P8600": [
                    {"rank": "normal", "mainsnak": {"datavalue": {"value": value}}}
                    for value in ids
                ]
            }
        }
    }


def _show_fixture(provider, path, *, params, headers):
    assert provider == "tvmaze" and path == "/shows/169"
    assert params["embed[]"] == ["seasons", "cast"]
    return {
        "id": 169,
        "language": "English",
        "premiered": "2008-01-20",
        "genres": ["Drama"],
        "_embedded": {
            "seasons": [{"id": 42, "number": 1, "premiereDate": "2008-01-20"}],
            "cast": [
                {
                    "person": {"id": 99, "name": "A lead actor"},
                    "character": {"id": 101, "name": "The main character"},
                }
            ],
        },
    }


def _episode_fixture(provider, path, *, headers, expected):
    assert provider == "tvmaze" and path == "/seasons/42/episodes" and expected is list
    return [
        {
            "id": 555,
            "name": "Opening episode",
            "airdate": "2008-01-20",
            "season": 1,
            "number": 1,
        },
        {"id": 556, "name": "Wrong season", "season": 2, "number": 1},
    ]


@pytest.mark.django_db
def test_lok_022_show_metadata_and_personal_episode_favourites(client):
    item = CatalogueItem.objects.create(
        kind=ItemKind.SHOW, title="A television series", is_public=True
    )
    assert (
        enrich_show(
            item,
            "Q1079",
            fetch_entities=lambda _: _entity(["169", "170"]),
            fetch=_show_fixture,
        )
        is None
    )
    show = enrich_show(
        item, "Q1079", fetch_entities=lambda _: _entity(["169"]), fetch=_show_fixture
    )
    season = show.seasons.get()
    enrich_season(season, "42", fetch=_episode_fixture)
    enrich_season(season, "42", fetch=_episode_fixture)
    episode = TVEpisode.objects.get()
    assert (
        episode.item.external_ids.get(namespace=Namespace.TVMAZE_EPISODE).value == "555"
    )
    show_detail = client.get(reverse("catalogue:detail", args=[item.public_id]))
    assert (
        b"The main character" in show_detail.content
        and b"TVmaze" in show_detail.content
    )
    show_season = client.get(reverse("catalogue:detail", args=[season.item.public_id]))
    assert (
        b"Opening episode" in show_season.content
        and b"Wrong season" not in show_season.content
    )

    owner = get_user_model().objects.create_user(
        email="reader@example.test", username="reader", email_verified=True
    )
    client.force_login(owner)
    session = client.session
    session[SESSION_GENERATION_KEY] = owner.session_generation
    session.save()
    saved = save_item(owner, item)
    response = client.post(
        reverse("libraries:edit", args=[saved.public_id]),
        {
            "state": SaveState.WATCHED,
            "visibility": Visibility.PRIVATE,
            "tv-favourite_episodes": [episode.pk],
            "tv-favourite_seasons": [season.pk],
            "tv-favourite_relationships": "My favourite relationship",
        },
    )
    assert response.status_code == 302
    annotation = TVAnnotation.objects.get(saved_item=saved)
    assert list(annotation.favourite_episodes.all()) == [episode]
    assert list(annotation.favourite_seasons.all()) == [season]
    episode_saved = save_item(owner, episode.item)
    form = client.get(
        reverse("libraries:edit", args=[episode_saved.public_id])
    ).context["form"]
    assert SaveState.WATCHED not in {value for value, _ in form.fields["state"].choices}


@pytest.mark.django_db
@pytest.mark.skipif(
    os.environ.get("LOKAM_LIVE_TESTS") != "1", reason="Requires Wikidata and TVmaze"
)
def test_lok_022_live_exact_tvmaze_seasons_and_episodes():
    item = CatalogueItem.objects.create(
        kind=ItemKind.SHOW, title="Breaking Bad", is_public=True
    )
    show = enrich_show(item, "Q1079")
    season = show.seasons.get(number=1)
    season_id = season.item.external_ids.get(namespace=Namespace.TVMAZE_SEASON).value
    enrich_season(season, season_id)
    assert season.episodes.filter(number=1).exists()
