from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    # ✅ Показываем в списке
    list_display = ("email", "username", "is_staff", "is_blocked")
    list_filter = ("is_staff", "is_blocked", "is_superuser")
    search_fields = ("email", "username")
    ordering = ("email",)

    # ✅ Добавляем поле is_blocked в форму редактирования
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("avatar", "phone", "country", "is_blocked")}),
    )

    # ✅ Добавляем поле is_blocked в форму создания
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("avatar", "phone", "country", "is_blocked")}),
    )
