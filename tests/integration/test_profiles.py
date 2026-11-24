import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import Client
from django.urls import reverse

from apps.accounts.middleware import SESSION_GENERATION_KEY
from apps.core.policies import Visibility
from apps.profiles.models import PageKey
from apps.profiles.services import create_profile, visible_pages


def logged_in(user):
    client = Client()
    client.force_login(user)
    session = client.session
    session[SESSION_GENERATION_KEY] = user.session_generation
    session.save()
    return client


@pytest.fixture
def profile():
    owner = get_user_model().objects.create_user(
        email="reader@example.test", username="reader", email_verified=True
    )
    return create_profile(owner)


@pytest.mark.django_db
def test_lok_011_private_profile_has_exactly_twenty_stable_pages(profile):
    assert list(profile.pages.values_list("key", flat=True)) == PageKey.values
    path = reverse("profiles:home", args=[profile.user.username])
    assert Client().get(path).status_code == 404
    response = logged_in(profile.user).get(path)
    assert response.status_code == 200
    assert b"Personal Timeline" in response.content
    assert logged_in(profile.user).get(path, {"preview": "public"}).status_code == 404
    assert not visible_pages(profile, AnonymousUser()).exists()


@pytest.mark.django_db
def test_lok_011_visibility_composes_and_hiding_revokes_access(profile):
    owner = logged_in(profile.user)
    settings_path = reverse("profiles:settings")
    owner.post(
        settings_path,
        {
            "introduction": "<script>private text</script>",
            "visibility": Visibility.PUBLIC,
        },
    )
    configure_home = reverse("profiles:configure-page", args=[PageKey.HOME])
    home = reverse("profiles:home", args=[profile.user.username])
    books = reverse("profiles:page", args=[profile.user.username, PageKey.BOOKS])
    visitor = Client()
    assert visitor.get(home).status_code == 404

    assert (
        owner.post(
            configure_home, {"enabled": "on", "visibility": Visibility.PUBLIC}
        ).status_code
        == 302
    )
    response = visitor.get(home)
    assert response.status_code == 200
    assert "no-store" in response.headers["Cache-Control"]
    assert b"&lt;script&gt;private text&lt;/script&gt;" in response.content
    assert b"Books" not in response.content
    assert visitor.get(books).status_code == 404
    assert b"Public preview" in owner.get(home, {"preview": "public"}).content

    owner.post(configure_home, {"visibility": Visibility.PUBLIC})
    assert visitor.get(home).status_code == 404
    assert b"hidden from visitors" in owner.get(home).content


@pytest.mark.django_db(transaction=True)
def test_lok_011_owner_reorders_without_touching_other_profiles(profile):
    stranger = get_user_model().objects.create_user(
        email="stranger@example.test", username="stranger", email_verified=True
    )
    other_profile = create_profile(stranger)
    url = reverse("profiles:configure-page", args=[PageKey.BOOKS])
    assert logged_in(profile.user).post(url, {"action": "up"}).status_code == 302
    assert list(profile.pages.values_list("key", flat=True)[:2]) == [
        PageKey.BOOKS,
        PageKey.HOME,
    ]
    assert other_profile.pages.get(key=PageKey.HOME).position == 0
