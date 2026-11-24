import re
from dataclasses import dataclass

from django.conf import settings
from django.core.exceptions import ValidationError

from apps.catalogue.identifiers import Namespace, normalize_identifier
from apps.catalogue.models import ItemKind, SourceProvider

from .http import ProviderCredentialsRequired, ProviderUnavailable, get_json


@dataclass(frozen=True)
class Candidate:
    provider: str
    namespace: str
    identifier: str
    kind: str
    title: str
    year: int | None
    creators: tuple[str, ...] = ()

    @property
    def source_url(self):
        if self.provider == SourceProvider.OPEN_LIBRARY:
            return f"https://openlibrary.org/works/{self.identifier}"
        entity = "movie" if self.kind == ItemKind.MOVIE else "tv"
        return f"https://www.themoviedb.org/{entity}/{self.identifier}"


def _title(value):
    if not isinstance(value, str):
        return ""
    return " ".join(value.split())[:240]


def _year(value):
    if type(value) is int and 1 <= value <= 9999:
        return value
    if isinstance(value, str) and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        return int(value[:4]) or None
    return None


def _rows(data, key):
    rows = data.get(key)
    if not isinstance(rows, list):
        raise ProviderUnavailable(
            "The provider returned an unexpected catalogue format."
        )
    return [row for row in rows[:10] if isinstance(row, dict)]


def _open_library_row(row):
    title = _title(row.get("title"))
    if not title:
        return None
    try:
        identifier = normalize_identifier(Namespace.OPEN_LIBRARY_WORK, row.get("key"))
    except ValidationError:
        return None
    names = row.get("author_name")
    creators = (
        tuple(filter(None, map(_title, names[:5]))) if isinstance(names, list) else ()
    )
    return Candidate(
        SourceProvider.OPEN_LIBRARY,
        Namespace.OPEN_LIBRARY_WORK,
        identifier,
        ItemKind.BOOK,
        title,
        _year(row.get("first_publish_year")),
        creators,
    )


def _tmdb_row(row, kind):
    movie = kind == ItemKind.MOVIE
    title = _title(row.get("title" if movie else "name"))
    namespace = Namespace.TMDB_MOVIE if movie else Namespace.TMDB_SHOW
    if not title or row.get("adult") is True:
        return None
    try:
        identifier = normalize_identifier(namespace, row.get("id"))
    except ValidationError:
        return None
    return Candidate(
        SourceProvider.TMDB,
        namespace,
        identifier,
        kind,
        title,
        _year(row.get("release_date" if movie else "first_air_date")),
    )


def search_external(kind, query, *, fetch=get_json):
    query = " ".join(query.split())
    if not 1 <= len(query) <= 120:
        raise ValidationError("Enter a search phrase up to 120 characters.")
    if kind == ItemKind.BOOK:
        data = fetch(
            SourceProvider.OPEN_LIBRARY,
            "/search.json",
            params={
                "title": query,
                "fields": "key,title,author_name,first_publish_year",
                "limit": 10,
            },
            headers={"User-Agent": "Lokam/0.1"},
        )
        return [
            candidate
            for row in _rows(data, "docs")
            if (candidate := _open_library_row(row))
        ]
    if kind not in {ItemKind.MOVIE, ItemKind.SHOW}:
        raise ValidationError("External search is unavailable for this catalogue type.")
    token = settings.LOKAM_TMDB_TOKEN
    if not token:
        raise ProviderCredentialsRequired(
            "TMDB is disabled until credentials are configured."
        )
    entity = "movie" if kind == ItemKind.MOVIE else "tv"
    data = fetch(
        SourceProvider.TMDB,
        f"/3/search/{entity}",
        params={"query": query, "include_adult": "false", "page": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    return [
        candidate
        for row in _rows(data, "results")
        if (candidate := _tmdb_row(row, kind))
    ]
