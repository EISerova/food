from django.core.exceptions import ImproperlyConfigured

import os
from dotenv import load_dotenv
from pathlib import Path


load_dotenv()


def get_env_value(env_variable):
    try:
        return os.getenv[env_variable]
    except KeyError:
        error_msg = "Установите переменную окружения {}".format(env_variable)
        raise ImproperlyConfigured(error_msg)


SECRET_KEY = os.getenv("SECRET_KEY")

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = True

ALLOWED_HOSTS = ["*"]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 3rd Party Apps
    "drf_yasg",
    "rest_framework",
    "rest_framework.authtoken",
    "djoser",
    "django_filters",
    # My Apps
    "users",
    "api",
    "recipes",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "foodgram.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "foodgram.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": os.getenv(
            "DB_ENGINE", default="django.db.backends.postgresql"
        ),
        "NAME": "postgresa",
        "USER": "postgresa",
        "PASSWORD": "12345",
        "HOST": "db",
        "PORT": 5432,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "users.User"


LANGUAGE_CODE = "ru-RU"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = "/static/"

STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


DJOSER = {
    "HIDE_USERS": False,
    "LOGIN_FIELD": "email",
    "SERIALIZERS": {
        "user": "api.serializers.CustomUserSerializer",
        "user_create": "api.serializers.CustomUserCreateSerializer",
        "current_user": "api.serializers.CustomUserSerializer",
    },
    "PERMISSIONS": {
        "user_list": ("rest_framework.permissions.AllowAny",),
        "user": ("rest_framework.permissions.IsAuthenticated",),
    },
}


REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.AllowAny",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 6,
}


# Кастомные переменные

MIN_COOKING_TIME = 1
USER_FIELD_RESPONSE = (
    "email",
    "id",
    "username",
    "first_name",
    "last_name",
)

RECIPE_FIELD_RESPONSE = (
    "name",
    "image",
    "cooking_time",
)

USER_NOT_EXIST_ERROR = "Пользователь не существует."
TAG_SLUG_LENGTH_ERROR = (
    "Разрешены латинские буквы и цифры. Не более 200 символов"
)
SUBSCRIBING_NOT_EXIST_ERROR = "Вы не подписаны на этого пользователя."
RECIPE_ADD_IN_CART_ERROR = "Этот рецепт уже добавлен в список покупок."
RECIPE_DELETE_FROM_CART_ERROR = "Этого рецепта нет в вашем списке покупок."
RECIPE_ADD_IN_FAVORITE_ERROR = "Этот рецепт уже добавлен в избранное."
RECIPE_DELETE_FROM_FAVORITE_ERROR = "Этот рецепт не добавлен в избранное."
DOUBLE_INGREDIENT_ADD_ERROR = "Вы добавили два одинаковых ингредиента."
DOUBLE_TAGS_ADD_ERROR = "Вы добавили два одинаковых тега."
DELETE_FOLLOWING_MESSAGE = "Вы отписались от пользователя {author}."
