from django.db import models
from django.db.models import Q


class Visibility(models.TextChoices):
    PRIVATE = "private", "Private"
    FOLLOWERS = "followers", "Approved followers"
    PUBLIC = "public", "Public"


def viewer_owns(viewer, owner_id):
    return viewer.is_authenticated and viewer.pk == owner_id


def access_filter(viewer, *, owner_field, visibility_field="visibility"):
    public = Q(**{visibility_field: Visibility.PUBLIC})
    if not viewer.is_authenticated:
        return public
    # Follower-only access stays restricted until an approved relationship exists.
    return public | Q(**{owner_field: viewer.pk})
