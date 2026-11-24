from collections import defaultdict
from dataclasses import dataclass

from django.db.models import Q

from apps.catalogue.models import CatalogueItem, ItemTag, Predicate
from apps.catalogue.relationships import supported_public_edges
from apps.catalogue.services import public_items
from apps.libraries.models import SaveState, UserItem

SEED_LIMIT = 40
EDGE_LIMIT = 240
TAG_LIMIT = 160
RESULT_LIMIT = 24
TENTATIVE = {
    SaveState.WANT_READ,
    SaveState.WANT_WATCH,
    SaveState.WANT_VISIT,
    SaveState.INTEREST,
}


@dataclass(frozen=True)
class Recommendation:
    item: CatalogueItem
    score: float
    reason: str
    via: CatalogueItem | None = None


def _preference(saved):
    weight = 0.55 if saved.state in TENTATIVE else 1.0
    if saved.favourite:
        weight += 2.0
    if saved.rating is not None:
        weight += (saved.rating - 3) * 0.15
    return weight


def _direct_edge(edge, seed):
    if edge.object_id == seed.pk:
        if edge.predicate == Predicate.ADAPTED_FROM:
            return edge.subject, f"Adaptation of {seed.title}"
        return edge.subject, f"Connected to {seed.title} by a verified relationship"
    if edge.predicate == Predicate.ADAPTED_FROM:
        return edge.object, f"Source work for {seed.title}"
    return (
        edge.object,
        f"Verified connection from {seed.title}: {edge.get_predicate_display()}",
    )


def _edges(start):
    return (
        supported_public_edges()
        .filter(Q(subject_id__in=start) | Q(object_id__in=start))
        .select_related("subject", "object")
        .order_by("id")[:EDGE_LIMIT]
    )


def _graph_candidates(seeds):
    first_hops = {}
    for edge in _edges(seeds):
        for seed_id in (edge.subject_id, edge.object_id):
            if seed_id not in seeds:
                continue
            seed = seeds[seed_id]
            item, reason = _direct_edge(edge, seed.item)
            score = 4 * _preference(seed)
            yield Recommendation(item, score, reason)
            if item.pk not in seeds and (
                item.pk not in first_hops or first_hops[item.pk][1] < score
            ):
                first_hops[item.pk] = (seed, score)

    for edge in _edges(first_hops):
        for node in (edge.subject, edge.object):
            if node.pk not in first_hops:
                continue
            seed, score = first_hops[node.pk]
            item = edge.object if edge.subject_id == node.pk else edge.subject
            yield Recommendation(
                item,
                score * 0.50,
                f"Connected to {seed.item.title} through {node.title}",
                node,
            )


def _content_candidates(seeds):
    terms = {}
    seed_tags = (
        ItemTag.objects.filter(item_id__in=seeds)
        .select_related("term")
        .order_by("id")[:TAG_LIMIT]
    )
    for tag in seed_tags:
        seed = seeds[tag.item_id]
        if tag.term_id not in terms or _preference(terms[tag.term_id]) < _preference(
            seed
        ):
            terms[tag.term_id] = seed
    candidates = (
        ItemTag.objects.filter(term_id__in=terms, item__in=public_items())
        .exclude(item_id__in=seeds)
        .select_related("item", "term")
        .order_by("id")[:TAG_LIMIT]
    )
    for tag in candidates:
        seed = terms[tag.term_id]
        yield Recommendation(
            tag.item,
            _preference(seed) * 1.5,
            f"Shares the catalogue subject {tag.term.label} with {seed.item.title}",
        )


def recommend(owner, *, kind=""):
    library = UserItem.objects.filter(owner=owner)
    seeds = {
        saved.item_id: saved
        for saved in library.filter(item__in=public_items())
        .select_related("item")
        .order_by("-favourite", "item__title_key", "pk")[:SEED_LIMIT]
    }
    if not seeds:
        return []
    candidates = defaultdict(list)
    for generator in (_graph_candidates(seeds), _content_candidates(seeds)):
        for candidate in generator:
            if not kind or candidate.item.kind == kind:
                candidates[candidate.item.pk].append(candidate)
    owned = set(
        library.filter(item_id__in=candidates).values_list("item_id", flat=True)
    )
    winners = [
        max(evidence, key=lambda candidate: candidate.score)
        for item_id, evidence in candidates.items()
        if item_id not in owned
    ]
    return sorted(
        winners, key=lambda value: (-value.score, value.item.title_key, value.item.pk)
    )[:RESULT_LIMIT]
