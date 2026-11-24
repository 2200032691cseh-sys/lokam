from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.db import models
from django.db.models.functions import Lower


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, username, password, **extra_fields):
        user = self.model(email=email, username=username, **extra_fields)
        user.clean()
        user.set_password(password)
        user.full_clean(validate_unique=False, validate_constraints=False)
        user.save(using=self._db)
        return user

    def create_user(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, username, password, **extra_fields)

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if not (extra_fields["is_staff"] and extra_fields["is_superuser"] and password):
            raise ValueError("A superuser requires staff access and a password.")
        return self._create_user(email, username, password, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email=email.strip().lower())

    async def aget_by_natural_key(self, email):
        return await self.aget(email=email.strip().lower())


class User(AbstractUser):
    username = models.CharField(
        max_length=32,
        unique=True,
        validators=[ASCIIUsernameValidator()],
        error_messages={"unique": "This username is unavailable."},
    )
    email = models.EmailField(unique=True)
    session_generation = models.PositiveIntegerField(default=0)
    email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(username=Lower("username")) & ~models.Q(username=""),
                name="accounts_username_nonempty_lower",
            ),
            models.CheckConstraint(
                condition=models.Q(email=Lower("email")) & ~models.Q(email=""),
                name="accounts_email_nonempty_lower",
            ),
        ]

    def clean(self):
        super().clean()
        self.username = (self.username or "").strip().lower()
        self.email = (self.email or "").strip().lower()
