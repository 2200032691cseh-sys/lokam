from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from .models import CatalogueRelationship, ItemKind, Predicate, RelationshipEvidence

PERSON_KINDS = {ItemKind.PERSON, ItemKind.MUSIC_ARTIST, ItemKind.HISTORY}
WORK_KINDS = {
    ItemKind.BOOK,
    ItemKind.BOOK_EDITION,
    ItemKind.MOVIE,
    ItemKind.SHOW,
    ItemKind.EPISODE,
    ItemKind.MUSICAL_WORK,
    ItemKind.MUSIC_RECORDING,
    ItemKind.LEARNING,
}
TARGET_KINDS = {
    Predicate.ADAPTED_FROM: WORK_KINDS,
    Predicate.WRITTEN_BY: PERSON_KINDS,
    Predicate.DIRECTED_BY: PERSON_KINDS,
    Predicate.CREATED_BY: PERSON_KINDS,
    Predicate.COMPOSED_BY: PERSON_KINDS,
    Predicate.PERFORMED_BY: PERSON_KINDS,
    Predicate.FEATURES_CHARACTER: {ItemKind.CHARACTER},
    Predicate.DEPICTS_FIGURE: {ItemKind.HISTORY, ItemKind.PERSON},
    Predicate.DEPICTS_EVENT: {ItemKind.HISTORY},
    Predicate.SET_IN: {ItemKind.PLACE},
    Predicate.SET_DURING: {ItemKind.HISTORY},
    Predicate.CULTURE: {ItemKind.CULTURE},
    Predicate.LANGUAGE: {ItemKind.LANGUAGE},
    Predicate.SOUNDTRACK: {ItemKind.MOVIE, ItemKind.SHOW, ItemKind.EPISODE},
    Predicate.SERIES: {ItemKind.SERIES, ItemKind.SHOW},
    Predicate.FRANCHISE: {ItemKind.SERIES},
    Predicate.MYTHOLOGY: {ItemKind.MYTHOLOGY},
    Predicate.LOCATED_IN: {ItemKind.PLACE},
    Predicate.CUISINE: {ItemKind.CUISINE},
}


@transaction.atomic
def record_edge(
    subject,
    predicate,
    target,
    *,
    source,
    statement_id,
    reference_url="",
    qualifiers=None,
):
    if (
        subject.owner_id
        or target.owner_id
        or subject.pk == target.pk
        or predicate not in Predicate.values
        or (predicate in TARGET_KINDS and target.kind not in TARGET_KINDS[predicate])
        or (predicate == Predicate.ADAPTED_FROM and subject.kind not in WORK_KINDS)
        or "relationship" not in source.fields
        or source.item_id not in {subject.pk, target.pk}
        or not statement_id
    ):
        raise ValidationError(
            "The relationship requires supported endpoints and source evidence."
        )
    edge, _ = CatalogueRelationship.objects.get_or_create(
        subject=subject, predicate=predicate, object=target
    )
    RelationshipEvidence.objects.get_or_create(
        edge=edge,
        source=source,
        statement_id=statement_id,
        defaults={"reference_url": reference_url, "qualifiers": qualifiers or {}},
    )
    return edge


@transaction.atomic
def verify_edge(edge_id):
    edge = CatalogueRelationship.objects.select_for_update().get(pk=edge_id)
    if not edge.evidence.filter(source__show_credit=True).exists():
        raise ValidationError(
            "Visible source evidence is required to verify a relationship."
        )
    edge.verified_at = timezone.now()
    edge.save(update_fields=["verified_at"])
    return edge


def supported_public_edges():
    return CatalogueRelationship.objects.filter(
        verified_at__isnull=False,
        subject__owner__isnull=True,
        object__owner__isnull=True,
        subject__is_public=True,
        object__is_public=True,
        evidence__source__show_credit=True,
    ).distinct()


def public_relations(item):
    edges = supported_public_edges().filter(Q(subject=item) | Q(object=item))
    return [
        (
            edge.object if edge.subject_id == item.pk else edge.subject,
            "Adaptation"
            if edge.object_id == item.pk and edge.predicate == Predicate.ADAPTED_FROM
            else edge.get_predicate_display()
            if edge.subject_id == item.pk
            else "Related work or subject",
        )
        for edge in edges.select_related("subject", "object").order_by("id")[:12]
    ]
