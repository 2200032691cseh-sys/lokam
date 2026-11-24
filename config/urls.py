"""Platform route declarations."""

from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("", include("apps.profiles.urls")),
    path("account/", include("apps.accounts.urls")),
    path("catalogue/", include("apps.catalogue.urls")),
    path("saved/", include("apps.libraries.urls")),
    path("discover/", include("apps.discovery.urls")),
    path("images/", include("apps.media.urls")),
    path(
        "", TemplateView.as_view(template_name="platform/landing.html"), name="landing"
    ),
]
