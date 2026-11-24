from datetime import timedelta

import httpx
import pytest
from django.utils import timezone

from apps.catalogue.models import CatalogueItem, ItemKind
from apps.integrations.adapters import search_external
from apps.integrations.http import (
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


@pytest.mark.parametrize(
    "kind, screen_class", [(ItemKind.MOVIE, "Q11424"), (ItemKind.SHOW, "Q5398426")]
)
def test_lok_014_wikidata_accepts_only_matching_classes(kind, screen_class):
    def claim(value, rank="normal"):
        return {"rank": rank, "mainsnak": {"datavalue": {"value": value}}}

    def fake_fetch(provider, path, *, params, headers):
        assert path == "/w/api.php" and "Authorization" not in headers
        if provider == "wikidata-search":
            assert params["action"] == "wbsearchentities"
            return {"search": [{"id": "Q24"}, {"id": "Q25"}, {"id": "not-an-id"}]}
        assert params["ids"] == "Q24|Q25"
        return {
            "entities": {
                "Q24": {
                    "lastrevid": 421,
                    "labels": {"en": {"value": "Screen title"}},
                    "claims": {
                        "P31": [claim({"id": screen_class})],
                        "P577": [
                            claim({"time": "+1939-01-01T00:00:00Z", "precision": 11})
                        ],
                    },
                },
                "Q25": {
                    "labels": {"en": {"value": "Unrelated title"}},
                    "claims": {"P31": [claim({"id": screen_class}, rank="deprecated")]},
                },
            }
        }

    (match,) = search_external(kind, "Screen title", fetch=fake_fetch)
    assert match.year == 1939 and match.revision == "421"
    assert match.source_url == "https://www.wikidata.org/wiki/Q24"


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
