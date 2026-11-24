import json
import re
import socket
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from ipaddress import ip_address
from threading import BoundedSemaphore
from time import monotonic

import httpx
from django.db import transaction
from django.utils import timezone

from .models import ProviderSyncState

HOSTS = {
    "open-library": "openlibrary.org",
    "wikidata-search": "www.wikidata.org",
    "wikidata-read": "www.wikidata.org",
    "wikidata-labels": "www.wikidata.org",
    "commons-image": "commons.wikimedia.org",
    "tvmaze": "api.tvmaze.com",
}
PATHS = {
    "open-library": re.compile(
        r"/(?:search\.json|works/OL[1-9][0-9]{0,15}W(?:\.json|/editions\.json))"
    ),
    "wikidata-search": re.compile(r"/w/api\.php"),
    "wikidata-read": re.compile(r"/w/api\.php"),
    "wikidata-labels": re.compile(r"/w/api\.php"),
    "commons-image": re.compile(r"/w/api\.php"),
    "tvmaze": re.compile(
        r"/(?:shows/[1-9][0-9]{0,11}|seasons/[1-9][0-9]{0,11}/episodes)"
    ),
}
INTERVALS = {provider: 1 for provider in HOSTS}
MAX_RESPONSE_BYTES = 512 * 1024
DNS_THREADS = ThreadPoolExecutor(max_workers=2, thread_name_prefix="provider-dns")
DNS_SLOTS = BoundedSemaphore(2)


class ProviderUnavailable(Exception):
    """Provider access or quota is temporarily unavailable."""


def _public_address(host):
    if not DNS_SLOTS.acquire(blocking=False):
        raise ProviderUnavailable("Provider DNS is busy.")
    lookup = DNS_THREADS.submit(socket.getaddrinfo, host, 443, type=socket.SOCK_STREAM)
    lookup.add_done_callback(lambda _: DNS_SLOTS.release())
    try:
        addresses = {ip_address(entry[4][0]) for entry in lookup.result(timeout=1.0)}
    except (OSError, TimeoutError) as error:
        raise ProviderUnavailable("Provider DNS is unavailable.") from error
    if not addresses or any(
        not value.is_global or value.is_multicast for value in addresses
    ):
        raise ProviderUnavailable("Provider DNS returned an unapproved address.")
    return str(min(addresses, key=lambda value: (value.version, int(value))))


@transaction.atomic
def reserve(provider):
    state, _ = ProviderSyncState.objects.select_for_update().get_or_create(
        provider=provider
    )
    now = timezone.now()
    if state.next_request_at > now or (
        state.blocked_until and state.blocked_until > now
    ):
        raise ProviderUnavailable("The provider is temporarily rate limited.")
    state.next_request_at = now + timedelta(seconds=INTERVALS[provider])
    state.save(update_fields=["next_request_at"])


@transaction.atomic
def record_result(provider, *, success=False, retry_after=0):
    state = ProviderSyncState.objects.select_for_update().get(provider=provider)
    if success:
        state.consecutive_failures = 0
    else:
        state.consecutive_failures = min(3, state.consecutive_failures + 1)
        if state.consecutive_failures >= 3:
            retry_after = max(retry_after, 30)
        if retry_after:
            until = timezone.now() + timedelta(seconds=min(retry_after, 900))
            state.blocked_until = max(state.blocked_until or until, until)
    state.save(update_fields=["consecutive_failures", "blocked_until"])


def get_json(
    provider,
    path,
    *,
    params=None,
    headers=None,
    transport=None,
    resolver=_public_address,
    expected=dict,
):
    if provider not in HOSTS or not PATHS[provider].fullmatch(path):
        raise ValueError("External requests require an approved provider endpoint.")
    reserve(provider)
    host = HOSTS[provider]
    deadline = monotonic() + 4.0
    try:
        address = resolver(host)
        ip = ip_address(address)
        if not ip.is_global or ip.is_multicast:
            raise ProviderUnavailable("Provider DNS returned an unapproved address.")
        target = f"[{address}]" if ip.version == 6 else address
        with (
            httpx.Client(
                timeout=httpx.Timeout(1.5, connect=1.5),
                follow_redirects=False,
                trust_env=False,
                transport=transport,
            ) as client,
            client.stream(
                "GET",
                f"https://{target}{path}",
                params=params,
                headers={
                    **(headers or {}),
                    "Host": host,
                    "Accept": "application/json",
                    "Accept-Encoding": "identity",
                },
                extensions={"sni_hostname": host},
            ) as response,
        ):
            if response.status_code == 429:
                value = response.headers.get("Retry-After", "")[:12]
                delay = int(value) if value.isascii() and value.isdigit() else 60
                record_result(provider, retry_after=max(1, delay))
                raise ProviderUnavailable("The provider requested a retry delay.")
            response.raise_for_status()
            if (
                response.headers.get("Content-Encoding", "identity").lower()
                != "identity"
            ):
                raise ValueError("Unexpected response encoding.")
            body = bytearray()
            for chunk in response.iter_bytes(chunk_size=8192):
                body.extend(chunk)
                if len(body) > MAX_RESPONSE_BYTES or monotonic() > deadline:
                    raise ValueError("The provider response exceeded its budget.")
            data = json.loads(body)
            if not isinstance(data, expected):
                raise ValueError("The provider returned an unexpected response.")
    except ProviderUnavailable:
        raise
    except (httpx.HTTPError, OSError, ValueError, RecursionError) as error:
        record_result(provider)
        raise ProviderUnavailable(
            "The provider returned an unavailable response."
        ) from error
    record_result(provider, success=True)
    return data
