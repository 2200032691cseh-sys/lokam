from datetime import timedelta
from hashlib import sha256

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import constant_time_compare, salted_hmac

from apps.jobs.services import active_lease, enqueue

from .models import AccountMail, AuthThrottle, User

Purpose = AccountMail.Purpose


def _digest(secret):
    return sha256(secret.encode("ascii")).hexdigest()


def _token(record, user):
    fields = (
        f"{record.reference}:{record.purpose}:{record.session_generation}:{user.email}"
    )
    return salted_hmac("lokam.account-mail", fields, algorithm="sha256").hexdigest()


@transaction.atomic
def issue_mail(user, purpose):
    lifetime = (
        timedelta(hours=24) if purpose == Purpose.VERIFY else timedelta(minutes=30)
    )
    record = AccountMail(
        user=user,
        purpose=purpose,
        session_generation=user.session_generation,
        expires_at=timezone.now() + lifetime,
    )
    record.digest = _digest(_token(record, user))
    record.save()
    enqueue("account-mail", record.pk, f"account-mail:{record.pk}", owner=user)
    return record


def _account_matches(record, user):
    return (
        user.is_active
        and user.session_generation == record.session_generation
        and user.email_verified == (record.purpose == Purpose.RESET)
    )


def send_account_mail(job):
    record = (
        AccountMail.objects.select_related("user")
        .filter(
            pk=job.object_id,
            user_id=job.owner_id,
            used_at__isnull=True,
            sent_at__isnull=True,
        )
        .first()
    )
    if record is None or record.expires_at <= timezone.now():
        return
    token = _token(record, record.user)
    if (
        not _account_matches(record, record.user)
        or not constant_time_compare(record.digest, _digest(token))
        or not active_lease(job.pk, job.lease_token).exists()
    ):
        return
    route = "accounts:verify" if record.purpose == Purpose.VERIFY else "accounts:reset"
    subject = (
        "Verify your Lokam email"
        if record.purpose == Purpose.VERIFY
        else "Reset your Lokam password"
    )
    url = settings.LOKAM_PUBLIC_ORIGIN + reverse(route, args=[record.reference, token])
    send_mail(subject, f"{subject}:\n\n{url}\n", None, [record.user.email])
    AccountMail.objects.filter(pk=record.pk, sent_at__isnull=True).update(
        sent_at=timezone.now()
    )


def resolve_mail(reference, token, purpose, *, lock=False):
    if len(token) != 64 or any(char not in "0123456789abcdef" for char in token):
        return None
    matches = AccountMail.objects.filter(
        reference=reference,
        purpose=purpose,
        expires_at__gt=timezone.now(),
        used_at__isnull=True,
    )
    record = matches.first()
    if record is None or not constant_time_compare(record.digest, _digest(token)):
        return None
    user_query = User.objects.select_for_update() if lock else User.objects
    user = user_query.filter(pk=record.user_id).first()
    if user is None:
        return None
    if lock:
        record = matches.select_for_update().first()
    if (
        record is None
        or not _account_matches(record, user)
        or not constant_time_compare(token, _token(record, user))
    ):
        return None
    return record, user


@transaction.atomic
def consume_mail(reference, token, purpose, *, password=None):
    match = resolve_mail(reference, token, purpose, lock=True)
    if match is None:
        return False
    record, user = match
    if purpose == Purpose.VERIFY:
        user.email_verified = True
        user.save(update_fields=["email_verified"])
    else:
        user.set_password(password)
        user.session_generation += 1
        user.save(update_fields=["password", "session_generation"])
    record.used_at = timezone.now()
    record.save(update_fields=["used_at"])
    return True


@transaction.atomic
def increment_throttle(scope, value, limit, window):
    now = timezone.now()
    bucket = int(now.timestamp()) // window
    key = salted_hmac(
        "lokam.auth-throttle", f"{scope}:{bucket}:{value}", algorithm="sha256"
    ).hexdigest()
    counter, _ = AuthThrottle.objects.select_for_update().get_or_create(
        key=key, defaults={"expires_at": now + timedelta(seconds=window)}
    )
    if counter.count >= limit:
        return False
    counter.count += 1
    counter.save(update_fields=["count"])
    return True


def allow_auth_attempt(request, scope, email, *, per_identity=5):
    ip = request.META.get("REMOTE_ADDR", "unknown")
    return increment_throttle(f"{scope}:network", ip, 30, 900) and increment_throttle(
        f"{scope}:email", email.strip().lower(), per_identity, 900
    )
