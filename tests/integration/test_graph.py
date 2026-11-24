import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse

from apps.catalogue.identifiers import Namespace
from apps.catalogue.models import (
    CatalogueItem,
    CatalogueRelationship,
    ItemKind,
    Predicate,
    SourceProvider,
)
from apps.catalogue.relationships import (
    record_edge,
    supported_public_edges,
    verify_edge,
)
from apps.catalogue.services import bind_identifier, record_source, resolve_exact
from apps.integrations.wikidata_graph import import_wikidata_edges


def statement(qid, code, value, rank="normal"):
    return {
        "id": f"{qid}${code}",
        "rank": rank,
        "mainsnak": {"datavalue": {"value": value}},
    }


@pytest.mark.django_db
def test_lok_016_builds_typed_edges_without_marking_them_verified(client):
    book = CatalogueItem.objects.create(
        title="A novel", kind=ItemKind.BOOK, is_public=True
    )
    film = CatalogueItem.objects.create(
        title="Its film adaptation", kind=ItemKind.MOVIE, is_public=True
    )
    bind_identifier(book, Namespace.OPEN_LIBRARY_WORK, "OL66554W")
    bind_identifier(film, Namespace.WIKIDATA, "Q270385")
    record_source(
        film,
        provider=SourceProvider.WIKIDATA,
        reference="Q270385",
        revision="22",
        url="https://www.wikidata.org/wiki/Q270385",
        fields={"title"},
        licence="CC0 structured data",
        show_credit=True,
    )
    entities = {
        "Q170583": {
            "id": "Q170583",
            "lastrevid": 21,
            "claims": {
                "P648": [statement("Q170583", "p648", "OL66554W")],
            },
        },
        "Q270385": {
            "id": "Q270385",
            "lastrevid": 22,
            "claims": {
                "P144": [
                    statement("Q270385", "p144", {"id": "Q170583"}),
                    statement("Q270385", "old", {"id": "Q170583"}, rank="deprecated"),
                ],
            },
        },
    }
    (edge,) = import_wikidata_edges(entities)
    assert edge.subject == film and edge.object == book
    assert edge.predicate == Predicate.ADAPTED_FROM
    assert edge.evidence.count() == 1
    assert edge.evidence.get().source.revision == "22"
    assert resolve_exact([(Namespace.WIKIDATA, "Q170583")]) == book
    assert import_wikidata_edges(entities) == [edge]
    page = reverse("catalogue:detail", args=[book.public_id])
    assert b"Its film adaptation" not in client.get(page).content

    verify_edge(edge.pk)
    assert b"Its film adaptation" in client.get(page).content
    film.is_public = False
    film.save(update_fields=["is_public"])
    assert not supported_public_edges().exists()
    assert b"Its film adaptation" not in client.get(page).content


@pytest.mark.django_db
def test_lok_016_cannot_verify_without_evidence_or_bind_wrong_type():
    film = CatalogueItem.objects.create(title="A film", kind=ItemKind.MOVIE)
    book = CatalogueItem.objects.create(title="A book", kind=ItemKind.BOOK)
    edge = CatalogueRelationship.objects.create(
        subject=film, predicate=Predicate.ADAPTED_FROM, object=book
    )
    with pytest.raises(ValidationError):
        verify_edge(edge.pk)
    source = record_source(
        film,
        provider=SourceProvider.MANUAL,
        reference="example",
        revision="1",
        url="https://example.test/story",
        fields={"relationship"},
        licence="Reference citation",
        show_credit=True,
    )
    with pytest.raises(ValidationError):
        record_edge(film, Predicate.SET_IN, book, source=source, statement_id="invalid")
