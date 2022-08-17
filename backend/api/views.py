from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite, Follow, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag)
from rest_framework import (authentication, filters, mixins, permissions,
                            status, viewsets)
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from users.models import User

from .filter import RecipeListFilter
from .serializers import (CustomUserSerializer, FavoriteSerializer,
                          FollowSerializer, IngredientSerializer,
                          RecipeCreateSeializer, RecipeListSerializer,
                          ShoppingcartSerializer, TagSerializer)
from .utils import generate_pdf


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(methods=["POST", "DELETE"], detail=True)
    def subscribe(self, request, id):

        if self.request.method == "POST":
            try:
                author = User.objects.get(id=id)
                data = {"user": request.user.id, "author": author.id}
                serializer = FollowSerializer(
                    data=data, context={"request": request}
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            except ObjectDoesNotExist:
                return Response(
                    "Пользователя с таким id нет.",
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if self.request.method == "DELETE":
            try:
                following = Follow.objects.get(user=request.user, author=id)
                following.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ObjectDoesNotExist:
                return Response(
                    "Вы не подписаны на этого пользователя.",
                    status=status.HTTP_400_BAD_REQUEST,
                )

    @action(methods=["GET"], url_path="subscriptions", detail=False)
    def subscriptions(self, request):
        user = request.user
        data = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(data)
        serializer = CustomUserSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)


class RecipeViewSet(ModelViewSet):
    """Рецепты."""

    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeListFilter
    filterset_fields = ["author", "tags"]

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
            .annotate(amount=Sum("amount"))
        )
        return generate_pdf(ingredients_in_cart)

    @action(
        detail=True,
        methods=("POST", "DELETE"),
        url_path="shopping_cart",
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        user = request.user.id
        data = {"user": user, "recipe": pk}
        serializer = ShoppingcartSerializer(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        if self.request.method == "POST":
            if ShoppingCart.objects.filter(user=user, recipe=pk).exists():
                return Response(
                    "Этот рецепт уже добавлен в список покупок.",
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == "DELETE":
            try:
                shopping_cart = ShoppingCart.objects.get(user=user, recipe=pk)
                shopping_cart.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ObjectDoesNotExist:
                return Response(
                    "Этого рецепта нет в вашем списке покупок",
                    status=status.HTTP_400_BAD_REQUEST,
                )

    @action(
        detail=True,
        methods=("POST", "DELETE"),
        url_path="favorite",
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        user = request.user.id
        data = {"user": user, "recipe": pk}
        serializer = FavoriteSerializer(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        if self.request.method == "POST":
            if Favorite.objects.filter(user=user, recipe=pk).exists():
                return Response(
                    "Этот рецепт уже добавлен в избранное.",
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == "DELETE":
            try:
                favorite_pecipe = Favorite.objects.get(user=user, recipe=pk)
                favorite_pecipe.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ObjectDoesNotExist:
                return Response(
                    "Этот рецепт не добавлен в избранное.",
                    status=status.HTTP_400_BAD_REQUEST,
                )


class FavoriteViewSet(ModelViewSet):
    """Избранное."""

    serializer_class = FavoriteSerializer

    def get_queryset(self):
        user = self.request.user
        return Favorite.objects.filter(user=user)


###########################ГОТОВО###############################


class IngredientViewSet(ReadOnlyModelViewSet):
    """Ингредиенты."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["^name"]
    permission_classes = (AllowAny,)
    pagination_class = None


class TagViewSet(ModelViewSet):
    """Тэги."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
