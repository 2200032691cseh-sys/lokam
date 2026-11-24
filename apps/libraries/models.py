import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.catalogue.models import CatalogueItem, ItemKind
from apps.core.policies import Visibility


class SaveState(models.TextChoices):
    SAVED = "saved", "Saved"
    READ = "read", "Read"
    WANT_READ = "want-read", "Want to read"
    ASIDE = "set-aside", "Set aside"
    WATCHED = "watched", "Watched"
    WANT_WATCH = "want-watch", "Want to watch"
    VISITED = "visited", "Visited"
    WANT_VISIT = "want-visit", "Want to visit"
    KNOWN = "known", "Known"
    INTEREST = "interest", "Of interest"


STATE_OPTIONS = {
    ItemKind.BOOK: [SaveState.READ, SaveState.WANT_READ, SaveState.ASIDE],
    ItemKind.BOOK_EDITION: [SaveState.READ, SaveState.WANT_READ, SaveState.ASIDE],
    ItemKind.MOVIE: [SaveState.WATCHED, SaveState.WANT_WATCH],
    ItemKind.SHOW: [SaveState.WATCHED, SaveState.WANT_WATCH],
    ItemKind.PLACE: [SaveState.VISITED, SaveState.WANT_VISIT, SaveState.INTEREST],
    ItemKind.LANGUAGE: [SaveState.KNOWN, SaveState.INTEREST],
}


class UserItem(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_items"
    )
    item = models.ForeignKey(
        CatalogueItem, on_delete=models.CASCADE, related_name="saved_as"
    )
    state = models.CharField(
        max_length=12, choices=SaveState.choices, default=SaveState.SAVED
    )
    visibility = models.CharField(
        max_length=9, choices=Visibility.choices, default=Visibility.PRIVATE
    )
    favourite = models.BooleanField(default=False)
    feature_on_home = models.BooleanField(default=False)
    rating = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    note = models.TextField(blank=True, max_length=4000)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(feature_on_home=False) | models.Q(favourite=True),
                name="libraries_home_features_are_favourites",
            ),
            models.UniqueConstraint(
                fields=["owner", "item"], name="libraries_unique_saved_item"
            ),
            models.CheckConstraint(
                condition=models.Q(
                    state__in=SaveState.values, visibility__in=Visibility.values
                ),
                name="libraries_valid_relationship_settings",
            ),
            models.CheckConstraint(
                condition=models.Q(rating__isnull=True)
                | models.Q(rating__range=(1, 5)),
                name="libraries_valid_rating",
            ),
        ]


class BookAnnotation(models.Model):
    class Ownership(models.TextChoices):
        OWNED = "owned", "Owned"
        BORROWED = "borrowed", "Borrowed"
        PREVIOUSLY_OWNED = "previously-owned", "Previously owned"

    saved_item = models.OneToOneField(
        UserItem, on_delete=models.CASCADE, related_name="book_annotation"
    )
    ownership = models.CharField(max_length=16, choices=Ownership.choices, blank=True)
    personal_significance = models.TextField(max_length=2000, blank=True)
    favourite_passage = models.CharField(max_length=280, blank=True)
    passage_citation = models.CharField(max_length=240, blank=True)
    favourite_character = models.ForeignKey(
        CatalogueItem, on_delete=models.SET_NULL, null=True, blank=True
    )


class MovieAnnotation(models.Model):
    saved_item = models.OneToOneField(
        UserItem, on_delete=models.CASCADE, related_name="movie_annotation"
    )
    favourite_scene = models.TextField(max_length=1500, blank=True)
    favourite_performance = models.CharField(max_length=240, blank=True)
    favourite_dialogue = models.CharField(max_length=280, blank=True)


class TVAnnotation(models.Model):
    saved_item = models.OneToOneField(
        UserItem, on_delete=models.CASCADE, related_name="tv_annotation"
    )
    favourite_seasons = models.ManyToManyField("catalogue.TVSeason", blank=True)
    favourite_episodes = models.ManyToManyField("catalogue.TVEpisode", blank=True)
    favourite_characters = models.ManyToManyField(CatalogueItem, blank=True)
    favourite_relationships = models.TextField(max_length=1500, blank=True)


class MusicAnnotation(models.Model):
    saved_item = models.OneToOneField(
        UserItem, on_delete=models.CASCADE, related_name="music_annotation"
    )
    mood = models.CharField(max_length=120, blank=True)
    instruments = models.CharField(max_length=240, blank=True)
    languages = models.CharField(max_length=160, blank=True)
    musical_tradition = models.CharField(max_length=160, blank=True)
    personal_associations = models.TextField(max_length=1500, blank=True)
