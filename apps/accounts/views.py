from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods, require_POST

from apps.profiles.services import create_profile

from .forms import EmailForm, LoginForm, NewPasswordForm, SignUpForm
from .middleware import SESSION_GENERATION_KEY
from .models import User
from .services import (
    Purpose,
    allow_auth_attempt,
    consume_mail,
    issue_mail,
    resolve_mail,
)


def _form(request, form, title, submit, **context):
    return render(
        request,
        "accounts/form.html",
        {"form": form, "title": title, "submit": submit, **context},
    )


def _email_notice(request):
    return render(request, "accounts/email_notice.html")


def _invalid_link(request, retry):
    return render(request, "accounts/invalid_link.html", {"retry": retry}, status=400)


@never_cache
@require_http_methods(["GET", "POST"])
def signup(request):
    form = SignUpForm(request.POST if request.method == "POST" else None)
    if form.is_valid():
        email = form.cleaned_data["email"]
        if allow_auth_attempt(request, "signup", email, per_identity=3):
            try:
                with transaction.atomic():
                    user = User.objects.create_user(
                        email=email,
                        username=form.cleaned_data["username"],
                        password=form.cleaned_data["password"],
                    )
                    issue_mail(user, Purpose.VERIFY)
                    create_profile(user)
            except IntegrityError as error:
                diagnostic = getattr(error.__cause__, "diag", None)
                if getattr(diagnostic, "constraint_name", None) not in {
                    "accounts_user_email_key",
                    "accounts_user_username_key",
                }:
                    raise
        return _email_notice(request)
    return _form(request, form, "Create account", "Create account")


@never_cache
@require_http_methods(["GET", "POST"])
def signin(request):
    form = LoginForm(request.POST if request.method == "POST" else None)
    if form.is_valid():
        email = form.cleaned_data["email"]
        if allow_auth_attempt(request, "login", email):
            user = authenticate(
                request, username=email, password=form.cleaned_data["password"]
            )
            if user is not None:
                login(request, user)
                request.session[SESSION_GENERATION_KEY] = user.session_generation
                return redirect("landing")
        form.add_error(
            None, "We couldn't log you in. Check your credentials or try again later."
        )
    return _form(request, form, "Log in", "Log in", login_links=True)


@never_cache
@require_POST
def signout(request):
    logout(request)
    return redirect("landing")


@never_cache
@require_http_methods(["GET", "POST"])
def request_mail(request, purpose):
    form = EmailForm(request.POST if request.method == "POST" else None)
    if form.is_valid():
        email = form.cleaned_data["email"]
        if allow_auth_attempt(request, purpose, email, per_identity=3):
            user = User.objects.filter(
                email=email.lower(),
                is_active=True,
                email_verified=purpose == Purpose.RESET,
            ).first()
            if user is not None:
                issue_mail(user, purpose)
        return _email_notice(request)
    title = (
        "Recover your account"
        if purpose == Purpose.RESET
        else "Resend verification email"
    )
    return _form(request, form, title, "Send email")


@never_cache
@require_http_methods(["GET", "POST"])
def verify(request, reference, token):
    if request.method == "POST" and consume_mail(reference, token, Purpose.VERIFY):
        messages.success(request, "Your email is verified. You can log in.")
        return redirect("accounts:login")
    if resolve_mail(reference, token, Purpose.VERIFY) is None:
        return _invalid_link(request, "accounts:resend")
    return _form(request, forms.Form(), "Verify your email", "Verify email")


@never_cache
@require_http_methods(["GET", "POST"])
def reset(request, reference, token):
    match = resolve_mail(reference, token, Purpose.RESET)
    if match is None:
        return _invalid_link(request, "accounts:recover")
    _, user = match
    form = NewPasswordForm(
        request.POST if request.method == "POST" else None, user=user
    )
    if form.is_valid():
        if not consume_mail(
            reference, token, Purpose.RESET, password=form.cleaned_data["password"]
        ):
            return _invalid_link(request, "accounts:recover")
        logout(request)
        messages.success(request, "Your password was updated. You can log in.")
        return redirect("accounts:login")
    return _form(request, form, "Set a new password", "Save password")
