from django.contrib import admin

from users.models import User


@admin.register(User)
class UserClass(admin.ModelAdmin):
    """Админка юзеров."""

    list_display = (
        'id',
        'password',
        'last_login',
        'is_superuser',
        'username',
        'first_name',
        'last_name',
        'is_staff',
        'is_active',
        'email',
        'create_at',
        'confirmation_code',
    )
    list_filter = (
        'is_active',
        'last_login',
        'create_at',
    )
    list_editable = (
        'password',
        'username',
        'first_name',
        'last_name',
        'is_staff',
        'email',
    )
    search_fields = (
        'id',
        'username',
        'email',
    )
    ordering = ('-create_at',)
    empty_value_display = '-пусто-'

