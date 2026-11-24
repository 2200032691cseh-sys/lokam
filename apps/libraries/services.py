from dataclasses import asdict

from django.contrib.auth import get_user_model
from django.core import signing
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q

from apps.catalogue.models import CatalogueItem, ItemKind, normalize_name
from apps.core.policies import access_filter
from apps.integrations.adapters import Candidate
from apps.integrations.persistence import import_candidate
from apps.profiles.models import PageKey
from apps.profiles.services import visible_pages

from .models import UserItem

PAGE_KINDS = {
    PageKey.BOOKS: {ItemKind.BOOK, ItemKind.BOOK_EDITION},
    PageKey.MOVIES: {ItemKind.MOVIE},
    PageKey.TV: {ItemKind.SHOW, ItemKind.SEASON, ItemKind.EPISODE},
    PageKey.MUSIC: {
        ItemKind.MUSIC_ARTIST,
        ItemKind.MUSIC_ALBUM,
        ItemKind.MUSIC_RELEASE,
        ItemKind.MUSIC_RECORDING,
        ItemKind.MUSICAL_WORK,
    },
    PageKey.HISTORY: {ItemKind.HISTORY},
    PageKey.CULTURE: {ItemKind.CULTURE},
    PageKey.TRAVEL: {ItemKind.PLACE},
    PageKey.FOOD: {ItemKind.CUISINE, ItemKind.DISH},
    PageKey.LANGUAGES: {ItemKind.LANGUAGE},
    PageKey.MYTHOLOGY: {ItemKind.MYTHOLOGY},
    PageKey.PHILOSOPHY: {ItemKind.CONCEPT},
    PageKey.ACTIVITIES: {ItemKind.ACTIVITY},
    PageKey.LEARNING: {ItemKind.LEARNING},
}
EXTERNAL_KINDS = {ItemKind.BOOK, ItemKind.MOVIE, ItemKind.SHOW}
CANDIDATE_SALT = "lokam.catalogue-candidate"


def available_items(viewer):
    visible = Q(is_public=True, owner__isnull=True)
    if viewer.is_authenticated:
        visible |= Q(owner_id=viewer.pk)
    return CatalogueItem.objects.filter(visible)


def local_matches(viewer, query, kind):
    key = normalize_name(query)
    return (
        available_items(viewer)
        .filter(
            Q(title_key__contains=key) | Q(aliases__title_key__contains=key), kind=kind
        )
        .order_by("title_key", "pk")
        .distinct()[:24]
    )


def sign_candidate(owner, candidate):
    return signing.dumps(
        {"owner": owner.pk, "candidate": asdict(candidate)}, salt=CANDIDATE_SALT
    )


@transaction.atomic
def save_signed_candidate(owner, token):
    if len(token) > 5000:
        raise signing.BadSignature
    payload = signing.loads(token, salt=CANDIDATE_SALT, max_age=600)
    if payload.get("owner") != owner.pk:
        raise signing.BadSignature
    item = import_candidate(Candidate(**payload["candidate"]))
    if not item.is_public:
        raise ValidationError("This catalogue record is unavailable.")
    return save_item(owner, item)


def save_item(owner, item):
    if item.owner_id != owner.pk and (item.owner_id is not None or not item.is_public):
        raise ValidationError("This catalogue record is unavailable.")
    saved, _ = UserItem.objects.get_or_create(owner=owner, item=item)
    return saved


@transaction.atomic
def save_manual_item(owner, *, kind, title, year):
    # Lock the owner so two submissions of the same manual entry reuse one record.
    get_user_model().objects.select_for_update().get(pk=owner.pk)
    item = (
        CatalogueItem.objects.filter(
            owner=owner, kind=kind, title_key=normalize_name(title), year=year
        )
        .order_by("pk")
        .first()
    )
    if item is None:
        item = CatalogueItem.objects.create(
            owner=owner, kind=kind, title=title, year=year
        )
    return save_item(owner, item)


def page_items(profile, viewer, page):
    return (
        UserItem.objects.select_related("item")
        .filter(
            access_filter(viewer, owner_field="owner_id"),
            owner_id=profile.user_id,
            item__kind__in=PAGE_KINDS.get(page.key, ()),
            item__in=available_items(viewer),
            owner__profile__pages__in=visible_pages(
                profile, viewer, include_disabled_for_owner=True
            ).filter(pk=page.pk),
        )
        .order_by("item__title_key", "pk")
    )
