from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from users.models import User


class Recipe(models.Model):
    """Рецепт."""

    name = models.TextField("Название", max_length=200)
    text = models.TextField("Описание")
    image = models.BinaryField(verbose_name="Изображение", editable=True)
    cooking_time = models.PositiveSmallIntegerField(
        "время приготовления", validators=[MinValueValidator(1)]
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="автор")

    class Meta:
        ordering = ("author",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return f"Рецепт - {self.name}"


class Ingredient(models.Model):
    """Ингредиенты."""

    name = models.TextField("Название", max_length=256)
    measurement_unit = models.TextField("Мера измерения", max_length=256)
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ingredients",
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

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
                regex=r"^[-a-zA-Z0-9_]+$",
                message="Разрешены латинские буквы и цифры. Не более 200 символов.",
            ),
        ],
        null=True,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="tags",
    )

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def __str__(self):
        return f"Тэг - {self.name}"


class Follow(models.Model):
    """Подписка на авторов"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="follower_author_connection"
            )
        ]


class Favorite(models.Model):
    """Избранные рецепты"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorite_recipes",
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="favorites"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="user_recipe_connection"
            )
        ]


class Shopping_cart(models.Model):
    """Список покупок"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="cart")
