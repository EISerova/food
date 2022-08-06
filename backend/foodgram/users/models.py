from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import RegexUsernameValidator, validate_username_not_me


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
    password = models.CharField("Пароль", max_length=150)
    is_subscribed = models.BooleanField('Подписка', default=False)
    create_at = models.DateTimeField("Дата регистрации", auto_now_add=True)

    def __str__(self):
        return self.username
