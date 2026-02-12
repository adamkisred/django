from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from accounts.models import User, EmailOTP


# =========================================================
# CUSTOM USER ADMIN
# =========================================================
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("id",)
    list_display = (
        "id",
        "email",
        "username",
        "role",
        "is_active",
        "is_staff",
        "created_at",
    )
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("email", "username")

    fieldsets = (
        ("Basic Info", {
            "fields": (
                "email",
                "username",
                "password",
            )
        }),
        ("Role & Permissions", {
            "fields": (
                "role",
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Important Dates", {
            "fields": (
                "last_login",
                "created_at",
            )
        }),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "role",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )

    readonly_fields = ("created_at",)

    filter_horizontal = ("groups", "user_permissions")


# =========================================================
# EMAIL OTP ADMIN
# =========================================================
@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "otp",
        "is_used",
        "created_at",
    )
    list_filter = ("is_used", "created_at")
    search_fields = ("email", "otp")
    readonly_fields = ("otp", "created_at")
