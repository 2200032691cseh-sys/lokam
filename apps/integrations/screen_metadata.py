from datetime import date

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.catalogue.identifiers import Namespace, normalize_identifier
from apps.catalogue.models import (
    CatalogueItem,
    ItemKind,
    ItemPersonRole,
    ItemTag,
    Movie,
    Person,
    SourceProvider,
    VocabularyTerm,
    normalize_name,
)
from apps.catalogue.services import bind_identifier, record_source, resolve_exact
from apps.jobs.services import active_lease

from .adapters import (
    SCREEN_CLASSES,
    _claim_values,
    _object,
    _title,
    fetch_wikidata_entities,
)
from .http import ProviderUnavailable, get_json

CREDIT_ROLES = {
    "P57": ItemPersonRole.Role.DIRECTOR,
    "P58": ItemPersonRole.Role.WRITER,
    "P161": ItemPersonRole.Role.ACTOR,
    "P86": ItemPersonRole.Role.COMPOSER,
    "P170": ItemPersonRole.Role.CREATOR,
}


def _qid_values(entity, property_id, limit):
    result = []
    for value in _claim_values(entity, property_id)[:limit]:
        try:
            result.append(normalize_identifier(Namespace.WIKIDATA, value.get("id")))
        except ValidationError:
            continue
    return result


def _label(entity):
    labels = _object(entity.get("labels"))
    return _title(_object(labels.get("en")).get("value")) or _title(
        _object(labels.get("mul")).get("value")
    )


def _release(entity):
    values = []
    for value in _claim_values(entity, "P577"):
        time = value.get("time")
        if (
            value.get("precision") == 11
            and isinstance(time, str)
            and time.startswith("+")
        ):
            try:
                values.append(date.fromisoformat(time[1:11]))
            except ValueError:
                continue
    return min(values, default=None)


def fetch_labels(ids, *, fetch=get_json):
    if not ids:
        return {}
    if len(ids) > 24:
        raise ValidationError("Load up to 24 Wikidata labels in one batch.")
    data = fetch(
        "wikidata-labels",
        "/w/api.php",
        params={
            "action": "wbgetentities",
            "ids": "|".join(ids),
            "languages": "en|mul",
            "props": "info|labels",
            "format": "json",
        },
        headers={"User-Agent": "Lokam/0.1"},
    )
    entities = data.get("entities")
    if not isinstance(entities, dict):
        raise ProviderUnavailable("Wikidata did not return the related labels.")
    return entities


@transaction.atomic
def _store_credit(item, qid, entity, role, position):
    title = _label(entity)
    revision = entity.get("lastrevid")
    if not title or type(revision) is not int:
        return
    person_item = resolve_exact([(Namespace.WIKIDATA, qid)])
    if person_item is None:
        person_item = CatalogueItem.objects.create(
            kind=ItemKind.PERSON, title=title, is_public=True
        )
        bind_identifier(person_item, Namespace.WIKIDATA, qid)
    if person_item.kind != ItemKind.PERSON:
        return
    person, _ = Person.objects.get_or_create(item=person_item)
    ItemPersonRole.objects.get_or_create(
        person=person, item=item, role=role, defaults={"position": position}
    )
    record_source(
        person_item,
        provider=SourceProvider.WIKIDATA,
        reference=qid,
        revision=str(revision),
        url=f"https://www.wikidata.org/wiki/{qid}",
        fields={"title", "identifiers"},
        licence="CC0 structured data",
        show_credit=True,
    )


def enrich_movie(
    item,
    identifier,
    *,
    fetch_entities=fetch_wikidata_entities,
    get_labels=fetch_labels,
    still_active=lambda: True,
):
    identifier = normalize_identifier(Namespace.WIKIDATA, identifier)
    entity = _object(fetch_entities([identifier]).get(identifier))
    revision = entity.get("lastrevid")
    if (
        type(revision) is not int
        or not set(_qid_values(entity, "P31", 12)) & SCREEN_CLASSES[ItemKind.MOVIE]
    ):
        raise ProviderUnavailable("Wikidata did not return a current film revision.")
    roles = [
        (qid, role, position)
        for prop, role in CREDIT_ROLES.items()
        for position, qid in enumerate(
            _qid_values(entity, prop, 6 if prop == "P161" else 2)
        )
    ]
    countries = _qid_values(entity, "P495", 3)
    languages = _qid_values(entity, "P364", 3)
    genres = _qid_values(entity, "P136", 4)
    ids = list(
        dict.fromkeys([*countries, *languages, *genres, *(qid for qid, _, _ in roles)])
    )
    entities = get_labels(ids[:24])
    names = {qid: _label(_object(entities.get(qid))) for qid in ids}
    if not still_active():
        return
    with transaction.atomic():
        first_release = _release(entity)
        Movie.objects.update_or_create(
            item=item,
            defaults={
                "release_date": first_release,
                "countries": ", ".join(
                    names[qid] for qid in countries if names.get(qid)
                )[:240],
                "languages": ", ".join(
                    names[qid] for qid in languages if names.get(qid)
                )[:240],
            },
        )
        for qid, role, position in roles:
            _store_credit(item, qid, _object(entities.get(qid)), role, position)
        for qid in genres:
            if name := names.get(qid):
                name = name[:160]
                term, _ = VocabularyTerm.objects.get_or_create(
                    kind=VocabularyTerm.Kind.GENRE,
                    key=normalize_name(name),
                    defaults={"label": name},
                )
                ItemTag.objects.get_or_create(item=item, term=term)
        if "Q93204" in _qid_values(entity, "P31", 12):
            item.subtype = "documentary"
            item.save(update_fields=["subtype"])
        record_source(
            item,
            provider=SourceProvider.WIKIDATA,
            reference=identifier,
            revision=str(revision),
            url=f"https://www.wikidata.org/wiki/{identifier}",
            fields={"publication", "credits", "subjects", "language", "countries"},
            licence="CC0 structured data",
            show_credit=True,
        )


def enrich_screen_job(job):
    item = CatalogueItem.objects.filter(
        pk=job.object_id, kind=ItemKind.MOVIE, is_public=True
    ).first()
    if item is None:
        return
    identifier = (
        item.external_ids.filter(namespace=Namespace.WIKIDATA)
        .values_list("value", flat=True)
        .first()
    )
    if identifier:
        enrich_movie(
            item,
            identifier,
            still_active=lambda: active_lease(job.pk, job.lease_token).exists(),
        )
