from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from recipes.models import Recipe
from users.models import User


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ("email", "id", "username", "first_name", "last_name", "password")


class CustomUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ("email", "id", "username", "first_name", "last_name")


class RecipeSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "ingredients",
            "id",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
            "author",
        )
