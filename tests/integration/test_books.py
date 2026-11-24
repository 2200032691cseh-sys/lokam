import os

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.accounts.middleware import SESSION_GENERATION_KEY
from apps.catalogue.models import (
    Book,
    BookEdition,
    CatalogueItem,
    ItemKind,
    SourceProvider,
)
from apps.core.policies import Visibility
from apps.integrations.adapters import Candidate
from apps.integrations.book_editions import enrich_editions
from apps.integrations.persistence import import_candidate
from apps.jobs.models import BackgroundJob
from apps.libraries.models import BookAnnotation, SaveState
from apps.libraries.services import save_item
from apps.profiles.models import PageKey
from apps.profiles.services import create_profile


@pytest.mark.django_db
def test_lok_020_book_import_persists_authorship_and_schedules_editions(client):
    item = import_candidate(
        Candidate(
            SourceProvider.OPEN_LIBRARY,
            "ol-work",
            "OL66554W",
            ItemKind.BOOK,
            "A novel",
            1813,
            authors=(("An author", "OL700A"),),
        )
    )
    assert item.credits.get().person.item.title == "An author"
    assert (
        BackgroundJob.objects.filter(kind="enrich-book", object_id=item.pk).count() == 1
    )

    def fake_fetch(provider, path, *, params, headers):
        assert path == "/works/OL66554W/editions.json"
        assert params["limit"] == 8
        return {
            "entries": [
                {
                    "key": "/books/OL700M",
                    "title": "One edition",
                    "publish_date": "1995",
                    "publishers": ["A publisher"],
                    "isbn_10": ["0306406152"],
                    "languages": [{"key": "/languages/eng"}],
                },
                {"key": "/books/invalid", "title": "Bad record"},
            ]
        }

    (edition,) = enrich_editions(item.book, "OL66554W", fetch=fake_fetch)
    assert enrich_editions(item.book, "OL66554W", fetch=fake_fetch) == [edition]
    assert BookEdition.objects.count() == 1
    assert (
        b"One edition"
        in client.get(reverse("catalogue:detail", args=[item.public_id])).content
    )
    response = client.get(reverse("catalogue:detail", args=[edition.item.public_id]))
    assert b"9780306406157" in response.content
    assert b"A publisher" in response.content


@pytest.mark.django_db
def test_lok_020_personal_annotations_and_library_filter(client):
    owner = get_user_model().objects.create_user(
        email="reader@example.test", username="reader", email_verified=True
    )
    create_profile(owner)
    client.force_login(owner)
    session = client.session
    session[SESSION_GENERATION_KEY] = owner.session_generation
    session.save()
    novel = CatalogueItem.objects.create(
        title="River stories", kind=ItemKind.BOOK, is_public=True
    )
    other = CatalogueItem.objects.create(
        title="Another book", kind=ItemKind.BOOK, is_public=True
    )
    saved = save_item(owner, novel)
    save_item(owner, other)
    edit_url = reverse("libraries:edit", args=[saved.public_id])
    assert (
        client.post(
            edit_url,
            {
                "state": SaveState.READ,
                "visibility": Visibility.PRIVATE,
                "book-personal_significance": "My reading note",
                "book-ownership": BookAnnotation.Ownership.OWNED,
                "book-favourite_passage": "A brief private excerpt.",
            },
        ).status_code
        == 302
    )
    assert BookAnnotation.objects.get().ownership == BookAnnotation.Ownership.OWNED
    page = reverse("profiles:page", args=[owner.username, PageKey.BOOKS])
    results = client.get(page, {"state": SaveState.READ})
    assert b"River stories" in results.content
    assert b"Another book" not in results.content
    assert b"A brief private excerpt" not in results.content


@pytest.mark.django_db
@pytest.mark.skipif(
    os.environ.get("LOKAM_LIVE_TESTS") != "1", reason="Requires Open Library"
)
def test_lok_020_live_open_library_editions():
    item = CatalogueItem.objects.create(
        title="Pride and Prejudice", kind=ItemKind.BOOK, is_public=True
    )
    book = Book.objects.create(item=item)
    actual = enrich_editions(book, "OL66554W")
    assert actual and all(
        edition.item.external_ids.filter(namespace="ol-edition").exists()
        for edition in actual
    )
