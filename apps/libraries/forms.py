from django import forms

from apps.catalogue.models import (
    CatalogueItem,
    ItemKind,
    Predicate,
    TVEpisode,
    TVSeason,
    normalize_name,
)
from apps.catalogue.relationships import supported_public_edges
from apps.catalogue.services import public_items
from apps.core.policies import Visibility

from .models import (
    STATE_OPTIONS,
    BookAnnotation,
    MovieAnnotation,
    SaveState,
    TVAnnotation,
    UserItem,
)


class SearchForm(forms.Form):
    kind = forms.ChoiceField(choices=ItemKind.choices)
    query = forms.CharField(label="Title", max_length=120)

    def clean_query(self):
        query = self.cleaned_data["query"]
        normalize_name(query)
        return query


class ManualItemForm(forms.Form):
    kind = forms.ChoiceField(choices=ItemKind.choices)
    title = forms.CharField(max_length=240)
    year = forms.IntegerField(required=False, min_value=-9999, max_value=9999)

    def clean_title(self):
        title = self.cleaned_data["title"]
        normalize_name(title)
        return title


class ItemSettingsForm(forms.ModelForm):
    def clean(self):
        data = super().clean()
        if data.get("feature_on_home") and not data.get("favourite"):
            self.add_error(
                "feature_on_home", "Mark this item as a favourite to feature it."
            )
        return data

    class Meta:
        model = UserItem
        fields = [
            "state",
            "favourite",
            "feature_on_home",
            "rating",
            "note",
            "visibility",
        ]
        widgets = {"note": forms.Textarea(attrs={"rows": 4})}
        help_texts = {
            "note": "Only you can see this note.",
            "rating": "Optional, from 1 to 5.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        states = [
            SaveState.SAVED,
            *STATE_OPTIONS.get(self.instance.item.kind, [SaveState.INTEREST]),
        ]
        self.fields["state"].choices = [(state.value, state.label) for state in states]
        if self.instance.item.owner_id:
            self.fields["visibility"].choices = [
                (Visibility.PRIVATE, Visibility.PRIVATE.label)
            ]


class BookAnnotationForm(forms.ModelForm):
    class Meta:
        model = BookAnnotation
        fields = [
            "ownership",
            "personal_significance",
            "favourite_passage",
            "passage_citation",
            "favourite_character",
        ]
        widgets = {"personal_significance": forms.Textarea(attrs={"rows": 3})}
        help_texts = {
            "favourite_passage": "Keep quotations short. Your passage stays private."
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        item = self.instance.saved_item.item
        edition = getattr(item, "edition", None)
        work_id = edition.book.item_id if edition else item.pk
        ids = (
            supported_public_edges()
            .filter(subject_id=work_id, predicate=Predicate.FEATURES_CHARACTER)
            .values("object_id")
        )
        self.fields["favourite_character"].queryset = CatalogueItem.objects.filter(
            pk__in=ids
        ).order_by("title_key", "pk")


class MovieAnnotationForm(forms.ModelForm):
    class Meta:
        model = MovieAnnotation
        fields = ["favourite_scene", "favourite_performance", "favourite_dialogue"]
        widgets = {"favourite_scene": forms.Textarea(attrs={"rows": 3})}
        help_texts = {
            "favourite_dialogue": "Keep quotations short. Your dialogue stays private."
        }


class TVAnnotationForm(forms.ModelForm):
    class Meta:
        model = TVAnnotation
        fields = [
            "favourite_seasons",
            "favourite_episodes",
            "favourite_characters",
            "favourite_relationships",
        ]
        widgets = {"favourite_relationships": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        show_id = self.instance.saved_item.item_id
        eligible = public_items()
        seasons = TVSeason.objects.filter(
            show__item_id=show_id, item__in=eligible
        ).select_related("item")
        episodes = TVEpisode.objects.filter(
            season__in=seasons, item__in=eligible
        ).select_related("item")
        characters = eligible.filter(tvshowcharacter__show__item_id=show_id)
        self.fields["favourite_seasons"].queryset = seasons.order_by("number")
        self.fields["favourite_episodes"].queryset = episodes.order_by(
            "season__number", "number", "pk"
        )
        self.fields["favourite_characters"].queryset = characters.order_by(
            "title_key", "pk"
        )


class LibraryFilterForm(forms.Form):
    state = forms.ChoiceField(required=False, label="Status")
    query = forms.CharField(
        label="Title, author, genre, theme, character or series",
        required=False,
        max_length=120,
    )
    favourite = forms.BooleanField(label="Favourites only", required=False)

    def __init__(self, *args, kind, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["state"].choices = [
            ("", "All items"),
            *[(state.value, state.label) for state in STATE_OPTIONS[kind]],
        ]
        if kind in {ItemKind.MOVIE, ItemKind.SHOW}:
            self.fields[
                "query"
            ].label = "Title, cast, director, genre, language or country"

    def clean_query(self):
        query = self.cleaned_data["query"]
        return normalize_name(query) if query else ""
