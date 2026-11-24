from django.urls import path

from . import views

app_name = "profiles"
urlpatterns = [
    path("settings/profile/", views.configure, name="settings"),
    path(
        "settings/profile/pages/<slug:key>/",
        views.configure_page,
        name="configure-page",
    ),
    path("u/<str:username>/", views.website, name="home"),
    path("u/<str:username>/<slug:page>/", views.website, name="page"),
]
