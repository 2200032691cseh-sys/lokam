from datetime import date
from hashlib import sha256

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.catalogue.identifiers import Namespace, normalize_identifier
from apps.catalogue.models import (
    CatalogueItem,
    ItemKind,
    ItemPersonRole,
    ItemTag,
    Person,
    SourceProvider,
    TVEpisode,
    TVSeason,
    TVShow,
    TVShowCharacter,
    VocabularyTerm,
    normalize_name,
)
from apps.catalogue.services import bind_identifier, record_source, resolve_exact
from apps.jobs.services import active_lease, enqueue

from .adapters import _object, _title, fetch_wikidata_entities
from .http import ProviderUnavailable, get_json
from .screen_metadata import _qid_values, _store_credit, fetch_labels
from .wikidata_graph import _statements

LICENCE = "CC BY-SA (TVmaze)"
HEADERS = {"User-Agent": "Lokam/0.1"}


def _date(value):
    try:
        return date.fromisoformat(value) if isinstance(value, str) else None
    except ValueError:
        return None


def _rows(value, limit):
    return (
        [_object(row) for row in value[:limit] if isinstance(row, dict)]
        if isinstance(value, list)
        else []
    )


def _record(item, namespace, identifier, route, fields, values):
    return record_source(
        item,
        provider=SourceProvider.TVMAZE,
        reference=f"{namespace}:{identifier}",
        revision=sha256(repr(values).encode()).hexdigest(),
        url=f"https://www.tvmaze.com/{route}/{identifier}",
        fields=fields,
        licence=LICENCE,
        show_credit=True,
    )


def _canonical(namespace, raw_id, kind, title, year=None):
    identifier = normalize_identifier(namespace, raw_id)
    item = resolve_exact([(namespace, identifier)])
    if item is None:
        item = CatalogueItem.objects.create(
            kind=kind, title=title, year=year, is_public=True
        )
        bind_identifier(item, namespace, identifier)
    if item.kind != kind:
        raise ValidationError("TVmaze identifier conflicts with the catalogue.")
    return item, identifier


@transaction.atomic
def _store_season(show, row):
    number = row.get("number")
    if type(number) is not int or not 0 <= number <= 32767:
        return
    title = _title(row.get("name")) or f"Season {number} of {show.item.title}"[:240]
    premiere = _date(row.get("premiereDate"))
    item, identifier = _canonical(
        Namespace.TVMAZE_SEASON,
        row.get("id"),
        ItemKind.SEASON,
        title,
        premiere.year if premiere else None,
    )
    same_position = show.seasons.filter(number=number).exclude(item=item).exists()
    if same_position:
        raise ValidationError("Season number already belongs to another item.")
    season, _ = TVSeason.objects.get_or_create(
        item=item, defaults={"show": show, "number": number, "premiere_date": premiere}
    )
    if season.show_id != show.pk:
        raise ValidationError("Season belongs to another show.")
    _record(
        item,
        Namespace.TVMAZE_SEASON,
        identifier,
        "seasons",
        {"title", "identifiers", "publication"},
        (title, premiere, number),
    )
    enqueue("enrich-tv-season", season.pk, f"enrich-tv-season:{season.pk}")


@transaction.atomic
def _store_cast(show, row, position):
    member, character = _object(row.get("person")), _object(row.get("character"))
    name, character_name = _title(member.get("name")), _title(character.get("name"))
    if not name or not character_name:
        return
    actor, actor_id = _canonical(
        Namespace.TVMAZE_PERSON, member.get("id"), ItemKind.PERSON, name
    )
    role, role_id = _canonical(
        Namespace.TVMAZE_CHARACTER,
        character.get("id"),
        ItemKind.CHARACTER,
        character_name,
    )
    _record(
        actor,
        Namespace.TVMAZE_PERSON,
        actor_id,
        "people",
        {"title", "identifiers"},
        name,
    )
    _record(
        role,
        Namespace.TVMAZE_CHARACTER,
        role_id,
        "characters",
        {"title", "identifiers"},
        character_name,
    )
    person, _ = Person.objects.get_or_create(item=actor)
    ItemPersonRole.objects.get_or_create(
        item=show.item,
        person=person,
        role=ItemPersonRole.Role.ACTOR,
        detail=character_name[:160],
        defaults={"position": position},
    )
    TVShowCharacter.objects.get_or_create(show=show, character=role)


def enrich_show(
    item,
    qid,
    *,
    fetch_entities=fetch_wikidata_entities,
    fetch=get_json,
    get_labels=fetch_labels,
    still_active=lambda: True,
):
    qid = normalize_identifier(Namespace.WIKIDATA, qid)
    entity = _object(fetch_entities([qid]).get(qid))
    identifiers = set()
    for _, value in _statements(entity, "P8600"):
        try:
            identifiers.add(normalize_identifier(Namespace.TVMAZE_SHOW, value))
        except ValidationError:
            continue
    if len(identifiers) != 1:
        return None
    identifier = identifiers.pop()
    data = fetch(
        "tvmaze",
        f"/shows/{identifier}",
        params={"embed[]": ["seasons", "cast"]},
        headers=HEADERS,
    )
    if normalize_identifier(Namespace.TVMAZE_SHOW, data.get("id")) != identifier:
        raise ProviderUnavailable("TVmaze returned an unexpected series.")
    if not still_active():
        return None
    embedded = _object(data.get("_embedded"))
    station = _object(data.get("network")) or _object(data.get("webChannel"))
    premiere = _date(data.get("premiered"))
    country = _title(_object(station.get("country")).get("name"))
    language = _title(data.get("language"))
    creator_ids = _qid_values(entity, "P170", 4)
    creators = get_labels(creator_ids)
    with transaction.atomic():
        bind_identifier(item, Namespace.TVMAZE_SHOW, identifier)
        show, _ = TVShow.objects.update_or_create(
            item=item,
            defaults={
                "premiere_date": premiere,
                "countries": country,
                "languages": language,
            },
        )
        if (
            isinstance(data.get("type"), str)
            and data["type"].casefold() == "documentary"
        ):
            item.subtype = "documentary"
            item.save(update_fields=["subtype"])
        for position, creator_id in enumerate(creator_ids):
            _store_credit(
                item,
                creator_id,
                _object(creators.get(creator_id)),
                ItemPersonRole.Role.CREATOR,
                position,
            )
        for row in _rows(embedded.get("seasons"), 50):
            try:
                _store_season(show, row)
            except ValidationError:
                continue
        for position, row in enumerate(_rows(embedded.get("cast"), 25)):
            try:
                _store_cast(show, row, position)
            except ValidationError:
                continue
        genres = data.get("genres", [])
        if isinstance(genres, list):
            for raw in genres[:8]:
                if name := _title(raw)[:160]:
                    term, _ = VocabularyTerm.objects.get_or_create(
                        kind=VocabularyTerm.Kind.GENRE,
                        key=normalize_name(name),
                        defaults={"label": name},
                    )
                    ItemTag.objects.get_or_create(item=item, term=term)
        _record(
            item,
            Namespace.TVMAZE_SHOW,
            identifier,
            "shows",
            {
                "identifiers",
                "publication",
                "countries",
                "language",
                "credits",
                "subjects",
            },
            (data.get("updated"), premiere, country, language),
        )
    return show


@transaction.atomic
def _store_episode(season, row):
    title = _title(row.get("name"))
    number = row.get("number")
    if not title or row.get("season") != season.number:
        return
    number = number if type(number) is int and 0 <= number <= 32767 else None
    aired = _date(row.get("airdate"))
    item, identifier = _canonical(
        Namespace.TVMAZE_EPISODE,
        row.get("id"),
        ItemKind.EPISODE,
        title,
        aired.year if aired else None,
    )
    if (
        number is not None
        and season.episodes.filter(number=number).exclude(item=item).exists()
    ):
        raise ValidationError("Episode number already belongs to another item.")
    episode, _ = TVEpisode.objects.get_or_create(
        item=item, defaults={"season": season, "number": number, "air_date": aired}
    )
    if episode.season_id != season.pk:
        raise ValidationError("Episode belongs to another season.")
    _record(
        item,
        Namespace.TVMAZE_EPISODE,
        identifier,
        "episodes",
        {"title", "identifiers", "publication"},
        (title, aired, number),
    )


def enrich_season(season, identifier, *, fetch=get_json, still_active=lambda: True):
    identifier = normalize_identifier(Namespace.TVMAZE_SEASON, identifier)
    data = fetch(
        "tvmaze", f"/seasons/{identifier}/episodes", headers=HEADERS, expected=list
    )
    for row in _rows(data, 120):
        if not still_active():
            break
        try:
            _store_episode(season, row)
        except ValidationError:
            continue


def _identifier(item, namespace):
    return (
        item.external_ids.filter(namespace=namespace)
        .values_list("value", flat=True)
        .first()
    )


def enrich_show_job(job):
    item = CatalogueItem.objects.filter(
        pk=job.object_id, kind=ItemKind.SHOW, is_public=True
    ).first()
    if item and (qid := _identifier(item, Namespace.WIKIDATA)):
        enrich_show(
            item,
            qid,
            still_active=lambda: active_lease(job.pk, job.lease_token).exists(),
        )


def enrich_season_job(job):
    season = (
        TVSeason.objects.select_related("item")
        .filter(pk=job.object_id, item__is_public=True, show__item__is_public=True)
        .first()
    )
    if season and (identifier := _identifier(season.item, Namespace.TVMAZE_SEASON)):
        enrich_season(
            season,
            identifier,
            still_active=lambda: active_lease(job.pk, job.lease_token).exists(),
        )
