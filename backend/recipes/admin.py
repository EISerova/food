from django.contrib import admin

from users.models import User

from .models import Ingredient, Tag, Recipe


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
    empty_value_display = "-пусто-"


@admin.register(Ingredient)
class IngredientClass(admin.ModelAdmin):
    """Админка юзеров."""

    list_display = (
        "id",
        "name",
        "measurement_unit",
    )
    list_filter = ("measurement_unit",)
    list_editable = (
        "name",
        "measurement_unit",
    )
    search_fields = (
        "id",
        "name",
        "measurement_unit",
    )
    ordering = ("-id",)
    empty_value_display = "-пусто-"


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
    search_fields = (
        "id",
        "name",
        "slug",
    )
    ordering = ("-id",)
    empty_value_display = "-пусто-"


@admin.register(Recipe)
class RecipeClass(admin.ModelAdmin):
    """Админка рецептов."""

    list_display = (
        "name",
        "text",
        "image",
        "cooking_time",
        "author",
        # "ingredient",
        # "tag",
    )
    list_filter = ("author", "name")
    ordering = ("-id",)
    empty_value_display = "-пусто-"
