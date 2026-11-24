from django import forms
from django.contrib.auth.password_validation import validate_password

from .models import User


class EmailForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"autocomplete": "email"}))


class LoginForm(EmailForm):
    password = forms.CharField(
        max_length=256,
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )


class NewPasswordForm(forms.Form):
    password = forms.CharField(
        max_length=256,
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    password_confirmation = forms.CharField(
        label="Confirm password",
        max_length=256,
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get("password")
        if password and password != cleaned.get("password_confirmation"):
            self.add_error("password_confirmation", "Passwords must match.")
        if password:
            try:
                validate_password(password, self.user)
            except forms.ValidationError as error:
                self.add_error("password", error)
        return cleaned


class SignUpForm(EmailForm, NewPasswordForm):
    username = forms.CharField(
        max_length=32,
        validators=User._meta.get_field("username").validators,
        widget=forms.TextInput(
            attrs={"autocomplete": "username", "autocapitalize": "none"}
        ),
    )
    field_order = ["email", "username", "password", "password_confirmation"]

    def clean(self):
        self.user = User(
            email=self.cleaned_data.get("email", ""),
            username=self.cleaned_data.get("username", ""),
        )
        return super().clean()
