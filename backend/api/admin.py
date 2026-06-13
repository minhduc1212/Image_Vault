"""
Django admin registrations for Image Vault models.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Vault, Photo, Comment


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin panel for the custom User model."""

    # Columns shown in the list view
    list_display = ('email', 'name', 'initials', 'is_staff', 'is_active', 'created_at')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'name')
    ordering = ('email',)

    # Remove username-based fieldsets, replace with email-centric ones
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'initials', 'avatar')}),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions',
            )
        }),
        ('Important dates', {'fields': ('last_login', 'created_at')}),
    )
    readonly_fields = ('initials', 'created_at')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2'),
        }),
    )


# ---------------------------------------------------------------------------
# Vault
# ---------------------------------------------------------------------------

@admin.register(Vault)
class VaultAdmin(admin.ModelAdmin):
    list_display = ('name', 'emoji', 'owner', 'invite_code', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'owner__email', 'invite_code')
    readonly_fields = ('id', 'invite_code', 'created_at')
    filter_horizontal = ('members',)


# ---------------------------------------------------------------------------
# Photo
# ---------------------------------------------------------------------------

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'vault', 'uploader', 'caption', 'posted_at')
    list_filter = ('posted_at', 'vault')
    search_fields = ('caption', 'uploader__email', 'vault__name')
    readonly_fields = ('id', 'posted_at')


# ---------------------------------------------------------------------------
# Comment
# ---------------------------------------------------------------------------

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'photo', 'author', 'text', 'posted_at')
    list_filter = ('posted_at',)
    search_fields = ('text', 'author__email')
    readonly_fields = ('id', 'posted_at')
