from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import connections
from django.utils import timezone

from apps.jobs.models import BackgroundJob
from apps.jobs.services import cancel, claim, enqueue, finish


@pytest.fixture
def registered_job(settings):
    settings.LOKAM_JOB_HANDLERS = {"test": "tests.integration.test_jobs.test_handler"}
    return enqueue("test", 1, "test:1")


@pytest.mark.django_db(transaction=True)
def test_lok_009_competing_workers_receive_one_lease(registered_job):
    start = Barrier(2, timeout=5)

    def lease_once():
        try:
            start.wait()
            return claim()
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _: lease_once(), range(2)))

    assert sum(result is not None for result in results) == 1
    leased = next(result for result in results if result is not None)
    assert leased.pk == registered_job.pk
    assert finish(leased)
    assert not finish(leased)


@pytest.mark.django_db
def test_lok_009_expired_lease_is_reclaimed_and_fenced(registered_job):
    original = claim()
    BackgroundJob.objects.filter(pk=original.pk).update(
        lease_until=timezone.now() - timedelta(seconds=1)
    )

    reclaimed = claim()
    assert reclaimed.pk == original.pk
    assert reclaimed.lease_token != original.lease_token
    assert not finish(original)
    assert finish(reclaimed)


@pytest.mark.django_db
def test_lok_009_errors_back_off_then_expire(registered_job):
    job = claim()
    assert finish(job, error="timeout")
    assert claim() is None
    BackgroundJob.objects.filter(pk=job.pk).update(
        available_at=timezone.now(), max_attempts=2
    )
    job = claim()
    BackgroundJob.objects.filter(pk=job.pk).update(
        lease_until=timezone.now() - timedelta(seconds=1)
    )

    assert claim() is None
    job.refresh_from_db()
    assert job.state == BackgroundJob.State.FAILED
    assert job.error_code == "lease_expired"


@pytest.mark.django_db
def test_lok_009_duplicate_and_cancel_are_scoped(settings):
    settings.LOKAM_JOB_HANDLERS = {"test": "tests.integration.test_jobs.test_handler"}
    users = get_user_model().objects
    owner = users.create_user(email="owner@example.test", username="owner")
    other = users.create_user(email="other@example.test", username="other")
    job = enqueue("test", owner.pk, "test:owner", owner=owner)

    assert enqueue("test", owner.pk, "test:owner", owner=owner) == job
    with pytest.raises(ValueError):
        enqueue("test", other.pk, "test:owner", owner=other)

    leased = claim()
    assert not cancel(job.pk, owner=other)
    assert cancel(job.pk, owner=owner)
    assert not finish(leased)


@pytest.mark.django_db
def test_lok_009_command_runs_only_a_current_lease(settings):
    settings.LOKAM_JOB_HANDLERS = {"test": "builtins.repr"}
    job = enqueue("test", 1, "test:command")
    lease = claim()

    call_command("execute_job", str(job.pk), str(lease.lease_token))
    assert finish(lease)
