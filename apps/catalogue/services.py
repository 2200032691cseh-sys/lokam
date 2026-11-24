from django.db.models import Prefetch

from .models import CatalogueItem, ItemPersonRole, ItemTag


def public_items():
    return CatalogueItem.objects.filter(is_public=True, owner__isnull=True)


def public_details():
    credits = ItemPersonRole.objects.select_related("person__item").filter(
        person__item__in=public_items()
    )
    return public_items().prefetch_related(
        Prefetch("credits", queryset=credits, to_attr="public_credits"),
        Prefetch(
            "tags", queryset=ItemTag.objects.select_related("term").order_by("term")
        ),
        "aliases",
    )
