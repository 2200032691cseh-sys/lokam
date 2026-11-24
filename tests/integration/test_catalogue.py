import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.urls import reverse

from apps.catalogue.models import (
    CatalogueAlias,
    CatalogueItem,
    ItemKind,
    ItemPersonRole,
    Person,
)


@pytest.mark.django_db
def test_lok_012_catalogue_exposes_only_public_items_and_credits(client):
    book = CatalogueItem.objects.create(
        title="The River", kind=ItemKind.BOOK, is_public=True
    )
    private = CatalogueItem.objects.create(
        title="Unpublished contributor", kind=ItemKind.PERSON
    )
    public = CatalogueItem.objects.create(
        title="Public contributor", kind=ItemKind.PERSON, is_public=True
    )
    for item in (private, public):
        ItemPersonRole.objects.create(
            item=book,
            person=Person.objects.create(item=item),
            role=ItemPersonRole.Role.AUTHOR,
        )
    response = client.get(reverse("catalogue:detail", args=[book.public_id]))

    assert response.status_code == 200
    assert b"Public contributor" in response.content
    assert b"Unpublished contributor" not in response.content
    assert (
        client.get(reverse("catalogue:detail", args=[private.public_id])).status_code
        == 404
    )


@pytest.mark.django_db
def test_lok_012_filters_and_paginates(client):
    for number in range(25):
        CatalogueItem.objects.create(
            title=f"Book {number:02d}", kind=ItemKind.BOOK, is_public=True
        )
    CatalogueItem.objects.create(
        title="Another film", kind=ItemKind.MOVIE, is_public=True
    )
    url = reverse("catalogue:browse")
    response = client.get(url, {"kind": ItemKind.BOOK, "page": 2})
    assert response.status_code == 200
    assert b"Page 2 of 2" in response.content
    assert b"Book 24" in response.content
    assert b"Another film" not in response.content


@pytest.mark.django_db
def test_lok_012_search_names_and_custom_item_constraints():
    book = CatalogueItem.objects.create(title="  Ｔhe Café  ", kind=ItemKind.BOOK)
    assert book.title_key == "the café"
    CatalogueAlias.objects.create(item=book, title="Café Novel", language="en")
    with pytest.raises(IntegrityError), transaction.atomic():
        CatalogueAlias.objects.create(item=book, title="CAFÉ NOVEL", language="en")

    user = get_user_model().objects.create_user(
        email="reader@example.test", username="reader"
    )
    with pytest.raises(IntegrityError), transaction.atomic():
        CatalogueItem.objects.create(
            owner=user, title="Personal entry", kind=ItemKind.BOOK, is_public=True
        )
