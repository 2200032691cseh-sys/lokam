import hashlib

from django.db import transaction

from apps.catalogue.models import CatalogueItem, SourceProvider
from apps.catalogue.services import (
    IdentifierConflict,
    bind_identifier,
    record_source,
    resolve_exact,
)

ATTRIBUTION = {
    SourceProvider.OPEN_LIBRARY: "Open Library catalogue metadata",
    SourceProvider.TMDB: "TMDB attributed noncommercial metadata",
}


@transaction.atomic
def _persist(candidate):
    item = resolve_exact([(candidate.namespace, candidate.identifier)])
    if item is None:
        item = CatalogueItem.objects.create(
            kind=candidate.kind,
            title=candidate.title,
            year=candidate.year,
            is_public=True,
        )
        bind_identifier(item, candidate.namespace, candidate.identifier)
    elif item.kind != candidate.kind:
        raise IdentifierConflict(
            "The provider identifier has an incompatible catalogue type."
        )
    revision = hashlib.sha256(
        f"{candidate.title}\0{candidate.year}".encode()
    ).hexdigest()
    fields = ["title", "identifiers"]
    if candidate.year is not None:
        fields.append("year")
    record_source(
        item,
        provider=candidate.provider,
        reference=candidate.identifier,
        revision=revision,
        url=candidate.source_url,
        fields=fields,
        licence=ATTRIBUTION[candidate.provider],
        show_credit=True,
    )
    return item


def import_candidate(candidate):
    try:
        return _persist(candidate)
    except IdentifierConflict:
        # Another process may have bound the ID while this transaction inserted its item.
        return _persist(candidate)
