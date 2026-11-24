from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_safe

from apps.catalogue.models import ItemKind

from .services import recommend


@never_cache
@login_required
@require_safe
def discover(request):
    kind = request.GET.get("kind", "")
    if kind not in ItemKind.values:
        kind = ""
    return render(
        request,
        "discovery/discover.html",
        {
            "recommendations": recommend(request.user, kind=kind),
            "kind": kind,
            "kinds": ItemKind.choices,
        },
    )
