import pytest
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import identify_hasher
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction


@pytest.mark.django_db
def test_lok_008_canonical_identity_and_argon2():
    user = get_user_model().objects.create_user(
        email=" Reader@Example.test ",
        username="READER",
        password="sample-test-password",
    )

    assert user.email == "reader@example.test"
    assert user.username == "reader"
    assert identify_hasher(user.password).algorithm == "argon2"
    assert (
        authenticate(username="READER@EXAMPLE.TEST", password="sample-test-password")
        == user
    )
    assert not user.is_staff
    assert not user.email_verified


@pytest.mark.django_db
def test_lok_008_rejects_duplicate_and_noncanonical_writes():
    manager = get_user_model().objects
    manager.create_user(email="reader@example.test", username="reader")

    with pytest.raises(IntegrityError), transaction.atomic():
        manager.create_user(email="READER@EXAMPLE.TEST", username="other")
    with pytest.raises(IntegrityError), transaction.atomic():
        manager.create(email="other@example.test", username="READER")
    with pytest.raises(ValidationError):
        manager.create_user(email="other@example.test", username="reader name")
