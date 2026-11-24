from django import forms

from apps.core.policies import Visibility
from apps.media.models import AssetState, MediaAsset

from .models import Profile


class ProfileForm(forms.ModelForm):
    avatar = forms.ModelChoiceField(
        queryset=MediaAsset.objects.none(), required=False, label="Profile photograph"
    )

    class Meta:
        model = Profile
        fields = ["introduction", "visibility", "avatar", "share_avatar"]
        widgets = {"introduction": forms.Textarea(attrs={"rows": 5})}
        labels = {"share_avatar": "Show the photograph to visitors who can see Home"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["avatar"].queryset = MediaAsset.objects.filter(
            owner_id=self.instance.user_id, state=AssetState.READY
        ).order_by("description", "pk")


class PageForm(forms.Form):
    enabled = forms.BooleanField(required=False)
    visibility = forms.ChoiceField(choices=Visibility.choices)
