from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import (
    require_http_methods,
    require_POST,
    require_safe,
)

from .forms import ImageUploadForm
from .models import AssetState, MediaAsset
from .services import private_storage, request_deletion, stage_upload


@never_cache
@login_required
@require_http_methods(["GET", "POST"])
def images(request):
    form = (
        ImageUploadForm(request.POST, request.FILES)
        if request.method == "POST"
        else ImageUploadForm()
    )
    if form.is_valid():
        try:
            stage_upload(
                request.user,
                form.cleaned_data["image"],
                form.cleaned_data["description"],
            )
        except ValidationError as error:
            form.add_error("image", error)
        else:
            messages.success(request, "Image queued for processing.")
            return redirect("media:index")
    rows = MediaAsset.objects.filter(owner=request.user).order_by("-pk")
    page = Paginator(rows, 20).get_page(request.GET.get("page"))
    return render(request, "media/images.html", {"form": form, "page_obj": page})


def image_response(asset, variant, *, download=False):
    rendition = asset.variants.get(variant)
    if rendition is None:
        raise Http404
    try:
        body = private_storage().open(rendition["key"], "rb")
    except FileNotFoundError as error:
        raise Http404 from error
    return FileResponse(
        body,
        content_type="image/webp",
        as_attachment=download,
        filename=f"lokam-{asset.public_id}.webp",
    )


@never_cache
@login_required
@require_safe
def image(request, public_id, variant):
    asset = get_object_or_404(
        MediaAsset, owner=request.user, public_id=public_id, state=AssetState.READY
    )
    return image_response(asset, variant, download=request.GET.get("download") == "1")


@never_cache
@login_required
@require_POST
def delete(request, public_id):
    asset = get_object_or_404(MediaAsset, owner=request.user, public_id=public_id)
    request_deletion(asset.pk, request.user)
    messages.success(request, "Image deletion queued.")
    return redirect("media:index")
