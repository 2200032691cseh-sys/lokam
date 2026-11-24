from django.urls import path

from . import views
from .models import AccountMail

app_name = "accounts"
urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("login/", views.signin, name="login"),
    path("logout/", views.signout, name="logout"),
    path(
        "verify/",
        views.request_mail,
        {"purpose": AccountMail.Purpose.VERIFY},
        name="resend",
    ),
    path("verify/<uuid:reference>/<str:token>/", views.verify, name="verify"),
    path(
        "recover/",
        views.request_mail,
        {"purpose": AccountMail.Purpose.RESET},
        name="recover",
    ),
    path("recover/<uuid:reference>/<str:token>/", views.reset, name="reset"),
]
