from django.conf import settings
from django.db import models

from apps.core.policies import Visibility


class PageKey(models.TextChoices):
    HOME = "home", "Home"
    BOOKS = "books", "Books"
    MOVIES = "movies", "Movies"
    TV = "tv-shows", "TV Shows"
    MUSIC = "music", "Music"
    HISTORY = "history", "History"
    CULTURE = "culture-heritage", "Culture & Heritage"
    TRAVEL = "travel", "Travel"
    FOOD = "food-cuisine", "Food & Cuisine"
    LANGUAGES = "languages", "Languages"
    MYTHOLOGY = "mythology-folklore", "Mythology & Folklore"
    PHILOSOPHY = "philosophy-psychology", "Philosophy & Psychology"
    ACTIVITIES = "activities-experiences", "Activities & Experiences"
    LEARNING = "learning-exploration", "Learning & Exploration"
    MEMORIES = "photography-memories", "Photography & Memories"
    COLLECTIONS = "collections", "Collections"
    FAVOURITES = "favourites", "Favourites"
    BUCKET_LIST = "bucket-list", "Lifetime Bucket List"
    STATISTICS = "statistics", "Statistics"
    TIMELINE = "timeline", "Personal Timeline"


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    introduction = models.TextField(max_length=2000, blank=True)
    avatar = models.ForeignKey(
        "media.MediaAsset", on_delete=models.SET_NULL, null=True, blank=True
    )
    share_avatar = models.BooleanField(default=False)
    visibility = models.CharField(
        max_length=9, choices=Visibility.choices, default=Visibility.PRIVATE
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(visibility__in=Visibility.values),
                name="profiles_valid_visibility",
            )
        ]


class ProfilePage(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="pages")
    key = models.CharField(max_length=24, choices=PageKey.choices)
    position = models.PositiveSmallIntegerField()
    enabled = models.BooleanField(default=True)
    visibility = models.CharField(
        max_length=9, choices=Visibility.choices, default=Visibility.PRIVATE
    )

    class Meta:
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "key"], name="profiles_unique_page_key"
            ),
            models.UniqueConstraint(
                fields=["profile", "position"],
                name="profiles_unique_page_position",
                deferrable=models.Deferrable.DEFERRED,
            ),
            models.CheckConstraint(
                condition=models.Q(position__range=(0, 19), key__in=PageKey.values)
                & models.Q(visibility__in=Visibility.values),
                name="profiles_valid_page_settings",
            ),
        ]
