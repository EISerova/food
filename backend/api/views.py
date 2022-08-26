from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from foodgram.settings import (
    SUBSCRIBING_NOT_EXIST_ERROR,
    USER_NOT_EXIST_ERROR,
    DELETE_FOLLOWING_MESSAGE,
)
from .filter import RecipeListFilter, IngredientSearchFilter
from .permissions import IsAuthorOrReadOnly
from recipes.models import (
    Favorite,
    Follow,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)
from .serializers import (
    CustomUserSerializer,
    FavoriteSerializer,
    FollowRepresentationSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipeCreateSeializer,
    RecipeListSerializer,
    ShoppingcartSerializer,
    TagSerializer,
    BaseRecipeSerializer,
)
from users.models import User
from .utils import generate_pdf


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(methods=["POST", "DELETE"], detail=True)
    def subscribe(self, request, id):

        if self.request.method == "POST":
            try:
                author = User.objects.get(id=id)
            except User.DoesNotExist:
                return Response(
                    USER_NOT_EXIST_ERROR,
                    status=status.HTTP_400_BAD_REQUEST,
                )
            data = {"user": request.user.id, "author": author.id}
            serializer = FollowSerializer(
                data=data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == "DELETE":
            author = User.objects.get(id=id)
            try:
                following = Follow.objects.get(
                    user=request.user, author=author
                )
            except Follow.DoesNotExist:
                return Response(
                    SUBSCRIBING_NOT_EXIST_ERROR,
                    status=status.HTTP_400_BAD_REQUEST,
                )
            following.delete()
            return Response(
                DELETE_FOLLOWING_MESSAGE.format(author=author),
                status=status.HTTP_204_NO_CONTENT,
            )

    @action(methods=["GET"], url_path="subscriptions", detail=False)
    def subscriptions(self, request):
        data = User.objects.filter(following__user=request.user)
        pages = self.paginate_queryset(data)
        serializer = FollowRepresentationSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)


class RecipeViewSet(ModelViewSet):
    """Рецепты."""

    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeListFilter
    filterset_fields = ["author", "tags"]
    permission_classes = (IsAuthorOrReadOnly,)

    def perform_create(self, serializer):
        """Создает рецепт."""
        serializer.save(
            author=self.request.user,
        )

    def get_serializer_class(self):
        if self.request.method in ("POST", "PATCH", "DELETE"):
            return RecipeCreateSeializer
        return RecipeListSerializer

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        ingredients_in_cart = (
            IngredientRecipe.objects.filter(recipe__cart__user=request.user)
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(ingredient_amount=Sum("amount"))
        )
        return generate_pdf(ingredients_in_cart)

    def base_shopping_cart_favorite(self, model, pk, serializer):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = serializer(
            data={"user": self.request.user.id, "recipe": recipe.id},
            context={"request": self.request},
        )
        if self.request.method == "POST":
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = BaseRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        object = model.objects.filter(user=self.request.user, recipe=recipe)
        if not object.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=("POST", "DELETE"),
        url_path="favorite",
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        return self.base_shopping_cart_favorite(
            Favorite, pk, FavoriteSerializer
        )

    @action(
        detail=True,
        methods=("POST", "DELETE"),
        url_path="shopping_cart",
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        return self.base_shopping_cart_favorite(
            ShoppingCart, pk, ShoppingcartSerializer
        )


class FavoriteViewSet(ModelViewSet):
    """Избранное."""

    serializer_class = FavoriteSerializer

    def get_queryset(self):
        user = self.request.user
        return Favorite.objects.filter(user=user)


class IngredientViewSet(ReadOnlyModelViewSet):
    """Ингредиенты."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [IngredientSearchFilter]
    search_fields = ["^name"]
    permission_classes = (AllowAny,)
    pagination_class = None


class TagViewSet(ModelViewSet):
    """Тэги."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
