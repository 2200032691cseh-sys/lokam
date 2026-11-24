from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import (
    require_http_methods,
    require_POST,
    require_safe,
)

from apps.core.policies import viewer_owns
from apps.libraries.services import PAGE_KINDS, page_items
from apps.media.views import image_response

from .forms import PageForm, ProfileForm
from .home import home_features, visible_avatar
from .models import PageKey
from .services import (
    create_profile,
    move_page,
    update_page,
    visible_pages,
    visible_profiles,
)


@never_cache
@require_safe
def website(request, username, page=PageKey.HOME):
    if page == PageKey.HOME and request.resolver_match.url_name == "page":
        raise Http404
    viewer = request.user
    preview = request.GET.get("preview") == "public" and (
        viewer.is_authenticated and viewer.username == username
    )
    if preview:
        viewer = AnonymousUser()
    profile = get_object_or_404(
        visible_profiles(viewer).select_related("avatar"), user__username=username
    )
    current = get_object_or_404(
        visible_pages(profile, viewer, include_disabled_for_owner=True), key=page
    )
    item_page = None
    if current.key in PAGE_KINDS:
        item_page = Paginator(page_items(profile, viewer, current), 24).get_page(
            request.GET.get("page")
        )
    return render(
        request,
        "profiles/site.html",
        {
            "profile": profile,
            "page": current,
            "pages": visible_pages(profile, viewer),
            "owner": viewer_owns(viewer, profile.user_id),
            "preview": preview,
            "item_page": item_page,
            **(home_features(profile, viewer) if current.key == PageKey.HOME else {}),
        },
    )


@never_cache
@require_safe
def avatar(request, username):
    profile = get_object_or_404(
        visible_profiles(request.user).select_related("avatar"), user__username=username
    )
    get_object_or_404(
        visible_pages(profile, request.user, include_disabled_for_owner=True),
        key=PageKey.HOME,
    )
    asset = visible_avatar(profile, request.user)
    if asset is None:
        raise Http404
    return image_response(asset, "small")


@never_cache
@login_required
@require_http_methods(["GET", "POST"])
def configure(request):
    profile = create_profile(request.user)
    form = ProfileForm(
        request.POST if request.method == "POST" else None, instance=profile
    )
    if form.is_valid():
        form.save()
        messages.success(request, "Profile settings saved.")
        return redirect("profiles:settings")
    return render(
        request,
        "profiles/settings.html",
        {
            "profile": profile,
            "form": form,
            "visibility_options": PageForm.base_fields["visibility"].choices,
        },
    )


@never_cache
@login_required
@require_POST
def configure_page(request, key):
    if key not in PageKey.values:
        raise Http404
    action = request.POST.get("action")
    if action in {"up", "down"}:
        move_page(request.user, key, -1 if action == "up" else 1)
    else:
        form = PageForm(request.POST)
        if not form.is_valid():
            messages.error(request, "Choose a valid page visibility.")
            return redirect("profiles:settings")
        update_page(request.user, key, **form.cleaned_data)
    messages.success(request, "Page settings saved.")
    return redirect("profiles:settings")
