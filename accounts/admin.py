from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.utils.html import format_html

User = get_user_model()

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Add our custom fields to the user edit page
    fieldsets = UserAdmin.fieldsets + (
        ("Profile", {"fields": ("nickname", "bio", "profile_picture", "privacy_mode", "profile_preview")}),
    )

    # Make the preview read‑only so it doesn't show up as an editable field
    readonly_fields = ("profile_preview",)

    # Add useful columns to the user list page
    list_display = ("username", "email", "nickname", "privacy_mode", "profile_thumb", "is_staff")

    def profile_thumb(self, obj):
        """Small thumbnail for the user list page."""
        if obj.profile_picture:
            return format_html(
                '<img src="{}" style="width:40px; height:40px; border-radius:50%;" />',
                obj.profile_picture.url
            )
        return "—"
    profile_thumb.short_description = "Photo"

    def profile_preview(self, obj):
        """Larger preview on the user edit page."""
        if obj.profile_picture:
            return format_html(
                '<img src="{}" style="width:150px; height:150px; border-radius:8px; object-fit:cover;" />',
                obj.profile_picture.url
            )
        return "No image uploaded"
    profile_preview.short_description = "Current Profile Picture"
