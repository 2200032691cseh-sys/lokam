import re
from dataclasses import dataclass

from django.core.exceptions import ValidationError

from apps.catalogue.identifiers import Namespace, normalize_identifier
from apps.catalogue.models import ItemKind, SourceProvider

from .http import ProviderUnavailable, get_json

SCREEN_CLASSES = {
    ItemKind.MOVIE: {"Q11424", "Q202866", "Q93204", "Q24862"},
    ItemKind.SHOW: {"Q5398426", "Q1259759", "Q15416"},
}


@dataclass(frozen=True)
class Candidate:
    provider: str
    namespace: str
    identifier: str
    kind: str
    title: str
    year: int | None
    creators: tuple[str, ...] = ()
    revision: str = ""
    authors: tuple[tuple[str, str], ...] = ()
    subjects: tuple[str, ...] = ()

    @property
    def source_url(self):
        if self.provider == SourceProvider.OPEN_LIBRARY:
            return f"https://openlibrary.org/works/{self.identifier}"
        return f"https://www.wikidata.org/wiki/{self.identifier}"


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
    authors = []
    author_keys = row.get("author_key")
    if (
        isinstance(names, list)
        and isinstance(author_keys, list)
        and len(names) == len(author_keys)
    ):
        for name, key in zip(names[:5], author_keys[:5]):
            if public_name := _title(name):
                try:
                    authors.append(
                        (
                            public_name,
                            normalize_identifier(Namespace.OPEN_LIBRARY_AUTHOR, key),
                        )
                    )
                except ValidationError:
                    continue
    return Candidate(
        SourceProvider.OPEN_LIBRARY,
        Namespace.OPEN_LIBRARY_WORK,
        identifier,
        ItemKind.BOOK,
        title,
        _year(row.get("first_publish_year")),
        creators,
        authors=tuple(authors),
        subjects=tuple(
            label
            for raw in (row.get("subject") or [])[:8]
            if isinstance(raw, str) and (label := _title(raw)[:100])
        )
        if isinstance(row.get("subject"), list)
        else (),
    )


def _object(value):
    return value if isinstance(value, dict) else {}


def _claim_values(entity, property_id):
    entries = _object(entity.get("claims")).get(property_id)
    if not isinstance(entries, list):
        return []
    values = []
    for entry in entries[:80]:
        entry = _object(entry)
        if entry.get("rank") == "deprecated":
            continue
        value = _object(_object(entry.get("mainsnak")).get("datavalue")).get("value")
        if isinstance(value, dict):
            values.append(value)
    return values


def _wikidata_candidate(identifier, entity, kind, fallback_label):
    classes = {
        value.get("id")
        for value in _claim_values(entity, "P31")
        if isinstance(value.get("id"), str)
    }
    labels = _object(entity.get("labels"))
    title = (
        _title(_object(labels.get("en")).get("value"))
        or _title(_object(labels.get("mul")).get("value"))
        or _title(fallback_label)
    )
    if not title or not classes & SCREEN_CLASSES[kind]:
        return None
    years = []
    for property_id in ("P577", "P580", "P571"):
        for value in _claim_values(entity, property_id):
            precision = value.get("precision")
            raw = value.get("time")
            if type(precision) is int and precision >= 9 and isinstance(raw, str):
                match = re.match(r"^\+([0-9]{4})-", raw)
                if match and (year := _year(int(match[1]))):
                    years.append(year)
        if years:
            break
    revision = entity.get("lastrevid")
    return Candidate(
        SourceProvider.WIKIDATA,
        Namespace.WIKIDATA,
        identifier,
        kind,
        title,
        min(years, default=None),
        revision=str(revision) if type(revision) is int else "",
    )


def _search_wikidata(kind, query, fetch):
    headers = {"User-Agent": "Lokam/0.1"}
    matches = fetch(
        "wikidata-search",
        "/w/api.php",
        params={
            "action": "wbsearchentities",
            "search": query,
            "language": "en",
            "type": "item",
            "limit": 8,
            "format": "json",
        },
        headers=headers,
    )
    keys = {}
    for entry in _rows(matches, "search"):
        try:
            key = normalize_identifier(Namespace.WIKIDATA, entry.get("id"))
        except ValidationError:
            continue
        keys.setdefault(key, entry.get("label"))
    if not keys:
        return []
    entities = fetch_wikidata_entities(keys, fetch=fetch)
    return [
        match
        for key, fallback_label in keys.items()
        if (
            match := _wikidata_candidate(
                key, _object(entities.get(key)), kind, fallback_label
            )
        )
    ]


def fetch_wikidata_entities(ids, *, fetch=get_json):
    keys = list(
        dict.fromkeys(normalize_identifier(Namespace.WIKIDATA, key) for key in ids)
    )
    if not 1 <= len(keys) <= 8:
        raise ValidationError("Query between one and eight Wikidata entity IDs.")
    data = fetch(
        "wikidata-read",
        "/w/api.php",
        params={
            "action": "wbgetentities",
            "ids": "|".join(keys),
            "languages": "en|mul",
            "props": "info|labels|claims",
            "format": "json",
        },
        headers={"User-Agent": "Lokam/0.1"},
    )
    entities = data.get("entities")
    if not isinstance(entities, dict):
        raise ProviderUnavailable("Wikidata did not return structured entity data.")
    return entities


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
                "fields": "key,title,author_name,author_key,first_publish_year,subject",
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
    return _search_wikidata(kind, query, fetch)
