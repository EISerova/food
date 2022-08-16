from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from foodgram.settings import USER_FIELD_RESPONSE, RECIPE_FIELD_RESPONSE
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

############################# ЮЗЕРЫ #########################


class CustomUserCreateSerializer(UserCreateSerializer):
    "Сериализатор для модели User (регистрация)."

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = USER_FIELD_RESPONSE + ("password",)


class CustomUserSerializer(serializers.ModelSerializer):
    "Сериализатор для модели User."
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user.id
        return Follow.objects.filter(user=user, author=obj).exists()


############################# ПОДПИСКА #########################


class ShowRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class FollowRepresentationSerializer(serializers.ModelSerializer):
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
        return Follow.objects.filter(user=user, author=obj).exists()

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

    def create(self, validated_data):
        try:
            following = Follow.objects.create(**validated_data)
        except Exception as error:
            raise serializers.ValidationError({"detail": error})
        return following

    def to_representation(self, instance):
        context = {"request": self.context.get("request")}
        return FollowRepresentationSerializer(instance.author, context=context).data


############################# ИЗБРАННОЕ #########################


class RepForRecipeFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = Favorite
        fields = "__all__"
        read_only_fields = ("recipe",)

    def to_representation(self, instance):
        context = {"request": self.context.get("request")}
        return RepForRecipeFavoriteSerializer(instance.recipe, context=context).data


############################# СПИСОК ПОКУПОК #########################


class RepForRecipeShoppingcartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class ShoppingcartSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = ShoppingCart
        fields = "__all__"
        read_only_fields = ("recipe",)

    def to_representation(self, instance):
        context = {"request": self.context.get("request")}
        return RepForRecipeShoppingcartSerializer(instance.recipe, context=context).data


############### СОЗДАНИЕ РЕЦЕПТА ##############################


class IngredientShortSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField()
    id = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = (
            "id",
            "amount",
        )


class RepForRecipeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = RECIPE_FIELD_RESPONSE


class IngredientForRecipeCreateSerializer(IngredientShortSerializer):
    class Meta:
        model = IngredientRecipe
        fields = (
            "id",
            "amount",
            "ingredient",
            "recipe",
        )
        read_only_fields = (
            "ingredient",
            "recipe",
        )


class RecipeCreateSeializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    image = Base64ImageField(max_length=None, use_url=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    ingredients = IngredientForRecipeCreateSerializer(many=True)

    class Meta:
        model = Recipe
        fields = RECIPE_FIELD_RESPONSE + ("author",)

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
                raise serializers.ValidationError({"detail": error})
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
        try:
            representation = RepForRecipeCreateSerializer(
                instance, context=self.context
            )
        except Exception as error:
            raise serializers.ValidationError({"detail": error})

        return representation.data


############### ИНГРЕДИЕНТЫ, ТЭГИ ##############################


class IngredientSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = Tag
        fields = "__all__"


########################СПИСОК РЕЦЕПТОВ (LIST, GET)#################


class IngredientForRecipeCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="ingredient.id")
    name = serializers.CharField(source="ingredient.name")
    measurement_unit = serializers.CharField(source="ingredient.measurement_unit")

    class Meta:
        model = IngredientRecipe
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class RecipeListSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer()
    ingredients = IngredientForRecipeCreateSerializer(
        many=True, source="ingredient_recipe"
    )
    is_favorited = serializers.SerializerMethodField(method_name="get_is_favorited")
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name="get_is_in_shopping_cart"
    )

    class Meta:
        model = Recipe
        fields = RECIPE_FIELD_RESPONSE + (
            "author",
            "id",
            "is_favorited",
            "is_in_shopping_cart",
        )
        depth = 1

    def get_is_favorited(self, obj):
        user = self.context.get("request").user.id
        return Favorite.objects.filter(user=user, recipe=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get("request").user.id
        return ShoppingCart.objects.filter(user=user, recipe=obj.id).exists()


# class IngredientRecipeSerializer(IngredientShortSerializer):
#     class Meta:
#         model = IngredientRecipe
#         fields = (
#             "id",
#             "amount",
#             "ingredient",
#             "recipe",
#         )
#         read_only_fields = (
#             "ingredient",
#             "recipe",
#         )


# # class BaseUserSerializer(UserSerializer):
# #     class Meta:
# #         model = User
# #         fields = USER_FIELD_RESPONSE


# # class CustomUserSerializer(serializers.ModelSerializer):
# #     is_subscribed = serializers.SerializerMethodField()
# #     # get_recipes = serializers.SerializerMethodField("get_recipes")
# #     # recipes_count = serializers.SerializerMethodField("get_recipes_count")

# #     class Meta:
# #         model = User
# #         fields = (
# #             "email",
# #             "id",
# #             "username",
# #             "first_name",
# #             "last_name",
# #             "is_subscribed",
# #             # "get_recipes",
# #             # "recipes_count",
# #         )

# #     def get_is_subscribed(self, obj):
# #         user = self.context.get("request").user.id
# #         return Follow.objects.filter(user=user, author=obj).exists()


# # def get_recipes(self, obj):
# #     recipes = Recipe.objects.filter(author=obj)
# #     return RecipeListSerializer(recipes, many=True).data

# # def get_recipes_count(self, obj):
# #     return Recipe.objects.filter(author=obj).count()


# class RecipeCreateRepresentationSerializer(serializers.ModelSerializer):
#     ingredients = IngredientShortSerializer(many=True, source="ingredient_recipe")

#     class Meta:
#         model = Recipe
#         fields = RECIPE_FIELD_RESPONSE


# class RecipeSerializer(serializers.ModelSerializer):
#     author = serializers.HiddenField(default=serializers.CurrentUserDefault())
#     image = Base64ImageField(max_length=None, use_url=True)
#     tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
#     ingredients = IngredientRecipeSerializer(many=True)

#     class Meta:
#         model = Recipe
#         fields = RECIPE_FIELD_RESPONSE + ("author",)

#     # def create(self, validated_data):
#     #     recipe_tags = validated_data.pop("tags")
#     #     recipe_ingredients = validated_data.pop("ingredients")
#     #     try:
#     #         new_recipe = Recipe.objects.create(**validated_data)
#     #         new_recipe.tags.set(recipe_tags)
#     #     except Exception as error:
#     #         raise serializers.ValidationError({"detail": error})
#     #     for ingredient in recipe_ingredients:
#     #         try:
#     #             IngredientRecipe.objects.create(
#     #                 recipe=new_recipe,
#     #                 amount=ingredient["amount"],
#     #                 ingredient_id=ingredient["id"],
#     #             )
#     #         except Exception as error:
#     #             raise serializers.ValidationError({"detail": error})
#     #     return new_recipe

#     # def update(self, instance, validated_data):
#     #     instance.image = validated_data.get("image", instance.image)
#     #     instance.name = validated_data.get("name", instance.name)
#     #     instance.cooking_time = validated_data.get(
#     #         "cooking_time", instance.cooking_time
#     #     )
#     #     instance.tags.set(validated_data["tags"])
#     #     prev_ingredients = IngredientRecipe.objects.filter(recipe=instance.id)
#     #     prev_ingredients.delete()
#     #     # recipe_ingredients = validated_data["ingredients"]
#     #     # for ingredient in recipe_ingredients:
#     #     # IngredientRecipe.objects.create(
#     #     #     recipe=instance,
#     #     #     amount=recipe_ingredients["amount"],
#     #     #     ingredient_id=recipe_ingredients["id"],
#     #     # )
#     #     # instance.save()
#     #     return instance

#     def to_representation(self, instance):
#         # if self.context["request"].method == "GET":
#         #     serializer = RecipeListSerializer(instance, context=self.context)
#         #     return serializer.data
#         # if self.context["request"].method == "POST":
#         #     serializer = RecipeCreateRepresentationSerializer(
#         #         instance, context=self.context
#         #     )
#         #     return serializer.data
#         # return super().to_representation(instance)
#         try:
#             representation = RepForRecipeCreateSerializer(
#                 instance, context=self.context
#             )
#         except Exception as error:
#             raise serializers.ValidationError({"detail": error})

#         return representation.data


# # class FollowRepresentationSerializer(CustomUserSerializer):
# #     recipes = serializers.SerializerMethodField(method_name="get_recipes")
# #     recipes_count = serializers.SerializerMethodField(method_name="get_recipes_count")

# #     class Meta:
# #         depth = 1

# #     def get_recipes(self, obj):
# #         recipes = Recipe.objects.filter(author=obj)
# #         return RecipeListSerializer(recipes, many=True).data

# #     def get_recipes_count(self, obj):
# #         return Recipe.objects.filter(author=obj).count()
