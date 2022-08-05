from djoser.views import UserViewSet
from rest_framework.viewsets import ModelViewSet

from users.models import User

from .serializers import CustomUserSerializer, RecipeSerializer


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer


class RecipeViewSet(ModelViewSet):
    """Рецепты."""

    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        """Создает рецепт."""
        serializer.save(
            author=self.request.user,
        )
