from datetime import timedelta

import httpx
import pytest
from django.utils import timezone

from apps.catalogue.models import CatalogueItem, ItemKind
from apps.integrations.adapters import search_external
from apps.integrations.http import (
    ProviderCredentialsRequired,
    ProviderUnavailable,
    get_json,
)
from apps.integrations.models import ProviderSyncState
from apps.integrations.persistence import import_candidate


@pytest.mark.django_db
def test_lok_014_open_library_candidate_and_repeat_import():
    def fake_fetch(provider, path, *, params, headers):
        assert provider == "open-library" and path == "/search.json"
        assert params["title"] == "A Selected Book"
        return {
            "docs": [
                {
                    "key": "/works/OL100W",
                    "title": "A Selected Book",
                    "first_publish_year": 1874,
                    "author_name": ["An Author"],
                    "first_sentence": ["Unlicensed sample text"],
                },
                {"key": "/books/OL100M", "title": "Invalid work ID"},
            ]
        }

    (candidate,) = search_external(ItemKind.BOOK, "A Selected Book", fetch=fake_fetch)
    assert candidate.creators == ("An Author",)
    item = import_candidate(candidate)
    assert import_candidate(candidate) == item
    assert CatalogueItem.objects.count() == 1
    assert item.description == ""
    assert item.sources.get().fields == ["identifiers", "title", "year"]


def test_lok_014_tmdb_is_optional_until_credentials_exist(settings):
    settings.LOKAM_TMDB_TOKEN = ""
    with pytest.raises(ProviderCredentialsRequired):
        search_external(ItemKind.MOVIE, "Example film")

    settings.LOKAM_TMDB_TOKEN = "unit-test-value"

    def fake_fetch(provider, path, *, params, headers):
        assert provider == "tmdb" and path == "/3/search/movie"
        assert headers["Authorization"] == "Bearer unit-test-value"
        assert params["include_adult"] == "false"
        return {
            "results": [
                {"id": 123, "title": "Example film", "release_date": "1939-01-01"},
                {"id": 456, "title": "Filtered title", "adult": True},
            ]
        }

    (match,) = search_external(ItemKind.MOVIE, "Example film", fetch=fake_fetch)
    assert match.year == 1939
    assert match.source_url == "https://www.themoviedb.org/movie/123"


@pytest.mark.django_db
def test_lok_014_pins_provider_endpoint_and_respects_retry_after():
    def rate_limited(request):
        assert request.url.host == "93.184.216.34"
        assert request.headers["Host"] == "openlibrary.org"
        assert request.extensions["sni_hostname"] == "openlibrary.org"
        return httpx.Response(429, headers={"Retry-After": "45"})

    with pytest.raises(ProviderUnavailable, match="retry delay"):
        get_json(
            "open-library",
            "/search.json",
            transport=httpx.MockTransport(rate_limited),
            resolver=lambda host: "93.184.216.34",
        )
    state = ProviderSyncState.objects.get(provider="open-library")
    assert state.blocked_until > timezone.now() + timedelta(seconds=30)
    with pytest.raises(ProviderUnavailable, match="rate limited"):
        get_json("open-library", "/search.json")
    with pytest.raises(ValueError):
        get_json("open-library", "/unapproved")


@pytest.mark.django_db
def test_lok_014_rejects_private_addresses_without_a_connection():
    with pytest.raises(ProviderUnavailable, match="unapproved address"):
        get_json("open-library", "/search.json", resolver=lambda host: "127.0.0.1")
