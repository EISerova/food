from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from foodgram.settings import (
    RECIPE_ADD_IN_CART_ERROR,
    RECIPE_ADD_IN_FAVORITE_ERROR,
    RECIPE_DELETE_FROM_CART_ERROR,
    RECIPE_DELETE_FROM_FAVORITE_ERROR,
    SUBSCRIBING_NOT_EXIST_ERROR,
    USER_NOT_EXIST_ERROR,
    DELETE_FOLLOWING_MESSAGE,
)
from .filter import RecipeListFilter
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
            try:
                following = Follow.objects.get(user=request.user, author=id)
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
        serializer.is_valid(raise_exception=True)
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

    def base_shopping_cart_favorite(
        self,
        request,
        pk,
        model,
        model_serializer,
        error_text_create,
        error_text_delete,
    ):
        """базовый метод для shopping_cart и favorite."""
        user = request.user.id
        data = {"user": user, "recipe": pk}
        serializer = model_serializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        obj = model.objects.get(user=user, recipe=pk)

        if request.method == "GET":
            if obj:
                data = {"errors": error_text_create}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == "DELETE":
            if not obj:
                data = {"errors": error_text_delete}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=("POST", "DELETE"),
        url_path="shopping_cart",
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        return self.base_shopping_cart_favorite(
            request,
            pk,
            model=ShoppingCart,
            model_serializer=ShoppingcartSerializer,
            error_text_create=RECIPE_ADD_IN_CART_ERROR,
            error_text_delete=RECIPE_DELETE_FROM_CART_ERROR,
        )

    @action(
        detail=True,
        methods=("POST", "DELETE"),
        url_path="favorite",
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        return self.base_shopping_cart_favorite(
            request,
            pk,
            model=Favorite,
            model_serializer=FavoriteSerializer,
            error_text_create=RECIPE_ADD_IN_FAVORITE_ERROR,
            error_text_delete=RECIPE_DELETE_FROM_FAVORITE_ERROR,
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
