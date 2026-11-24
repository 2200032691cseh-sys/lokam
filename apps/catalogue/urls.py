from django.urls import path

from . import views

app_name = "catalogue"
urlpatterns = [
    path("", views.browse, name="browse"),
    path("credits/", views.credits, name="credits"),
    path("<uuid:public_id>/", views.detail, name="detail"),
]
