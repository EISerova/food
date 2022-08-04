from django.db import models

from django.core.validators import RegexValidator

class Ingridient(models.Model):
    """Ингредиенты."""

    name = models.TextField("Название", max_length=256)
    measurement_unit = models.TextField("Мера измерения", max_length=256)

    def __str__(self):
        return f"Ингредиент - {self.name}"


class Tag(models.Model):
    """Тэги."""

    name = models.TextField("Название", max_length=200)
    color = models.TextField("Цвет в HEX", max_length=7, null=True)
    slug = models.TextField(
        "Уникальный слаг",
        max_length=200,
        validators=[
            RegexValidator(
            regex = r"^[-a-zA-Z0-9_]+$",
            message = 'Разрешены латинские буквы и цифры. Не более 200 символов.'
            ),
        ],
        null=True)

    def __str__(self):
        return f"Тэг - {self.name}"

