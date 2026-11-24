from urllib.parse import urlsplit

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.catalogue.identifiers import Namespace, normalize_identifier
from apps.catalogue.models import ItemKind, Predicate, SourceProvider
from apps.catalogue.relationships import TARGET_KINDS, record_edge
from apps.catalogue.services import bind_identifier, record_source, resolve_exact

from .adapters import fetch_wikidata_entities

PROPERTIES = {
    "P144": Predicate.ADAPTED_FROM,
    "P4969": Predicate.ADAPTED_FROM,
    "P50": Predicate.WRITTEN_BY,
    "P57": Predicate.DIRECTED_BY,
    "P170": Predicate.CREATED_BY,
    "P86": Predicate.COMPOSED_BY,
    "P175": Predicate.PERFORMED_BY,
    "P674": Predicate.FEATURES_CHARACTER,
    "P840": Predicate.SET_IN,
    "P179": Predicate.SERIES,
    "P407": Predicate.LANGUAGE,
    "P364": Predicate.LANGUAGE,
    "P131": Predicate.LOCATED_IN,
    "P2596": Predicate.CULTURE,
}


def _mapping(value):
    return value if isinstance(value, dict) else {}


def _statements(entity, prop):
    entries = _mapping(entity.get("claims")).get(prop, [])
    if not isinstance(entries, list):
        return
    for statement in entries[:40]:
        row = _mapping(statement)
        if row and row.get("rank") in {"normal", "preferred"}:
            value = _mapping(_mapping(row.get("mainsnak")).get("datavalue")).get(
                "value"
            )
            yield row, value


def _exact_local_item(qid, entity):
    identifiers = [(Namespace.WIKIDATA, qid)]
    for _, value in _statements(entity, "P648"):
        if not isinstance(value, str):
            continue
        try:
            identifiers.append(
                (
                    Namespace.OPEN_LIBRARY_WORK,
                    normalize_identifier(Namespace.OPEN_LIBRARY_WORK, value),
                )
            )
        except ValidationError:
            continue
        if len(identifiers) >= 8:
            break
    item = resolve_exact(identifiers)
    if item is not None and (len(identifiers) == 1 or item.kind == ItemKind.BOOK):
        bind_identifier(item, Namespace.WIKIDATA, qid)
        return item
    return None


def _reference(statement):
    references = statement.get("references", [])
    if not isinstance(references, list):
        return ""
    for ref in references[:8]:
        urls = _mapping(_mapping(ref).get("snaks")).get("P854", [])
        if not isinstance(urls, list):
            continue
        for url in urls[:5]:
            value = _mapping(_mapping(url).get("datavalue")).get("value")
            if isinstance(value, str) and len(value) <= 500:
                try:
                    parts = urlsplit(value)
                except ValueError:
                    continue
                if parts.scheme == "https" and parts.hostname and not parts.username:
                    return value
    return ""


@transaction.atomic
def import_wikidata_edges(entities):
    records = {}
    for qid, raw in entities.items():
        entity = _mapping(raw)
        if entity.get("id") != qid or entity.get("missing") is not None:
            continue
        if item := _exact_local_item(qid, entity):
            records[qid] = (item, entity)

    edges = []
    for qid, (item, entity) in records.items():
        revision = entity.get("lastrevid")
        if type(revision) is not int or revision <= 0:
            continue
        for prop, predicate in PROPERTIES.items():
            for statement, value in _statements(entity, prop):
                target_id = _mapping(value).get("id")
                statement_id = statement.get("id")
                if not isinstance(target_id, str) or not (
                    isinstance(statement_id, str)
                    and statement_id.startswith(f"{qid}$")
                    and len(statement_id) <= 100
                ):
                    continue
                target_record = records.get(target_id)
                if target_record is None:
                    continue
                target = target_record[0]
                subject, obj = (target, item) if prop == "P4969" else (item, target)
                if subject.pk == obj.pk or obj.kind not in TARGET_KINDS[predicate]:
                    continue
                source = record_source(
                    item,
                    provider=SourceProvider.WIKIDATA,
                    reference=qid,
                    revision=str(revision),
                    url=f"https://www.wikidata.org/wiki/{qid}",
                    fields={"relationship"},
                    licence="CC0 structured data",
                    show_credit=True,
                )
                # Qualifiers are recorded as property IDs. Interpretation stays part of review.
                qualifiers = [
                    key
                    for key in _mapping(statement.get("qualifiers"))
                    if key.startswith("P")
                ][:12]
                edges.append(
                    record_edge(
                        subject,
                        predicate,
                        obj,
                        source=source,
                        statement_id=statement_id,
                        reference_url=_reference(statement),
                        qualifiers={
                            "property": prop,
                            "qualifier_properties": qualifiers,
                            "rank": statement["rank"],
                        },
                    )
                )
    return edges


def sync_wikidata_edges(ids, *, fetch=fetch_wikidata_entities):
    return import_wikidata_edges(fetch(ids))
