import hashlib
import re

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.catalogue.identifiers import Namespace, normalize_identifier
from apps.catalogue.models import (
    Book,
    BookEdition,
    CatalogueItem,
    ItemKind,
    SourceProvider,
)
from apps.catalogue.services import (
    IdentifierConflict,
    bind_identifier,
    record_source,
    resolve_exact,
)
from apps.jobs.services import active_lease

from .http import ProviderUnavailable, get_json


def _text(value, limit):
    return " ".join(value.split())[:limit] if isinstance(value, str) else ""


def _first_text(values, limit):
    return (
        next(
            (
                _text(value, limit)
                for value in values
                if isinstance(value, str) and value.strip()
            ),
            "",
        )
        if isinstance(values, list)
        else ""
    )


def _edition_identifier(row):
    return normalize_identifier(Namespace.OPEN_LIBRARY_EDITION, row.get("key"))


def _isbn_keys(row):
    for field in ("isbn_13", "isbn_10"):
        values = row.get(field)
        if isinstance(values, list):
            for raw in values[:4]:
                try:
                    yield Namespace.ISBN, normalize_identifier(Namespace.ISBN, raw)
                except ValidationError:
                    continue


@transaction.atomic
def _store_edition(book, row):
    identifier = _edition_identifier(row)
    identifiers = [
        (Namespace.OPEN_LIBRARY_EDITION, identifier),
        *dict.fromkeys(_isbn_keys(row)),
    ]
    title = _text(row.get("title"), 240)
    if not title:
        return None
    date = _text(row.get("publish_date"), 80)
    year_match = re.search(r"\b(1[0-9]{3}|20[0-9]{2})\b", date)
    language_key = (
        _first_text(
            [
                value.get("key")
                for value in row["languages"][:4]
                if isinstance(value, dict)
            ],
            32,
        )
        if isinstance(row.get("languages"), list)
        else ""
    )
    language = (
        language_key.removeprefix("/languages/")
        if re.fullmatch(r"/languages/[a-z]{3}", language_key)
        else ""
    )
    item = resolve_exact(identifiers)
    if item is None:
        item = CatalogueItem.objects.create(
            kind=ItemKind.BOOK_EDITION,
            title=title,
            year=int(year_match[1]) if year_match else None,
            language=language,
            is_public=True,
        )
    if item.kind != ItemKind.BOOK_EDITION:
        raise IdentifierConflict("The edition identifier belongs to another item type.")
    edition, _ = BookEdition.objects.get_or_create(
        item=item,
        defaults={
            "book": book,
            "publisher": _first_text(row.get("publishers"), 180),
            "format": _text(row.get("physical_format"), 80),
            "publication_label": date,
        },
    )
    if edition.book_id != book.pk:
        raise IdentifierConflict("The edition already belongs to a different work.")
    for namespace, key in identifiers:
        bind_identifier(item, namespace, key)
    basis = (title, date, edition.publisher, edition.format, language, identifiers)
    revision = hashlib.sha256(repr(basis).encode()).hexdigest()
    fields = {"title", "identifiers"}
    if date:
        fields.add("publication")
    if year_match:
        fields.add("year")
    if edition.publisher:
        fields.add("publisher")
    if edition.format:
        fields.add("format")
    if language:
        fields.add("language")
    record_source(
        item,
        provider=SourceProvider.OPEN_LIBRARY,
        reference=identifier,
        revision=revision,
        url=f"https://openlibrary.org/books/{identifier}",
        fields=fields,
        licence="Open Library catalogue metadata",
        show_credit=True,
    )
    return edition


def enrich_editions(book, work_id, *, fetch=get_json, still_active=lambda: True):
    work_id = normalize_identifier(Namespace.OPEN_LIBRARY_WORK, work_id)
    data = fetch(
        SourceProvider.OPEN_LIBRARY,
        f"/works/{work_id}/editions.json",
        params={"limit": 8},
        headers={"User-Agent": "Lokam/0.1"},
    )
    rows = data.get("entries")
    if not isinstance(rows, list):
        raise ProviderUnavailable("Open Library did not return edition records.")
    imported = []
    for row in rows[:8]:
        if not still_active():
            break
        if not isinstance(row, dict):
            continue
        try:
            edition = _store_edition(book, row)
        except ValidationError:
            continue
        if edition is not None:
            imported.append(edition)
    return imported


def fetch_editions_job(job):
    book = Book.objects.filter(item_id=job.object_id, item__is_public=True).first()
    if book is None:
        return
    work_id = (
        book.item.external_ids.filter(namespace=Namespace.OPEN_LIBRARY_WORK)
        .values_list("value", flat=True)
        .first()
    )
    if work_id is not None:
        enrich_editions(
            book,
            work_id,
            still_active=lambda: active_lease(job.pk, job.lease_token).exists(),
        )
