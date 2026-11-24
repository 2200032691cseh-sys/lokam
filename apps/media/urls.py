from django.urls import path

from . import views

app_name = "media"
urlpatterns = [
    path("", views.images, name="index"),
    path("<uuid:public_id>/delete/", views.delete, name="delete"),
    path("<uuid:public_id>/<slug:variant>/", views.image, name="image"),
]
