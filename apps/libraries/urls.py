from django.urls import path

from . import views

app_name = "libraries"
urlpatterns = [
    path("", views.index, name="index"),
    path("add/", views.add, name="add"),
    path("manual/", views.manual, name="manual"),
    path("add/external/", views.save_external, name="save-external"),
    path("add/<uuid:item_id>/", views.save_existing, name="save-existing"),
    path("<uuid:saved_id>/", views.edit, name="edit"),
    path("<uuid:saved_id>/remove/", views.remove, name="remove"),
]
