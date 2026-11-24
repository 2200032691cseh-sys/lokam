import unicodedata
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .identifiers import Namespace, normalize_identifier


def normalize_name(value):
    normalized = unicodedata.normalize("NFKC", value).casefold()
    key = " ".join(normalized.split())
    if not key or len(key) > 480:
        raise ValidationError("Enter a name with a searchable length.")
    return key


class ItemKind(models.TextChoices):
    BOOK = "book", "Book"
    BOOK_EDITION = "book-edition", "Book edition"
    MOVIE = "movie", "Movie"
    SHOW = "tv-show", "TV show"
    SEASON = "tv-season", "TV season"
    EPISODE = "tv-episode", "TV episode"
    PERSON = "person", "Person"
    MUSIC_ARTIST = "music-artist", "Music artist"
    MUSIC_ALBUM = "music-album", "Music album"
    MUSIC_RELEASE = "music-release", "Music release"
    MUSIC_RECORDING = "music-recording", "Music recording"
    MUSICAL_WORK = "musical-work", "Musical work"
    HISTORY = "history", "Historical subject"
    CULTURE = "culture", "Culture or heritage"
    PLACE = "place", "Place"
    CUISINE = "cuisine", "Cuisine"
    DISH = "dish", "Dish"
    LANGUAGE = "language", "Language"
    MYTHOLOGY = "mythology", "Mythology or folklore"
    CONCEPT = "concept", "Concept"
    ACTIVITY = "activity", "Activity or experience"
    LEARNING = "learning", "Learning resource"
    CHARACTER = "character", "Character"
    SERIES = "series", "Series or franchise"


class CatalogueItem(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    kind = models.CharField(max_length=24, choices=ItemKind.choices)
    subtype = models.SlugField(max_length=48, blank=True)
    title = models.CharField(max_length=240)
    title_key = models.CharField(max_length=480, editable=False)
    description = models.TextField(max_length=4000, blank=True)
    language = models.CharField(max_length=24, blank=True)
    year = models.SmallIntegerField(null=True, blank=True)
    is_public = models.BooleanField(default=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )

    class Meta:
        indexes = [
            models.Index(
                fields=["title_key", "id"],
                name="catalogue_public_title_idx",
                condition=models.Q(is_public=True, owner__isnull=True),
            )
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(kind__in=ItemKind.values),
                name="catalogue_valid_kind",
            ),
            models.CheckConstraint(
                condition=models.Q(owner__isnull=True) | models.Q(is_public=False),
                name="catalogue_custom_never_public",
            ),
        ]

    def save(self, *args, **kwargs):
        self.title_key = normalize_name(self.title)
        if (
            kwargs.get("update_fields") is not None
            and "title" in kwargs["update_fields"]
        ):
            kwargs["update_fields"] = {*kwargs["update_fields"], "title_key"}
        super().save(*args, **kwargs)


class CatalogueAlias(models.Model):
    item = models.ForeignKey(
        CatalogueItem, on_delete=models.CASCADE, related_name="aliases"
    )
    title = models.CharField(max_length=240)
    title_key = models.CharField(max_length=480, editable=False)
    language = models.CharField(max_length=24, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["item", "language", "title_key"], name="catalogue_unique_alias"
            )
        ]

    def save(self, *args, **kwargs):
        self.title_key = normalize_name(self.title)
        if (
            kwargs.get("update_fields") is not None
            and "title" in kwargs["update_fields"]
        ):
            kwargs["update_fields"] = {*kwargs["update_fields"], "title_key"}
        super().save(*args, **kwargs)


class Person(models.Model):
    item = models.OneToOneField(
        CatalogueItem, on_delete=models.CASCADE, related_name="person"
    )

    def clean(self):
        if self.item_id and self.item.kind not in {
            ItemKind.PERSON,
            ItemKind.MUSIC_ARTIST,
        }:
            raise ValidationError(
                {"item": "A person requires a person or artist catalogue item."}
            )


class ItemPersonRole(models.Model):
    class Role(models.TextChoices):
        AUTHOR = "author", "Author"
        EDITOR = "editor", "Editor"
        DIRECTOR = "director", "Director"
        WRITER = "writer", "Writer"
        CREATOR = "creator", "Creator"
        ACTOR = "actor", "Cast"
        COMPOSER = "composer", "Composer"
        PERFORMER = "performer", "Performer"
        TRANSLATOR = "translator", "Translator"

    item = models.ForeignKey(
        CatalogueItem, on_delete=models.CASCADE, related_name="credits"
    )
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="credits")
    role = models.CharField(max_length=12, choices=Role.choices)
    detail = models.CharField(max_length=160, blank=True)
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["position", "pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["item", "person", "role", "detail"],
                name="catalogue_unique_credit",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    role__in=[
                        "author",
                        "editor",
                        "director",
                        "writer",
                        "creator",
                        "actor",
                        "composer",
                        "performer",
                        "translator",
                    ]
                ),
                name="catalogue_valid_role",
            ),
        ]


class VocabularyTerm(models.Model):
    class Kind(models.TextChoices):
        GENRE = "genre", "Genre"
        THEME = "theme", "Theme"
        TAG = "tag", "Tag"

    kind = models.CharField(max_length=5, choices=Kind.choices)
    label = models.CharField(max_length=160)
    key = models.CharField(max_length=480, editable=False)

    class Meta:
        ordering = ["kind", "label", "pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["kind", "key"], name="catalogue_unique_term"
            ),
            models.CheckConstraint(
                condition=models.Q(kind__in=["genre", "theme", "tag"]),
                name="catalogue_valid_term_kind",
            ),
        ]

    def save(self, *args, **kwargs):
        self.key = normalize_name(self.label)
        if (
            kwargs.get("update_fields") is not None
            and "label" in kwargs["update_fields"]
        ):
            kwargs["update_fields"] = {*kwargs["update_fields"], "key"}
        super().save(*args, **kwargs)


class ItemTag(models.Model):
    item = models.ForeignKey(
        CatalogueItem, on_delete=models.CASCADE, related_name="tags"
    )
    term = models.ForeignKey(VocabularyTerm, on_delete=models.PROTECT)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["item", "term"], name="catalogue_unique_item_term"
            )
        ]


class ExternalIdentifier(models.Model):
    item = models.ForeignKey(
        CatalogueItem, on_delete=models.CASCADE, related_name="external_ids"
    )
    namespace = models.CharField(
        max_length=16, choices=[(value.value, value.name) for value in Namespace]
    )
    value = models.CharField(max_length=40)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["namespace", "value"], name="catalogue_unique_external_id"
            ),
            models.CheckConstraint(
                condition=models.Q(namespace__in=[value.value for value in Namespace]),
                name="catalogue_valid_external_namespace",
            ),
        ]

    def save(self, *args, **kwargs):
        self.value = normalize_identifier(self.namespace, self.value)
        super().save(*args, **kwargs)


class SourceProvider(models.TextChoices):
    OPEN_LIBRARY = "open-library", "Open Library"
    TMDB = "tmdb", "TMDB"
    WIKIDATA = "wikidata", "Wikidata"
    MUSICBRAINZ = "musicbrainz", "MusicBrainz"
    WIKIMEDIA = "wikimedia", "Wikimedia"
    MANUAL = "manual", "Manual source"


class CatalogueSource(models.Model):
    item = models.ForeignKey(
        CatalogueItem, on_delete=models.CASCADE, related_name="sources"
    )
    provider = models.CharField(max_length=16, choices=SourceProvider.choices)
    reference = models.CharField(max_length=140)
    revision = models.CharField(max_length=80)
    source_url = models.URLField(max_length=500)
    licence = models.CharField(max_length=120, blank=True)
    fields = models.JSONField(default=list)
    retrieved_at = models.DateTimeField(auto_now_add=True)
    show_credit = models.BooleanField(default=False)
    export_allowed = models.BooleanField(default=False)

    class Meta:
        ordering = ["provider", "-retrieved_at", "pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["item", "provider", "reference", "revision"],
                name="catalogue_unique_source_revision",
            ),
            models.CheckConstraint(
                condition=models.Q(provider__in=SourceProvider.values),
                name="catalogue_valid_source",
            ),
        ]
