import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse

from apps.catalogue.identifiers import Namespace, normalize_identifier
from apps.catalogue.models import CatalogueItem, ItemKind, SourceProvider
from apps.catalogue.services import (
    IdentifierConflict,
    bind_identifier,
    record_source,
    resolve_exact,
)


def test_lok_013_stable_identifier_normalization():
    assert normalize_identifier(Namespace.ISBN, "0-306-40615-2") == "9780306406157"
    assert (
        normalize_identifier(Namespace.OPEN_LIBRARY_WORK, "/works/ol123w") == "OL123W"
    )
    assert normalize_identifier(Namespace.WIKIDATA, "q24") == "Q24"
    with pytest.raises(ValidationError):
        normalize_identifier(Namespace.ISBN, "9780306406150")
    with pytest.raises(ValidationError):
        normalize_identifier(Namespace.OPEN_LIBRARY_WORK, "/books/OL123M")


@pytest.mark.django_db
def test_lok_013_exact_resolution_prevents_conflicting_bindings():
    one = CatalogueItem.objects.create(title="One", kind=ItemKind.BOOK)
    two = CatalogueItem.objects.create(title="Two", kind=ItemKind.BOOK)
    first = bind_identifier(one, Namespace.OPEN_LIBRARY_WORK, "OL123W")
    assert bind_identifier(one, Namespace.OPEN_LIBRARY_WORK, "/works/ol123w") == first
    assert resolve_exact([(Namespace.OPEN_LIBRARY_WORK, "OL123W")]) == one
    with pytest.raises(IdentifierConflict):
        bind_identifier(two, Namespace.OPEN_LIBRARY_WORK, "OL123W")
    bind_identifier(two, Namespace.WIKIDATA, "Q24")
    with pytest.raises(IdentifierConflict):
        resolve_exact(
            [(Namespace.OPEN_LIBRARY_WORK, "OL123W"), (Namespace.WIKIDATA, "Q24")]
        )
    with pytest.raises(ValidationError):
        bind_identifier(two, Namespace.TMDB_MOVIE, "123")


@pytest.mark.django_db
def test_lok_013_rendered_source_has_recorded_rights_and_revision(client):
    item = CatalogueItem.objects.create(
        title="Illustration", kind=ItemKind.BOOK, is_public=True
    )
    source = record_source(
        item,
        provider=SourceProvider.WIKIDATA,
        reference="Q24",
        revision="314",
        url="https://www.wikidata.org/wiki/Q24",
        fields=["title"],
        licence="CC0",
        show_credit=True,
    )
    assert source.fields == ["title"]
    assert source.revision == "314"
    assert not source.export_allowed
    response = client.get(reverse("catalogue:detail", args=[item.public_id]))
    assert b"https://www.wikidata.org/wiki/Q24" in response.content
    with pytest.raises(ValidationError):
        record_source(
            item,
            provider=SourceProvider.WIKIDATA,
            reference="Q24",
            revision="314",
            url="https://example.test/private",
            fields=["title"],
        )
