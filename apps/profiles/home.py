from django.db.models import Q

from apps.catalogue.relationships import supported_public_edges
from apps.core.policies import access_filter, viewer_owns
from apps.libraries.models import UserItem
from apps.libraries.services import PAGE_KINDS, available_items
from apps.media.models import AssetState

from .services import visible_pages


def visible_avatar(profile, viewer):
    avatar = profile.avatar
    if (
        avatar is not None
        and avatar.owner_id == profile.user_id
        and avatar.state == AssetState.READY
        and (profile.share_avatar or viewer_owns(viewer, profile.user_id))
    ):
        return avatar
    return None


def home_features(profile, viewer):
    page_keys = visible_pages(profile, viewer).values_list("key", flat=True)
    kinds = {kind for page in page_keys for kind in PAGE_KINDS.get(page, ())}
    favourites = list(
        UserItem.objects.select_related("item")
        .filter(
            access_filter(viewer, owner_field="owner_id"),
            owner_id=profile.user_id,
            favourite=True,
            feature_on_home=True,
            item__kind__in=kinds,
            item__in=available_items(viewer),
        )
        .order_by("item__title_key", "pk")[:8]
    )
    featured_ids = {saved.item_id for saved in favourites}
    edges = (
        supported_public_edges()
        .filter(Q(subject_id__in=featured_ids) | Q(object_id__in=featured_ids))
        .select_related("subject", "object")
        .order_by("id")[:16]
    )
    connections = [edge for edge in edges if edge.subject.kind != edge.object.kind][:6]
    return {
        "avatar": visible_avatar(profile, viewer),
        "featured_favourites": favourites,
        "connections": connections,
    }
