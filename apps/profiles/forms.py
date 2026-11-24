from django import forms

from apps.core.policies import Visibility

from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["introduction", "visibility"]
        widgets = {"introduction": forms.Textarea(attrs={"rows": 5})}


class PageForm(forms.Form):
    enabled = forms.BooleanField(required=False)
    visibility = forms.ChoiceField(choices=Visibility.choices)
