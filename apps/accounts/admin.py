# apps/accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, PasswordResetToken, UserActivity


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ["email", "name", "is_active", "is_staff", "created_at"]
    search_fields = ["email", "name"]
    ordering      = ["-created_at"]
    fieldsets     = BaseUserAdmin.fieldsets + (
        ("Profile", {"fields": ("name", "avatar_url")}),
    )


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display  = ["user", "token", "created_at", "expires_at", "used"]
    list_filter   = ["used"]
    search_fields = ["user__email"]
    readonly_fields = ["token", "created_at"]


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display  = ["user", "date", "login_count", "access_count", "duration_seconds"]
    list_filter   = ["date"]
    search_fields = ["user__email"]
    ordering      = ["-date"]
