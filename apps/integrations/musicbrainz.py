from hashlib import sha256
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.catalogue.identifiers import normalize_identifier
from apps.catalogue.models import (
    CatalogueItem,
    ItemKind,
    ItemPersonRole,
    MusicAlbum,
    MusicalWork,
    MusicArtist,
    MusicLink,
    MusicRecording,
    MusicRelease,
    Person,
    SourceProvider,
)
from apps.catalogue.services import bind_identifier, record_source, resolve_exact
from apps.jobs.services import active_lease

from .adapters import MUSIC_ENDPOINTS, MUSIC_USER_AGENT, _object, _title
from .http import ProviderUnavailable, get_json

MUSIC_MODELS = {
    ItemKind.MUSIC_ARTIST: MusicArtist,
    ItemKind.MUSIC_ALBUM: MusicAlbum,
    ItemKind.MUSIC_RELEASE: MusicRelease,
    ItemKind.MUSIC_RECORDING: MusicRecording,
    ItemKind.MUSICAL_WORK: MusicalWork,
}
LICENSE = "MusicBrainz core data (CC0)"
HEADERS = {"User-Agent": MUSIC_USER_AGENT}
INCLUDES = {
    ItemKind.MUSIC_ARTIST: "url-rels",
    ItemKind.MUSIC_ALBUM: "artist-credits+url-rels",
    ItemKind.MUSIC_RELEASE: "artist-credits+release-groups+url-rels",
    ItemKind.MUSIC_RECORDING: "artist-credits+artist-rels+work-rels+url-rels",
    ItemKind.MUSICAL_WORK: "artist-rels+url-rels",
}


def _records(value, limit=12):
    return (
        [row for row in value[:limit] if isinstance(row, dict)]
        if isinstance(value, list)
        else []
    )


def _capture(item, identifier, values, *, fields):
    entity, _ = MUSIC_ENDPOINTS[item.kind]
    return record_source(
        item,
        provider=SourceProvider.MUSICBRAINZ,
        reference=f"{entity}:{identifier}",
        revision=sha256(repr(values).encode()).hexdigest(),
        url=f"https://musicbrainz.org/{entity}/{identifier}",
        fields=fields,
        licence=LICENSE,
        show_credit=True,
    )


@transaction.atomic
def _ensure_item(kind, identifier, title):
    _, namespace = MUSIC_ENDPOINTS[kind]
    model = MUSIC_MODELS[kind]
    identifier = normalize_identifier(namespace, identifier)
    item = resolve_exact([(namespace, identifier)])
    if item is None:
        item = CatalogueItem.objects.create(kind=kind, title=title, is_public=True)
        bind_identifier(item, namespace, identifier)
    if item.kind != kind:
        raise ValidationError(
            "This MusicBrainz identifier has a different catalogue type."
        )
    model.objects.get_or_create(item=item)
    _capture(item, identifier, (title,), fields={"title", "identifiers"})
    return item


def _credit(item, artist, role, position):
    name = _title(artist.get("name"))
    if not name:
        return
    try:
        artist_item = _ensure_item(ItemKind.MUSIC_ARTIST, artist.get("id"), name)
    except ValidationError:
        return
    person, _ = Person.objects.get_or_create(item=artist_item)
    ItemPersonRole.objects.get_or_create(
        person=person, item=item, role=role, defaults={"position": position}
    )


def listening_link(url):
    try:
        parts = urlsplit(url)
    except (TypeError, ValueError):
        return None
    if (
        parts.scheme != "https"
        or parts.username
        or parts.password
        or not parts.hostname
    ):
        return None
    hosts = {
        "open.spotify.com": "Spotify",
        "music.apple.com": "Apple Music",
        "music.youtube.com": "YouTube Music",
        "www.deezer.com": "Deezer",
        "tidal.com": "TIDAL",
    }
    label = hosts.get(parts.hostname)
    if label is None:
        return None
    query = ""
    if parts.hostname == "music.youtube.com":
        try:
            values = parse_qs(parts.query, max_num_fields=8)
        except ValueError:
            return None
        if values.get("v"):
            query = urlencode({"v": values["v"][0][:24]})
    return label, urlunsplit(("https", parts.hostname, parts.path, query, ""))[:500]


def enrich_music(item, identifier, *, fetch=get_json, still_active=lambda: True):
    entity, namespace = MUSIC_ENDPOINTS[item.kind]
    model = MUSIC_MODELS[item.kind]
    identifier = normalize_identifier(namespace, identifier)
    data = fetch(
        "musicbrainz",
        f"/ws/2/{entity}/{identifier}",
        params={"fmt": "json", "inc": INCLUDES[item.kind]},
        headers=HEADERS,
    )
    if normalize_identifier(namespace, data.get("id")) != identifier:
        raise ProviderUnavailable("MusicBrainz returned an unexpected identifier.")
    if not still_active():
        return
    relations = _records(data.get("relations"), 40)
    with transaction.atomic():
        attributes = {}
        if item.kind == ItemKind.MUSIC_ARTIST:
            attributes["artist_type"] = _title(data.get("type"))[:60]
        if item.kind == ItemKind.MUSIC_ALBUM:
            attributes["release_type"] = _title(data.get("primary-type"))[:60]
        if item.kind == ItemKind.MUSIC_RELEASE:
            attributes["release_date"] = _title(data.get("date"))[:24]
            attributes["country"] = _title(data.get("country"))[:24]
            group = _object(data.get("release-group"))
            if title := _title(group.get("title")):
                album = _ensure_item(ItemKind.MUSIC_ALBUM, group.get("id"), title)
                attributes["album_id"] = MusicAlbum.objects.get(item=album).pk
        if item.kind == ItemKind.MUSIC_RECORDING:
            milliseconds = data.get("length")
            if type(milliseconds) is int and 0 <= milliseconds <= 2_147_483_647:
                attributes["duration_ms"] = milliseconds
            for relation in relations:
                work = _object(relation.get("work"))
                if title := _title(work.get("title")):
                    target = _ensure_item(ItemKind.MUSICAL_WORK, work.get("id"), title)
                    attributes["work_id"] = MusicalWork.objects.get(item=target).pk
                    break
        model.objects.update_or_create(item=item, defaults=attributes)
        for position, credit in enumerate(_records(data.get("artist-credit"), 10)):
            _credit(
                item,
                _object(credit.get("artist")),
                ItemPersonRole.Role.PERFORMER,
                position,
            )
        for position, relation in enumerate(relations):
            artist = _object(relation.get("artist"))
            role = {
                "composer": ItemPersonRole.Role.COMPOSER,
                "performer": ItemPersonRole.Role.PERFORMER,
            }.get(relation.get("type"))
            if role and artist:
                _credit(item, artist, role, position)
            resource = _object(relation.get("url")).get("resource")
            if resource and (link := listening_link(resource)):
                label, url = link
                MusicLink.objects.get_or_create(
                    item=item, url=url, defaults={"service": label}
                )
        _capture(
            item,
            identifier,
            (attributes, data.get("id"), data.get("title")),
            fields={"identifiers", "credits", "relationship", "publication"},
        )


def enrich_music_job(job):
    item = CatalogueItem.objects.filter(
        pk=job.object_id, kind__in=MUSIC_MODELS, is_public=True
    ).first()
    if item is None:
        return
    _, namespace = MUSIC_ENDPOINTS[item.kind]
    identifier = (
        item.external_ids.filter(namespace=namespace)
        .values_list("value", flat=True)
        .first()
    )
    if identifier:
        enrich_music(
            item,
            identifier,
            still_active=lambda: active_lease(job.pk, job.lease_token).exists(),
        )
