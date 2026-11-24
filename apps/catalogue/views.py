from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_safe

from .models import ItemKind
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
    return render(request, "catalogue/detail.html", {"item": item})
