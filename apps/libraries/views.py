from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.core.signing import BadSignature
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import (
    require_http_methods,
    require_POST,
    require_safe,
)

from apps.catalogue.models import ItemKind
from apps.integrations.adapters import search_external
from apps.integrations.http import ProviderUnavailable

from .forms import BookAnnotationForm, ItemSettingsForm, ManualItemForm, SearchForm
from .models import BookAnnotation, UserItem
from .services import (
    EXTERNAL_KINDS,
    available_items,
    local_matches,
    save_item,
    save_manual_item,
    save_signed_candidate,
    sign_candidate,
)


@never_cache
@login_required
@require_safe
def index(request):
    items = (
        UserItem.objects.filter(owner=request.user)
        .select_related("item")
        .order_by("item__title_key", "pk")
    )
    return render(
        request,
        "libraries/index.html",
        {
            "page_obj": Paginator(items, 24).get_page(request.GET.get("page")),
        },
    )


@never_cache
@login_required
@require_safe
def add(request):
    form = SearchForm(request.GET or None)
    context = {"form": form}
    if form.is_valid():
        kind = form.cleaned_data["kind"]
        query = form.cleaned_data["query"]
        context["matches"] = local_matches(request.user, query, kind)
        context["has_provider"] = kind in EXTERNAL_KINDS
        if request.GET.get("external") == "yes" and kind in EXTERNAL_KINDS:
            try:
                context["external_matches"] = [
                    (candidate, sign_candidate(request.user, candidate))
                    for candidate in search_external(kind, query)
                ]
            except ProviderUnavailable:
                context["provider_unavailable"] = True
    return render(request, "libraries/add.html", context)


@never_cache
@login_required
@require_POST
def save_existing(request, item_id):
    item = get_object_or_404(available_items(request.user), public_id=item_id)
    saved = save_item(request.user, item)
    messages.success(request, "Saved to your library.")
    return redirect("libraries:edit", saved.public_id)


@never_cache
@login_required
@require_POST
def save_external(request):
    try:
        saved = save_signed_candidate(request.user, request.POST.get("candidate", ""))
    except (BadSignature, ValidationError):
        messages.error(
            request, "This result is unavailable. Search again or add it manually."
        )
        return redirect("libraries:add")
    messages.success(request, "Saved to your library.")
    return redirect("libraries:edit", saved.public_id)


@never_cache
@login_required
@require_http_methods(["GET", "POST"])
def manual(request):
    form = ManualItemForm(request.POST if request.method == "POST" else None)
    if form.is_valid():
        saved = save_manual_item(request.user, **form.cleaned_data)
        messages.success(request, "Saved to your library.")
        return redirect("libraries:edit", saved.public_id)
    return render(request, "libraries/manual.html", {"form": form})


@never_cache
@login_required
@require_http_methods(["GET", "POST"])
@transaction.atomic
def edit(request, saved_id):
    rows = UserItem.objects.select_related("item")
    if request.method == "POST":
        rows = rows.select_for_update(of=("self",))
    saved = get_object_or_404(rows, owner=request.user, public_id=saved_id)
    data = request.POST if request.method == "POST" else None
    form = ItemSettingsForm(data, instance=saved)
    book_form = None
    if saved.item.kind in {ItemKind.BOOK, ItemKind.BOOK_EDITION}:
        annotation = BookAnnotation.objects.filter(
            saved_item=saved
        ).first() or BookAnnotation(saved_item=saved)
        book_form = BookAnnotationForm(data, prefix="book", instance=annotation)
    if form.is_valid() and (book_form is None or book_form.is_valid()):
        form.save()
        if book_form is not None and book_form.has_changed():
            book_form.save()
        messages.success(request, "Saved item updated.")
        return redirect("libraries:edit", saved.public_id)
    return render(
        request,
        "libraries/edit.html",
        {"saved": saved, "form": form, "book_form": book_form},
    )


@never_cache
@login_required
@require_POST
def remove(request, saved_id):
    saved = get_object_or_404(UserItem, owner=request.user, public_id=saved_id)
    saved.delete()
    messages.success(request, "Removed from your library.")
    return redirect("libraries:index")
