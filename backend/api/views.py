from djoser.views import UserViewSet
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework import viewsets, mixins, permissions, authentication
from rest_framework import status, viewsets
from django.db.models import Sum

from users.models import User
from recipes.models import (
    Tag,
    Recipe,
    Ingredient,
    IngredientRecipe,
    ShoppingCart,
    Favorite,
    Follow,
)

from .serializers import (
    CustomUserSerializer,
    RecipeSerializer,
    TagSerializer,
    IngredientSerializer,
    IngredientRecipeSerializer,
    ShoppingcartSerializer,
    ShoppingListSerializer,
    FavoriteSerializer,
    FollowSerializer,
    UserRepresentationSerializer,
)
from .utils import generate_pdf
from rest_framework import filters


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(methods=["POST", "DELETE"], detail=True)
    def subscribe(self, request, id):

        if self.request.method == "POST":
            author = get_object_or_404(User, id=id)
            data = {"user": request.user.id, "author": author.id}
            serializer = FollowSerializer(data=data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == "DELETE":
            following = get_object_or_404(Follow, user=request.user, author=id)
            following.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["GET"], detail=False)
    def subscriptions(self, request):
        user = request.user
        data = User.objects.filter(following__user=user)
        serializer = UserRepresentationSerializer(
            data, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RecipeViewSet(ModelViewSet):
    """Рецепты."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        """Создает рецепт."""
        serializer.save(
            author=self.request.user,
        )

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
        data = {"user": request.user.id, "recipe": pk}
        serializer = ShoppingcartSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        if self.request.method == "POST":
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == "DELETE":
            shopping_cart = get_object_or_404(
                ShoppingCart, user=request.user, recipe_id=pk
            )
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=("POST", "DELETE"),
        url_path="favorite",
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        data = {"user": request.user.id, "recipe": pk}
        serializer = FavoriteSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        if self.request.method == "POST":
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == "DELETE":
            favorite_pecipe = get_object_or_404(
                Favorite, user=request.user, recipe_id=pk
            )
            favorite_pecipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(ModelViewSet):
    """Тэги."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    """Ингредиенты."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["^name"]


class FavoriteViewSet(ModelViewSet):
    """Избранное."""

    serializer_class = FavoriteSerializer

    def get_queryset(self):
        user = self.request.user
        return Favorite.objects.filter(user=user)
