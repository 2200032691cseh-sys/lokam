import hashlib

from django.db import transaction

from apps.catalogue.identifiers import Namespace
from apps.catalogue.models import (
    Book,
    CatalogueItem,
    ItemKind,
    ItemPersonRole,
    ItemTag,
    Person,
    SourceProvider,
    VocabularyTerm,
    normalize_name,
)
from apps.catalogue.services import (
    IdentifierConflict,
    bind_identifier,
    record_source,
    resolve_exact,
)
from apps.jobs.services import enqueue

ATTRIBUTION = {
    SourceProvider.OPEN_LIBRARY: "Open Library catalogue metadata",
    SourceProvider.WIKIDATA: "CC0 structured data",
}


@transaction.atomic
def _attach_author(work, name, identifier, position):
    item = resolve_exact([(Namespace.OPEN_LIBRARY_AUTHOR, identifier)])
    if item is None:
        item = CatalogueItem.objects.create(
            kind=ItemKind.PERSON, title=name, is_public=True
        )
        bind_identifier(item, Namespace.OPEN_LIBRARY_AUTHOR, identifier)
    if item.kind != ItemKind.PERSON:
        raise IdentifierConflict(
            "An author identifier belongs to a different record type."
        )
    person, _ = Person.objects.get_or_create(item=item)
    ItemPersonRole.objects.get_or_create(
        item=work,
        person=person,
        role=ItemPersonRole.Role.AUTHOR,
        defaults={"position": position},
    )
    record_source(
        item,
        provider=SourceProvider.OPEN_LIBRARY,
        reference=identifier,
        revision=hashlib.sha256(name.encode()).hexdigest(),
        url=f"https://openlibrary.org/authors/{identifier}",
        fields={"title", "identifiers"},
        licence=ATTRIBUTION[SourceProvider.OPEN_LIBRARY],
        show_credit=True,
    )


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
    values = (
        candidate.title,
        candidate.year,
        tuple(tuple(pair) for pair in candidate.authors),
        tuple(candidate.subjects),
    )
    revision = candidate.revision or hashlib.sha256(repr(values).encode()).hexdigest()
    fields = ["title", "identifiers"]
    if candidate.year is not None:
        fields.append("year")
    if candidate.provider == SourceProvider.OPEN_LIBRARY and item.kind == ItemKind.BOOK:
        Book.objects.get_or_create(item=item)
        for position, (name, identifier) in enumerate(candidate.authors):
            try:
                _attach_author(item, name, identifier, position)
            except IdentifierConflict:
                continue
            if "credits" not in fields:
                fields.append("credits")
        for label in candidate.subjects:
            term, _ = VocabularyTerm.objects.get_or_create(
                kind=VocabularyTerm.Kind.TAG,
                key=normalize_name(label),
                defaults={"label": label},
            )
            ItemTag.objects.get_or_create(item=item, term=term)
        if candidate.subjects:
            fields.append("subjects")
        if item.is_public:
            enqueue("enrich-book", item.pk, f"enrich-book:{item.pk}")
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
