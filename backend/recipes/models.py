from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from users.models import User

from foodgram.settings import MIN_COOKING_TIME, TAG_SLUG_LENGTH_ERROR


class Ingredient(models.Model):
    """Ингредиенты."""

    name = models.TextField("Название", max_length=256)
    measurement_unit = models.TextField("Мера измерения", max_length=256)

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return f"Ингредиент - {self.name}"


class Tag(models.Model):
    """Тэги."""

    name = models.TextField("Название", max_length=200, blank=True, null=True)
    color = models.TextField(
        "Цвет в HEX", max_length=7, blank=True, null=True, default="#ffffff"
    )
    slug = models.TextField(
        "Уникальный слаг",
        max_length=200,
        validators=[
            RegexValidator(
                regex=r"^[-a-zA-Z0-9_]+$",
                message=TAG_SLUG_LENGTH_ERROR,
            ),
        ],
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def __str__(self):
        return f"Тэг - {self.name}"


class Recipe(models.Model):
    """Рецепт."""

    name = models.TextField("Название", max_length=200)
    text = models.TextField("Описание")
    image = models.ImageField(
        verbose_name="Изображение", upload_to="recipes/", editable=True
    )
    cooking_time = models.PositiveSmallIntegerField(
        "Время приготовления (в минутах)",
        validators=[MinValueValidator(MIN_COOKING_TIME)],
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientRecipe",
        verbose_name="Ингредиенты",
    )
    tags = models.ManyToManyField(Tag, verbose_name="Тэги")

    class Meta:
        ordering = ("author",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return f"Рецепт - {self.name}"


class IngredientRecipe(models.Model):
    """Рецепт."""

    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name="ingredient_recipe"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="ingredient_recipe"
    )
    amount = models.PositiveSmallIntegerField()


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


class ShoppingCart(models.Model):
    """Список покупок"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="cart")
