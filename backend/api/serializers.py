from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from rest_framework.relations import SlugRelatedField
from django.shortcuts import get_object_or_404

from recipes.models import (
    Recipe,
    Tag,
    Ingredient,
    IngredientRecipe,
    ShoppingCart,
    Favorite,
    Follow,
)
from users.models import User


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    measurement_unit = serializers.CharField()
    id = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = (
            "name",
            "id",
            "measurement_unit",
        )


# class IngredientListSerializer(serializers.ModelSerializer):
#     name = serializers.CharField(source='ingredient.name')
#     id = serializers.IntegerField(source='ingredient.id')
#     measurement_unit = serializers.IntegerField(source='ingredient.id')


#     class Meta:
#         model = Ingredient
#         fields = (
#             "name",
#             "id",
#             "measurement_unit",
#         )


class IngredientRecipeSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField()
    id = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = "__all__"
        read_only_fields = ("ingredient", "recipe")


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )


class CustomUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
        )


class RecipeRepresentationSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer()
    ingredients = IngredientRecipeSerializer(many=True, source="ingredient_recipe")

    class Meta:
        model = Recipe
        fields = (
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
            "author",
        )
        depth = 1


class CartRepresentationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )
        depth = 1


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    image = Base64ImageField(max_length=None, use_url=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    ingredients = IngredientRecipeSerializer(many=True)

    class Meta:
        model = Recipe
        fields = "__all__"

    def create(self, validated_data):
        recipe_tags = validated_data.pop("tags")
        recipe_ingredients = validated_data.pop("ingredients")
        try:
            new_recipe = Recipe.objects.create(**validated_data)
            new_recipe.tags.set(recipe_tags)
        except Exception as error:
            raise serializers.ValidationError({"detail": error})
        for ingredient in recipe_ingredients:
            try:
                IngredientRecipe.objects.create(
                    recipe=new_recipe,
                    amount=ingredient["amount"],
                    ingredient_id=ingredient["id"],
                )
            except Exception as error:
                raise serializers.ValidationError({"detail": ingredient})
        return new_recipe

    def to_representation(self, instance):
        try:
            representation = RecipeRepresentationSerializer(instance)
        except Exception as error:
            raise serializers.ValidationError({"detail": error})

        return representation.data


class ShowRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class ShoppingcartSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = ShoppingCart
        fields = "__all__"
        read_only_fields = ("recipe",)
        depth = 1

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return ShowRecipeSerializer(instance.recipe, context=context).data


class ShoppingListSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = ShoppingCart
        fields = "__all__"
        read_only_fields = ("recipe",)
        depth = 1


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = Favorite
        fields = "__all__"
        read_only_fields = ("recipe",)
        depth = 1

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return ShowRecipeSerializer(instance.recipe, context=context).data


class UserRepresentationSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(method_name="get_is_subscribed")
    recipes = serializers.SerializerMethodField(method_name="get_recipes")
    recipes_count = serializers.SerializerMethodField(method_name="get_recipes_count")

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )
        depth = 1

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user.id
        if Follow.objects.filter(user=user, author=obj).exists():
            return True

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj)
        return ShowRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Follow
        fields = "__all__"
        # depth = 1

    def create(self, validated_data):
        try:
            following = Follow.objects.create(**validated_data)
        except Exception as error:
            raise serializers.ValidationError({"detail": error})
        return following

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return UserRepresentationSerializer(instance.author, context=context).data
