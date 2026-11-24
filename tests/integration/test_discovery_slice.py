import os
from urllib.parse import urlsplit

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.urls import reverse

from apps.catalogue.models import (
    CatalogueItem,
    ItemKind,
    ItemTag,
    Predicate,
    SourceProvider,
    VocabularyTerm,
)
from apps.catalogue.relationships import record_edge, verify_edge
from apps.catalogue.services import record_source
from apps.integrations.adapters import search_external
from apps.integrations.persistence import import_candidate
from apps.integrations.wikidata_graph import sync_wikidata_edges
from apps.jobs.services import claim, finish
from apps.libraries.services import save_item


def create_and_verify_account(client):
    credentials = {
        "email": "reader@example.test",
        "password": "granite-sunrise-path-978",
    }
    assert (
        client.post(
            reverse("accounts:signup"),
            {
                **credentials,
                "username": "reader",
                "password_confirmation": credentials["password"],
            },
        ).status_code
        == 200
    )
    job = claim()
    call_command("execute_job", str(job.pk), str(job.lease_token))
    assert finish(job)
    link = urlsplit(mail.outbox[-1].body.splitlines()[-1]).path
    assert client.post(link).status_code == 302
    assert client.post(reverse("accounts:login"), credentials).status_code == 302
    return get_user_model().objects.get(email=credentials["email"])


@pytest.mark.django_db
def test_lok_017_one_user_gets_graph_and_content_evidence(client):
    owner = create_and_verify_account(client)
    book = CatalogueItem.objects.create(
        title="A reader's novel", kind=ItemKind.BOOK, is_public=True
    )
    film = CatalogueItem.objects.create(
        title="A film adaptation", kind=ItemKind.MOVIE, is_public=True
    )
    place = CatalogueItem.objects.create(
        title="A thematically related place", kind=ItemKind.PLACE, is_public=True
    )
    source = record_source(
        film,
        provider=SourceProvider.MANUAL,
        reference="adaptation",
        revision="1",
        url="https://example.test/film",
        fields={"relationship"},
        licence="Citation",
        show_credit=True,
    )
    edge = record_edge(
        film, Predicate.ADAPTED_FROM, book, source=source, statement_id="adaptation"
    )
    theme = VocabularyTerm.objects.create(
        label="Coastal settlements", kind=VocabularyTerm.Kind.THEME
    )
    ItemTag.objects.bulk_create(
        [ItemTag(item=book, term=theme), ItemTag(item=place, term=theme)]
    )
    save_item(owner, book)
    discover = reverse("discovery:discover")
    assert b"A film adaptation" not in client.get(discover).content
    verify_edge(edge.pk)
    result = client.get(discover)
    assert result.status_code == 200
    assert "no-store" in result.headers["Cache-Control"]
    assert b"Adaptation of A reader&#x27;s novel" in result.content
    assert b"Shares the catalogue subject Coastal settlements" in result.content
    assert (
        b"A film adaptation"
        not in client.get(discover, {"kind": ItemKind.PLACE}).content
    )
    assert get_user_model().objects.count() == 1
    save_item(owner, film)
    assert b"A film adaptation" not in client.get(discover).content


@pytest.mark.django_db
@pytest.mark.skipif(
    os.environ.get("LOKAM_LIVE_TESTS") != "1", reason="Requires live public providers"
)
def test_lok_017_live_single_user_acquisition_and_adaptation(client):
    film = next(
        item
        for item in search_external(ItemKind.MOVIE, "Pride & Prejudice")
        if item.identifier == "Q270385"
    )
    movie = import_candidate(film)
    create_and_verify_account(client)
    add_url = reverse("libraries:add")
    response = client.get(
        add_url,
        {"kind": ItemKind.BOOK, "query": "Pride and Prejudice", "external": "yes"},
    )
    book, token = next(
        pair
        for pair in response.context["external_matches"]
        if pair[0].identifier == "OL66554W"
    )
    assert (
        client.post(
            reverse("libraries:save-external"), {"candidate": token}
        ).status_code
        == 302
    )
    edges = sync_wikidata_edges(["Q170583", "Q270385"])
    edge = next(
        edge
        for edge in edges
        if edge.subject_id == movie.pk and edge.predicate == Predicate.ADAPTED_FROM
    )
    assert edge.object.title == book.title
    source = record_source(
        movie,
        provider=SourceProvider.MANUAL,
        reference="focus-features-adaptation",
        revision="1",
        url="https://www.focusfeatures.com/pride_and_prejudice",
        fields={"relationship"},
        licence="Reference citation",
        show_credit=True,
    )
    record_edge(
        movie,
        Predicate.ADAPTED_FROM,
        edge.object,
        source=source,
        statement_id="adaptation",
    )
    verify_edge(edge.pk)
    response = client.get(reverse("discovery:discover"))
    assert response.status_code == 200
    assert response.context["recommendations"][0].item == movie
    assert response.context["recommendations"][0].reason.startswith("Adaptation of")
    assert get_user_model().objects.count() == 1
