import re

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from apps.accounts.middleware import SESSION_GENERATION_KEY
from apps.catalogue.models import CatalogueItem, ItemKind, SourceProvider
from apps.core.policies import Visibility
from apps.integrations.adapters import Candidate
from apps.integrations.http import ProviderUnavailable
from apps.libraries.models import SaveState, UserItem
from apps.profiles.models import PageKey
from apps.profiles.services import create_profile


@pytest.fixture
def member_client():
    def sign_in(username):
        member = get_user_model().objects.create_user(
            email=f"{username}@example.test", username=username, email_verified=True
        )
        create_profile(member)
        client = Client()
        client.force_login(member)
        session = client.session
        session[SESSION_GENERATION_KEY] = member.session_generation
        session.save()
        return client, member

    return sign_in


@pytest.mark.django_db
def test_lok_015_external_result_requires_owner_and_saves_once(
    member_client, monkeypatch
):
    owner, member = member_client("reader")
    stranger, _ = member_client("stranger")
    external = Candidate(
        SourceProvider.OPEN_LIBRARY,
        "ol-work",
        "OL999W",
        ItemKind.BOOK,
        "A chosen book",
        1802,
    )
    calls = []

    def lookup(kind, query):
        calls.append((kind, query))
        return [external]

    monkeypatch.setattr("apps.libraries.views.search_external", lookup)
    add = reverse("libraries:add")
    values = {"kind": ItemKind.BOOK, "query": "chosen book"}
    assert owner.get(add, values).status_code == 200
    assert not calls
    response = owner.get(add, {**values, "external": "yes"})
    token = re.search(rb'name="candidate" value="([^"]+)"', response.content)[
        1
    ].decode()
    save = reverse("libraries:save-external")

    assert stranger.post(save, {"candidate": token}).status_code == 302
    assert not UserItem.objects.exists()
    assert owner.post(save, {"candidate": token}).status_code == 302
    assert owner.post(save, {"candidate": token}).status_code == 302
    assert (
        UserItem.objects.filter(owner=member, item__title=external.title).count() == 1
    )
    assert CatalogueItem.objects.get().sources.count() == 1


@pytest.mark.django_db
def test_lok_015_private_manual_entries_survive_outage(member_client, monkeypatch):
    owner, member = member_client("reader")
    stranger, _ = member_client("stranger")

    def unavailable(*args):
        raise ProviderUnavailable("Unavailable")

    monkeypatch.setattr("apps.libraries.views.search_external", unavailable)
    add = reverse("libraries:add")
    response = owner.get(
        add, {"kind": ItemKind.BOOK, "query": "My title", "external": "yes"}
    )
    assert b"temporarily unavailable" in response.content
    manual = reverse("libraries:manual")
    assert (
        owner.post(manual, {"kind": ItemKind.BOOK, "title": "My title"}).status_code
        == 302
    )
    assert (
        owner.post(manual, {"kind": ItemKind.BOOK, "title": "MY TITLE"}).status_code
        == 302
    )
    saved = UserItem.objects.get(owner=member)
    assert saved.item.owner == member
    assert not saved.item.is_public
    assert (
        b"My title"
        not in stranger.get(
            add, {"kind": ItemKind.BOOK, "query": "My title"}
        ).content.split(b"Lokam matches")[1]
    )
    edit = reverse("libraries:edit", args=[saved.public_id])
    assert stranger.get(edit).status_code == 404
    assert stranger.post(edit, {"state": SaveState.READ}).status_code == 404


@pytest.mark.django_db
def test_lok_015_published_relationship_respects_origin_page(member_client):
    owner, member = member_client("reader")
    item = CatalogueItem.objects.create(
        kind=ItemKind.BOOK, title="Shared book", is_public=True
    )
    owner.post(reverse("libraries:save-existing", args=[item.public_id]))
    saved = UserItem.objects.get(owner=member)
    edit = reverse("libraries:edit", args=[saved.public_id])
    settings = reverse("profiles:settings")
    page_settings = reverse("profiles:configure-page", args=[PageKey.BOOKS])
    page = reverse("profiles:page", args=[member.username, PageKey.BOOKS])

    assert (
        owner.post(
            edit, {"state": SaveState.WATCHED, "visibility": Visibility.PUBLIC}
        ).status_code
        == 200
    )
    owner.post(
        edit,
        {
            "state": SaveState.READ,
            "visibility": Visibility.PUBLIC,
            "note": "Secret note",
        },
    )
    owner.post(settings, {"visibility": Visibility.PUBLIC})
    assert Client().get(page).status_code == 404
    owner.post(page_settings, {"enabled": "on", "visibility": Visibility.PUBLIC})
    result = Client().get(page)
    assert b"Shared book" in result.content and b"Secret note" not in result.content
