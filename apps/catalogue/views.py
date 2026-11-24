from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_safe

from apps.media.models import CatalogueImage

from .models import ItemKind
from .relationships import public_relations
from .services import public_details, public_items


@never_cache
@require_safe
def browse(request):
    items = public_items().order_by("title_key", "pk")
    kind = request.GET.get("kind", "")
    if kind in ItemKind.values:
        items = items.filter(kind=kind)
    page = Paginator(items, 24).get_page(request.GET.get("page"))
    return render(
        request,
        "catalogue/list.html",
        {"page_obj": page, "kind": kind, "kind_choices": ItemKind.choices},
    )


@never_cache
@require_safe
def detail(request, public_id):
    item = get_object_or_404(public_details(), public_id=public_id)
    image = (
        CatalogueImage.objects.select_related("source")
        .filter(
            source__item=item,
            source__show_credit=True,
            can_display=True,
        )
        .order_by("pk")
        .first()
    )
    return render(
        request,
        "catalogue/detail.html",
        {
            "item": item,
            "relations": public_relations(item),
            "catalogue_image": image,
        },
    )


@never_cache
@require_safe
def credits(request):
    records = (
        CatalogueImage.objects.select_related("source", "source__item")
        .filter(
            can_display=True, source__show_credit=True, source__item__in=public_items()
        )
        .order_by("source__item__title_key", "pk")
    )
    page_obj = Paginator(records, 24).get_page(request.GET.get("page"))
    return render(request, "catalogue/credits.html", {"page_obj": page_obj})
