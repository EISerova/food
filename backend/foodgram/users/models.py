from django.db import models
from django.contrib.auth.models import AbstractUser
from .validators import (RegexUsernameValidator, validate_username_not_me)

from foodgram.settings import CONFIRMATION_CODE_LENGTH

class User(AbstractUser):
    """Модель пользователей."""

    username = models.CharField(
        "Логин",
        max_length=150,
        unique=True,
        validators=[RegexUsernameValidator, validate_username_not_me],
    )
    first_name = models.CharField("Имя", max_length=150, blank=True)
    last_name = models.CharField("Фамилия", max_length=150, blank=True)
    email = models.EmailField("Почта", max_length=254, unique=True)
    confirmation_code = models.CharField(
        "Код подтверждения", max_length=CONFIRMATION_CODE_LENGTH, null=True
    )
