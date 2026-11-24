from datetime import timedelta
from urllib.parse import urlsplit

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import AccountMail
from apps.jobs.services import claim, finish

EMAIL = "reader@example.test"
PASSWORD = "Ivory-tomato-canvas-381"
NEW_PASSWORD = "Granite-windmill-book-693"


def deliver_queued_email():
    job = claim()
    call_command("execute_job", str(job.pk), str(job.lease_token))
    assert finish(job)
    return urlsplit(mail.outbox[-1].body.splitlines()[-1]).path


@pytest.mark.django_db
def test_lok_010_signup_verification_and_login(client):
    post = {
        "email": EMAIL,
        "username": "reader",
        "password": PASSWORD,
        "password_confirmation": PASSWORD,
    }
    assert client.post(reverse("accounts:signup"), post).status_code == 200
    user = get_user_model().objects.get(email=EMAIL)
    assert not user.email_verified
    assert client.post(reverse("accounts:signup"), post).status_code == 200
    assert AccountMail.objects.count() == 1
    assert client.post(reverse("accounts:login"), post).status_code == 200

    path = deliver_queued_email()
    assert AccountMail.objects.get().digest != path.rstrip("/").rsplit("/", 1)[1]
    assert client.get(path).status_code == 200
    user.refresh_from_db()
    assert not user.email_verified
    assert client.post(path).status_code == 302
    assert client.post(path).status_code == 400
    assert client.post(reverse("accounts:login"), post).status_code == 302
    assert b"Log out" in client.get(reverse("landing")).content
    assert client.get(reverse("accounts:logout")).status_code == 405
    assert client.post(reverse("accounts:logout")).status_code == 302
    assert b"Log out" not in client.get(reverse("landing")).content


@pytest.mark.django_db
def test_lok_010_recovery_revokes_existing_sessions(client):
    user = get_user_model().objects.create_user(
        email=EMAIL, username="reader", password=PASSWORD, email_verified=True
    )
    assert (
        client.post(
            reverse("accounts:login"), {"email": EMAIL, "password": PASSWORD}
        ).status_code
        == 302
    )
    recovery_client = Client()
    recover = reverse("accounts:recover")
    known = recovery_client.post(recover, {"email": EMAIL})
    unknown = recovery_client.post(recover, {"email": "unknown@example.test"})
    assert known.status_code == unknown.status_code == 200
    assert known.content == unknown.content
    path = deliver_queued_email()

    values = {"password": NEW_PASSWORD, "password_confirmation": NEW_PASSWORD}
    assert recovery_client.post(path, values).status_code == 302
    assert recovery_client.post(path, values).status_code == 400
    assert b"Log out" not in client.get(reverse("landing")).content
    user.refresh_from_db()
    assert user.session_generation == 1 and user.check_password(NEW_PASSWORD)


@pytest.mark.django_db
def test_lok_010_expired_recovery_link_fails(client):
    user = get_user_model().objects.create_user(
        email=EMAIL, username="reader", password=PASSWORD, email_verified=True
    )
    client.post(reverse("accounts:recover"), {"email": EMAIL})
    path = deliver_queued_email()
    AccountMail.objects.filter(user=user).update(
        expires_at=timezone.now() - timedelta(seconds=1)
    )
    assert client.get(path).status_code == 400


@pytest.mark.django_db
def test_lok_010_csrf_and_throttled_login(client):
    get_user_model().objects.create_user(
        email=EMAIL, username="reader", password=PASSWORD, email_verified=True
    )
    path = reverse("accounts:login")
    data = {"email": EMAIL, "password": PASSWORD}
    assert Client(enforce_csrf_checks=True).post(path, data).status_code == 403
    for _ in range(5):
        assert client.post(path, {**data, "password": "wrong"}).status_code == 200
    assert client.post(path, data).status_code == 200
    assert "_auth_user_id" not in client.session
