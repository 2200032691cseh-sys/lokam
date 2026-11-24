from django import forms

from apps.catalogue.models import ItemKind, normalize_name
from apps.core.policies import Visibility

from .models import STATE_OPTIONS, SaveState, UserItem


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
