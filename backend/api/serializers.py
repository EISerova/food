from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from foodgram.settings import (
    DOUBLE_INGREDIENT_ADD_ERROR,
    DOUBLE_TAGS_ADD_ERROR,
    RECIPE_FIELD_RESPONSE,
    USER_FIELD_RESPONSE,
)
from recipes.models import (
    Favorite,
    Follow,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)
from rest_framework import serializers
from users.models import User


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для модели User (регистрация)."""

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = USER_FIELD_RESPONSE + ("password",)


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = USER_FIELD_RESPONSE + ("is_subscribed",)

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user.id
        return Follow.objects.filter(user=user, author=obj).exists()


class BaseRecipeSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для модели Recipe."""

    class Meta:
        model = Recipe
        fields = RECIPE_FIELD_RESPONSE + ("id",)


class FollowRepresentationSerializer(CustomUserSerializer):
    recipes = BaseRecipeSerializer(many=True)
    recipes_count = serializers.SerializerMethodField(
        method_name="get_recipes_count"
    )

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    class Meta:
        model = User
        fields = USER_FIELD_RESPONSE + (
            "is_subscribed",
            "recipes",
            "recipes_count",
        )
        depth = 2


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор подписок."""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Follow
        fields = "__all__"

    def to_representation(self, instance):
        context = {"request": self.context.get("request")}
        return FollowRepresentationSerializer(
            instance.author, context=context
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранного."""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = Favorite
        fields = "__all__"
        read_only_fields = ("recipe",)

    def to_representation(self, instance):
        context = {"request": self.context.get("request")}
        return BaseRecipeSerializer(instance.recipe, context=context).data


class ShoppingcartSerializer(serializers.ModelSerializer):
    """Сериализатор списка покупок."""

    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = ShoppingCart
        fields = "__all__"
        read_only_fields = ("recipe",)

    def to_representation(self, instance):
        context = {"request": self.context.get("request")}
        return BaseRecipeSerializer(instance.recipe, context=context).data


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели IngredientRecipe."""

    id = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ("id", "amount")


class IdIngredientRecipeSerializer(IngredientRecipeSerializer):
    """Сериализатор id ингедиента."""

    id = serializers.IntegerField(source="ingredient.id", required=False)


class RepresentationRecipeCreateSerializer(serializers.ModelSerializer):
    """Выводит поля для сериализатора RecipeCreateSeializer."""

    ingredients = IdIngredientRecipeSerializer(
        many=True, required=True, source="ingredient_recipe"
    )

    class Meta:
        model = Recipe
        fields = RECIPE_FIELD_RESPONSE + (
            "ingredients",
            "tags",
            "text",
        )


class RecipeCreateSeializer(serializers.ModelSerializer):
    """Сериализатор создания рецепта."""

    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    image = Base64ImageField(max_length=None, use_url=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = IngredientRecipeSerializer(many=True)

    class Meta:
        model = Recipe
        fields = RECIPE_FIELD_RESPONSE + (
            "ingredients",
            "tags",
            "text",
            "author",
        )

    def validate_tags(self, value):
        removing_double = set(value)
        if len(value) > len(removing_double):
            raise serializers.ValidationError(
                {"detail": DOUBLE_TAGS_ADD_ERROR}
            )
        return value

    def validate(self, data):
        ingredients_ids = set()
        for ingredient in data["ingredients"]:
            ingredients_ids.add(ingredient["id"])
        if len(data["ingredients"]) > len(ingredients_ids):
            raise serializers.ValidationError(
                {"detail": DOUBLE_INGREDIENT_ADD_ERROR}
            )
        return data

    def create_recipe_ingredients(self, new_recipe, recipe_ingredients):
        IngredientRecipe.objects.bulk_create(
            IngredientRecipe(
                recipe=new_recipe,
                amount=ingredient["amount"],
                ingredient_id=ingredient["id"],
            )
            for ingredient in recipe_ingredients
        )

    def create(self, validated_data):
        recipe_tags = validated_data.pop("tags")
        recipe_ingredients = validated_data.pop("ingredients")
        new_recipe = Recipe.objects.create(**validated_data)
        new_recipe.tags.set(recipe_tags)
        self.create_recipe_ingredients(new_recipe, recipe_ingredients)
        return new_recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get("image", instance.image)
        instance.name = validated_data.get("name", instance.name)
        instance.cooking_time = validated_data.get(
            "cooking_time", instance.cooking_time
        )
        instance.tags.set(validated_data["tags"])
        prev_ingredients = IngredientRecipe.objects.filter(recipe=instance.id)
        prev_ingredients.delete()
        ingredients = validated_data.pop("ingredients")
        for ingredient in ingredients:
            IngredientRecipe.objects.get_or_create(
                ingredient=get_object_or_404(Ingredient, id=ingredient["id"]),
                amount=ingredient["amount"],
                recipe=instance,
            )
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = RepresentationRecipeCreateSerializer(
            instance, context={"request": self.context.get("request")}
        )
        return representation.data


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента."""

    name = serializers.CharField()
    measurement_unit = serializers.CharField()
    id = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit",
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тэга."""

    class Meta:
        model = Tag
        fields = "__all__"


class IngredientForRecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента для RecipeListSerializer."""

    id = serializers.IntegerField(source="ingredient.id")
    name = serializers.CharField(source="ingredient.name")
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = IngredientRecipe
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор списка рецептов."""

    author = CustomUserSerializer()
    ingredients = IngredientForRecipeListSerializer(
        many=True, source="ingredient_recipe"
    )
    is_favorited = serializers.SerializerMethodField(
        method_name="get_is_favorited"
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name="get_is_in_shopping_cart"
    )
    tags = TagSerializer(many=True)

    class Meta:
        model = Recipe
        fields = RECIPE_FIELD_RESPONSE + (
            "author",
            "id",
            "is_favorited",
            "is_in_shopping_cart",
            "ingredients",
            "tags",
        )
        depth = 1

    def get_is_favorited(self, obj):
        user = self.context.get("request").user.id
        return Favorite.objects.filter(user=user, recipe=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get("request").user.id
        return ShoppingCart.objects.filter(user=user, recipe=obj.id).exists()
