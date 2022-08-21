from django.contrib import admin

from .models import (
    Favorite,
    Follow,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)
from users.models import User

EMPTY_VALUE_DISPLAY = "-пусто-"


@admin.register(User)
class UserClass(admin.ModelAdmin):
    """Админка юзеров."""

    list_display = (
        "id",
        "password",
        "last_login",
        "is_superuser",
        "username",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "email",
        "create_at",
    )
    list_filter = (
        "is_active",
        "last_login",
        "create_at",
    )
    list_editable = (
        "password",
        "username",
        "first_name",
        "last_name",
        "is_staff",
        "email",
    )
    search_fields = (
        "id",
        "username",
        "email",
    )
    ordering = ("-create_at",)
    empty_value_display = EMPTY_VALUE_DISPLAY


@admin.register(Ingredient)
class IngredientClass(admin.ModelAdmin):
    """Админка ингредиентов."""

    list_display = (
        "id",
        "name",
        "measurement_unit",
    )
    list_filter = (
        "name",
        "measurement_unit",
    )
    list_editable = (
        "name",
        "measurement_unit",
    )
    search_fields = ("name",)
    ordering = ("id",)
    empty_value_display = EMPTY_VALUE_DISPLAY


@admin.register(Tag)
class TagClass(admin.ModelAdmin):
    """Админка тэгов."""

    list_display = (
        "id",
        "name",
        "color",
        "slug",
    )
    list_filter = ("color",)
    list_editable = (
        "name",
        "color",
        "slug",
    )
    search_fields = ("name",)
    ordering = ("id",)
    empty_value_display = EMPTY_VALUE_DISPLAY


@admin.register(Recipe)
class RecipeClass(admin.ModelAdmin):
    """Админка рецептов."""

    list_display = (
        "name",
        "text",
        "image",
        "cooking_time",
        "author",
        "_get_adding_to_favourite",
    )
    list_filter = (
        "author",
        "name",
        "tags",
    )
    ordering = ("-id",)
    search_fields = ("name",)
    empty_value_display = EMPTY_VALUE_DISPLAY


@admin.register(IngredientRecipe)
class IngredientRecipeClass(admin.ModelAdmin):
    """Админка ингредиентов рецепта."""

    list_display = (
        "id",
        "ingredient",
        "recipe",
        "amount",
    )
    list_filter = (
        "ingredient",
        "recipe",
        "amount",
    )
    ordering = ("-recipe",)
    empty_value_display = EMPTY_VALUE_DISPLAY


@admin.register(Follow)
class FollowClass(admin.ModelAdmin):
    """Админка подписок на авторов."""

    list_display = (
        "id",
        "user",
        "author",
    )
    list_filter = (
        "user",
        "author",
    )
    ordering = ("-id",)
    empty_value_display = EMPTY_VALUE_DISPLAY


@admin.register(Favorite)
class FavoriteClass(admin.ModelAdmin):
    """Админка избранных рецептов."""

    list_display = (
        "id",
        "user",
        "recipe",
    )
    list_filter = (
        "user",
        "id",
    )
    ordering = ("-id",)
    empty_value_display = EMPTY_VALUE_DISPLAY


@admin.register(ShoppingCart)
class ShoppingCartClass(admin.ModelAdmin):
    """Админка списка покупок."""

    list_display = (
        "id",
        "user",
        "recipe",
    )
    list_filter = ("user", "recipe")
    ordering = ("-id",)
    empty_value_display = EMPTY_VALUE_DISPLAY
