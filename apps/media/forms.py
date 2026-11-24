from django import forms


class ImageUploadForm(forms.Form):
    image = forms.FileField(
        widget=forms.ClearableFileInput(
            attrs={"accept": "image/jpeg,image/png,image/webp"}
        )
    )
    description = forms.CharField(
        max_length=512,
        help_text="Describe what the image shows.",
        widget=forms.TextInput(),
    )
