"""Platform route declarations."""

from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("", include("apps.profiles.urls")),
    path("account/", include("apps.accounts.urls")),
    path(
        "", TemplateView.as_view(template_name="platform/landing.html"), name="landing"
    ),
]
