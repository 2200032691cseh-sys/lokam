from urllib.parse import urlsplit

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Prefetch, Q

from .identifiers import Namespace, normalize_identifier
from .models import (
    CatalogueItem,
    CatalogueSource,
    ExternalIdentifier,
    ItemKind,
    ItemPersonRole,
    ItemTag,
    SourceProvider,
)

IDENTIFIER_KINDS = {
    Namespace.OPEN_LIBRARY_WORK: ItemKind.BOOK,
    Namespace.OPEN_LIBRARY_EDITION: ItemKind.BOOK_EDITION,
    Namespace.OPEN_LIBRARY_AUTHOR: ItemKind.PERSON,
    Namespace.ISBN: ItemKind.BOOK_EDITION,
    Namespace.TMDB_MOVIE: ItemKind.MOVIE,
    Namespace.TMDB_SHOW: ItemKind.SHOW,
    Namespace.TMDB_PERSON: ItemKind.PERSON,
    Namespace.MUSICBRAINZ_ARTIST: ItemKind.MUSIC_ARTIST,
    Namespace.MUSICBRAINZ_RELEASE: ItemKind.MUSIC_RELEASE,
    Namespace.MUSICBRAINZ_GROUP: ItemKind.MUSIC_ALBUM,
    Namespace.MUSICBRAINZ_RECORDING: ItemKind.MUSIC_RECORDING,
    Namespace.MUSICBRAINZ_WORK: ItemKind.MUSICAL_WORK,
}
SOURCE_HOSTS = {
    SourceProvider.OPEN_LIBRARY: {"openlibrary.org"},
    SourceProvider.TMDB: {"www.themoviedb.org"},
    SourceProvider.WIKIDATA: {"www.wikidata.org"},
    SourceProvider.MUSICBRAINZ: {"musicbrainz.org"},
    SourceProvider.WIKIMEDIA: {"commons.wikimedia.org", "en.wikipedia.org"},
}
PROVENANCE_FIELDS = {
    "title",
    "language",
    "year",
    "aliases",
    "identifiers",
    "credits",
    "subjects",
    "description",
    "relationship",
    "image",
    "publisher",
    "format",
    "publication",
    "countries",
}


class IdentifierConflict(ValidationError):
    """Stable identifiers resolve to different canonical records."""


def resolve_exact(identifiers):
    keys = list(identifiers)
    if not keys:
        return None
    if len(keys) > 16:
        raise ValidationError("Supply at most 16 identifiers per lookup.")
    condition = Q()
    for namespace, value in keys:
        condition |= Q(
            namespace=namespace, value=normalize_identifier(namespace, value)
        )
    item_ids = list(
        ExternalIdentifier.objects.filter(condition, item__owner__isnull=True)
        .values_list("item_id", flat=True)
        .distinct()[:2]
    )
    if len(item_ids) > 1:
        raise IdentifierConflict(
            "These identifiers belong to different catalogue records."
        )
    return CatalogueItem.objects.get(pk=item_ids[0]) if item_ids else None


@transaction.atomic
def bind_identifier(item, namespace, value):
    expected_kind = IDENTIFIER_KINDS.get(namespace)
    if item.owner_id is not None or (
        expected_kind is not None and item.kind != expected_kind
    ):
        raise ValidationError(
            "This identifier cannot be attached to the selected record."
        )
    identifier, _ = ExternalIdentifier.objects.get_or_create(
        namespace=namespace,
        value=normalize_identifier(namespace, value),
        defaults={"item": item},
    )
    if identifier.item_id != item.pk:
        raise IdentifierConflict("This identifier belongs to another catalogue record.")
    return identifier


@transaction.atomic
def record_source(
    item,
    *,
    provider,
    reference,
    revision,
    url,
    fields,
    licence="",
    show_credit=False,
    export_allowed=False,
):
    source_url = urlsplit(url)
    hosts = SOURCE_HOSTS.get(provider)
    if (
        source_url.scheme != "https"
        or not source_url.hostname
        or source_url.username
        or source_url.password
        or source_url.query
        or (hosts is not None and source_url.hostname not in hosts)
        or provider not in SourceProvider.values
        or item.owner_id is not None
    ):
        raise ValidationError("Use an approved source reference on a shared record.")
    field_names = set(fields)
    if (
        not field_names
        or not field_names <= PROVENANCE_FIELDS
        or not revision
        or not reference
    ):
        raise ValidationError(
            "Record a revision, source reference and permitted fields."
        )
    if (show_credit or export_allowed) and not licence:
        raise ValidationError(
            "Record the rights or attribution basis before enabling reuse."
        )
    source, created = CatalogueSource.objects.select_for_update().get_or_create(
        item=item,
        provider=provider,
        reference=reference,
        revision=revision,
        defaults={
            "source_url": url,
            "fields": sorted(field_names),
            "licence": licence,
            "show_credit": show_credit,
            "export_allowed": export_allowed,
        },
    )
    if not created:
        if (
            source.source_url != url
            or source.licence != licence
            or source.export_allowed != export_allowed
        ):
            raise ValidationError(
                "Reusing a revision requires the same source and rights."
            )
        source.fields = sorted(set(source.fields) | field_names)
        source.show_credit = source.show_credit or show_credit
        source.save(update_fields=["fields", "show_credit"])
    return source


def public_items():
    return CatalogueItem.objects.filter(is_public=True, owner__isnull=True)


def public_details():
    credits = ItemPersonRole.objects.select_related("person__item").filter(
        person__item__in=public_items()
    )
    return public_items().prefetch_related(
        Prefetch("credits", queryset=credits, to_attr="public_credits"),
        Prefetch(
            "tags", queryset=ItemTag.objects.select_related("term").order_by("term")
        ),
        "aliases",
        Prefetch(
            "sources",
            queryset=CatalogueSource.objects.filter(show_credit=True)[:8],
            to_attr="public_sources",
        ),
    )
