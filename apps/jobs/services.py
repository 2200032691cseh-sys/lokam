import secrets
import uuid
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.db.models import F, Q
from django.utils import timezone

from .models import BackgroundJob

State = BackgroundJob.State
ERROR_CODES = {"handler_failed", "handler_missing", "timeout"}


def enqueue(kind, object_id, dedup_key, *, owner=None):
    """Call inside the transaction that creates the object referenced by the job."""
    if kind not in settings.LOKAM_JOB_HANDLERS or object_id < 1 or not dedup_key:
        raise ValueError(
            "A registered job kind, object ID and deduplication key are required."
        )
    job, _ = BackgroundJob.objects.get_or_create(
        dedup_key=dedup_key,
        defaults={"kind": kind, "object_id": object_id, "owner": owner},
    )
    if (job.kind, job.object_id, job.owner_id) != (
        kind,
        object_id,
        owner.pk if owner else None,
    ):
        raise ValueError("This job key already identifies a different job.")
    return job


@transaction.atomic
def claim():
    now = timezone.now()
    expired = Q(state=State.RUNNING, lease_until__lte=now)
    exhausted = list(
        BackgroundJob.objects.select_for_update(skip_locked=True)
        .filter(expired, attempts__gte=F("max_attempts"))
        .order_by("lease_until", "id")
        .values_list("id", flat=True)[:50]
    )
    if exhausted:
        BackgroundJob.objects.filter(id__in=exhausted).update(
            state=State.FAILED,
            lease_token=None,
            lease_until=None,
            error_code="lease_expired",
        )
    job = (
        BackgroundJob.objects.select_for_update(skip_locked=True)
        .filter(Q(state=State.READY, available_at__lte=now) | expired)
        .filter(attempts__lt=F("max_attempts"))
        .order_by("available_at", "id")
        .first()
    )
    if job is None:
        return None
    job.state = State.RUNNING
    job.attempts += 1
    job.lease_token = uuid.uuid4()
    job.lease_until = now + timedelta(seconds=job.timeout_seconds + 15)
    job.save(update_fields=["state", "attempts", "lease_token", "lease_until"])
    return job


def active_lease(job_id, token):
    return BackgroundJob.objects.filter(
        pk=job_id,
        state=State.RUNNING,
        lease_token=token,
        lease_until__gt=timezone.now(),
    )


def finish(job, *, error=""):
    if error and error not in ERROR_CODES:
        raise ValueError("Unknown job error code.")
    values = {"lease_token": None, "lease_until": None, "error_code": error}
    if not error:
        values["state"] = State.SUCCEEDED
    elif job.attempts >= job.max_attempts or error == "handler_missing":
        values["state"] = State.FAILED
    else:
        values["state"] = State.READY
        delay = min(300, 2**job.attempts) + secrets.randbelow(5)
        values["available_at"] = timezone.now() + timedelta(seconds=delay)
    return active_lease(job.pk, job.lease_token).update(**values) == 1


def cancel(job_id, *, owner):
    return (
        BackgroundJob.objects.filter(
            pk=job_id, owner_id=owner.pk, state__in=[State.READY, State.RUNNING]
        ).update(state=State.CANCELLED, lease_token=None, lease_until=None)
        == 1
    )
