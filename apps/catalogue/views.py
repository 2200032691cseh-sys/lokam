from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_safe

from apps.media.models import CatalogueImage

from .identifiers import Namespace
from .models import BookEdition, ItemKind
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
    book_editions = (
        BookEdition.objects.filter(book__item=item, item__in=public_items())
        .select_related("item")
        .order_by("item__year", "item__title_key", "pk")[:24]
        if item.kind == ItemKind.BOOK
        else ()
    )
    edition = (
        BookEdition.objects.select_related("book__item").filter(item=item).first()
        if item.kind == ItemKind.BOOK_EDITION
        else None
    )
    isbns = (
        item.external_ids.filter(namespace=Namespace.ISBN).values_list(
            "value", flat=True
        )[:8]
        if edition
        else ()
    )
    return render(
        request,
        "catalogue/detail.html",
        {
            "item": item,
            "relations": public_relations(item),
            "catalogue_image": image,
            "book_editions": book_editions,
            "edition": edition,
            "isbns": isbns,
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
